"""
Recommender Service - ML-based book recommendations

Implemented:
- PopularityRecommender: rank by popularity_score
- ContentBasedRecommender: TF-IDF + cosine similarity on book text features

Planned:
- CollaborativeFilteringRecommender (matrix factorization)
- Deeper hybrid scoring
"""

from __future__ import annotations

import logging
import os
import pickle
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Set

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class BaseRecommender(ABC):
    """Base class for recommendation models"""

    @abstractmethod
    def train(self, data: Dict) -> None:
        """Train the model with user-book interaction data"""
        pass

    @abstractmethod
    def predict(self, user_id: int, book_ids: List[int]) -> List[float]:
        """Predict ratings/scores for a user on given books"""
        pass

    @abstractmethod
    def get_recommendations(self, user_id: int, n: int = 10) -> List[int]:
        """Get top N book recommendations for a user"""
        pass

    def save(self, path: str) -> None:
        """Save model to disk"""
        with open(path, 'wb') as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, path: str) -> 'BaseRecommender':
        """Load model from disk"""
        with open(path, 'rb') as f:
            return pickle.load(f)


class PopularityRecommender(BaseRecommender):
    """Simple popularity-based recommender."""

    def __init__(self):
        self.popular_books: List[int] = []

    def train(self, data: Dict) -> None:
        books = data.get('books', [])
        sorted_books = sorted(
            books, key=lambda x: x.get('popularity_score', 0), reverse=True
        )
        self.popular_books = [b['id'] for b in sorted_books]

    def predict(self, user_id: int, book_ids: List[int]) -> List[float]:
        scores = []
        for book_id in book_ids:
            if book_id in self.popular_books:
                rank = self.popular_books.index(book_id)
                scores.append(1.0 / (rank + 1))
            else:
                scores.append(0.0)
        return scores

    def get_recommendations(
        self,
        user_id: int,
        n: int = 10,
        exclude_ids: Optional[Set[int]] = None,
    ) -> List[int]:
        exclude = exclude_ids or set()
        results = [bid for bid in self.popular_books if bid not in exclude]
        return results[:n]


class ContentBasedRecommender(BaseRecommender):
    """
    Content-based recommender using TF-IDF on book text features
    and cosine similarity for ranking.
    """

    def __init__(self):
        self.book_ids: List[int] = []
        self._book_id_to_idx: Dict[int, int] = {}
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None
        self.user_interactions: Dict[int, List[tuple]] = {}
        self._trained = False

    @staticmethod
    def _build_document(book: Dict) -> str:
        parts = [
            book.get('title') or '',
            book.get('author') or '',
            book.get('genre') or '',
            book.get('category_name') or '',
            book.get('description') or '',
        ]
        return ' '.join(part for part in parts if part).strip()

    def train(self, data: Dict) -> None:
        books = data.get('books', [])
        if not books:
            self.book_ids = []
            self._book_id_to_idx = {}
            self.vectorizer = None
            self.tfidf_matrix = None
            self.user_interactions = {}
            self._trained = False
            logger.warning('ContentBasedRecommender.train() called with no books')
            return

        self.book_ids = [int(b['id']) for b in books]
        self._book_id_to_idx = {bid: i for i, bid in enumerate(self.book_ids)}
        documents = [self._build_document(b) for b in books]

        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=5000,
            ngram_range=(1, 2),
            min_df=1,
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(documents)

        self.user_interactions = {}
        for interaction in data.get('user_interactions', []):
            user_id = int(interaction['user_id'])
            book_id = int(interaction['book_id'])
            weight = float(interaction.get('weight', 1.0))
            self.user_interactions.setdefault(user_id, []).append((book_id, weight))

        self._trained = True
        logger.info(
            'ContentBasedRecommender trained on %s books (%s users with interactions)',
            len(self.book_ids),
            len(self.user_interactions),
        )

    def _rank_by_vector(
        self,
        query_vector,
        n: int,
        exclude_ids: Optional[Set[int]] = None,
    ) -> List[int]:
        if self.tfidf_matrix is None or query_vector is None:
            return []

        exclude = exclude_ids or set()
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        ranked_indices = np.argsort(similarities)[::-1]

        results: List[int] = []
        for idx in ranked_indices:
            book_id = self.book_ids[idx]
            if book_id in exclude:
                continue
            if similarities[idx] <= 0:
                continue
            results.append(book_id)
            if len(results) >= n:
                break
        return results

    def get_similar_books(
        self,
        book_id: int,
        n: int = 5,
        exclude_ids: Optional[Set[int]] = None,
    ) -> List[int]:
        if not self._trained or book_id not in self._book_id_to_idx:
            return []

        idx = self._book_id_to_idx[book_id]
        exclude = set(exclude_ids or set())
        exclude.add(book_id)
        return self._rank_by_vector(self.tfidf_matrix[idx], n, exclude)

    def recommend_for_query(
        self,
        query: str,
        n: int = 10,
        exclude_ids: Optional[Set[int]] = None,
    ) -> List[int]:
        if not self._trained or not query or self.vectorizer is None:
            return []

        query_vector = self.vectorizer.transform([query])
        return self._rank_by_vector(query_vector, n, exclude_ids)

    def _user_profile_vector(self, user_id: int):
        interactions = self.user_interactions.get(int(user_id), [])
        if not interactions or self.tfidf_matrix is None:
            return None

        vectors = []
        weights = []
        for book_id, weight in interactions:
            idx = self._book_id_to_idx.get(book_id)
            if idx is None:
                continue
            vectors.append(self.tfidf_matrix[idx])
            weights.append(max(weight, 0.0))

        if not vectors:
            return None

        stacked = np.vstack([v.toarray() for v in vectors])
        weight_arr = np.array(weights, dtype=float).reshape(-1, 1)
        if weight_arr.sum() == 0:
            return None

        profile = (stacked * weight_arr).sum(axis=0) / weight_arr.sum()
        return profile.reshape(1, -1)

    def predict(self, user_id: int, book_ids: List[int]) -> List[float]:
        profile = self._user_profile_vector(user_id)
        if profile is None or self.tfidf_matrix is None:
            return [0.0] * len(book_ids)

        scores = []
        for book_id in book_ids:
            idx = self._book_id_to_idx.get(int(book_id))
            if idx is None:
                scores.append(0.0)
            else:
                score = float(
                    cosine_similarity(profile, self.tfidf_matrix[idx]).flatten()[0]
                )
                scores.append(score)
        return scores

    def get_recommendations(
        self,
        user_id: int,
        n: int = 10,
        exclude_ids: Optional[Set[int]] = None,
    ) -> List[int]:
        profile = self._user_profile_vector(user_id)
        if profile is None:
            return []

        exclude = set(exclude_ids or set())
        for book_id, _ in self.user_interactions.get(int(user_id), []):
            exclude.add(book_id)

        return self._rank_by_vector(profile, n, exclude)


class CollaborativeFilteringRecommender(BaseRecommender):
    """
    Collaborative filtering recommender (placeholder for Phase 2).
    """

    def __init__(self):
        self.user_factors: Dict = {}
        self.item_factors: Dict = {}

    def train(self, data: Dict) -> None:
        logger.info('CollaborativeFilteringRecommender.train() - Not yet implemented')

    def predict(self, user_id: int, book_ids: List[int]) -> List[float]:
        return [0.5] * len(book_ids)

    def get_recommendations(self, user_id: int, n: int = 10) -> List[int]:
        return []


class RecommenderService:
    """
    Service for managing recommendation models.

    Usage:
        service = RecommenderService()
        service.initialize()
        service.train_all(books_data, ratings_data, user_interactions)
        recommendations = service.get_recommendations(user_id=1, n=10, algorithm='content')
    """

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or 'models/recommender'
        self.popularity_model: Optional[PopularityRecommender] = None
        self.content_model: Optional[ContentBasedRecommender] = None
        self.cf_model: Optional[CollaborativeFilteringRecommender] = None
        self.initialized = False

    def initialize(self, force_retrain: bool = False) -> None:
        os.makedirs(self.model_path, exist_ok=True)

        popularity_path = os.path.join(self.model_path, 'popularity.pkl')
        content_path = os.path.join(self.model_path, 'content.pkl')

        if not force_retrain and os.path.exists(popularity_path):
            try:
                self.popularity_model = PopularityRecommender.load(popularity_path)
                logger.info('Loaded popularity model from disk')
            except Exception as e:
                logger.warning('Failed to load popularity model: %s', e)
                self.popularity_model = PopularityRecommender()
        else:
            self.popularity_model = PopularityRecommender()

        if not force_retrain and os.path.exists(content_path):
            try:
                self.content_model = ContentBasedRecommender.load(content_path)
                logger.info('Loaded content-based model from disk')
            except Exception as e:
                logger.warning('Failed to load content model: %s', e)
                self.content_model = ContentBasedRecommender()
        else:
            self.content_model = ContentBasedRecommender()

        self.cf_model = CollaborativeFilteringRecommender()
        self.initialized = True

    @property
    def content_ready(self) -> bool:
        return bool(
            self.content_model
            and getattr(self.content_model, '_trained', False)
            and self.content_model.tfidf_matrix is not None
        )

    def train_all(
        self,
        books_data: List[Dict],
        ratings_data: Optional[List[Dict]] = None,
        user_interactions: Optional[List[Dict]] = None,
    ) -> None:
        if not self.initialized:
            self.initialize(force_retrain=True)

        ratings_data = ratings_data or []
        user_interactions = user_interactions or []

        self.popularity_model.train({'books': books_data})
        self.popularity_model.save(os.path.join(self.model_path, 'popularity.pkl'))

        self.content_model.train({
            'books': books_data,
            'user_interactions': user_interactions,
        })
        self.content_model.save(os.path.join(self.model_path, 'content.pkl'))

        self.cf_model.train({'ratings': ratings_data})

        logger.info('All recommender models trained successfully')

    def get_recommendations(
        self,
        user_id: Optional[int] = None,
        n: int = 10,
        algorithm: str = 'hybrid',
        exclude_ids: Optional[Set[int]] = None,
    ) -> List[int]:
        if not self.initialized:
            self.initialize()

        exclude = exclude_ids or set()

        if algorithm == 'popularity' or user_id is None:
            return self.popularity_model.get_recommendations(
                user_id or 0, n, exclude_ids=exclude
            )

        if algorithm == 'content':
            recs = self.content_model.get_recommendations(
                user_id, n, exclude_ids=exclude
            )
            if len(recs) < n:
                fill = self.popularity_model.get_recommendations(
                    user_id, n - len(recs), exclude_ids=exclude | set(recs)
                )
                recs.extend(fill)
            return recs

        if algorithm == 'collaborative':
            return self.cf_model.get_recommendations(user_id, n)

        # Hybrid: content first, popularity fill
        if self.content_ready and user_id is not None:
            recs = self.content_model.get_recommendations(
                user_id, n, exclude_ids=exclude
            )
            if len(recs) < n:
                fill = self.popularity_model.get_recommendations(
                    user_id, n - len(recs), exclude_ids=exclude | set(recs)
                )
                recs.extend(fill)
            return recs

        return self.popularity_model.get_recommendations(
            user_id or 0, n, exclude_ids=exclude
        )

    def get_similar_books(
        self,
        book_id: int,
        n: int = 5,
        exclude_ids: Optional[Set[int]] = None,
    ) -> List[int]:
        if not self.initialized:
            self.initialize()

        if not self.content_ready:
            return []

        return self.content_model.get_similar_books(
            book_id, n, exclude_ids=exclude_ids
        )

    def recommend_for_query(
        self,
        query: str,
        n: int = 10,
        exclude_ids: Optional[Set[int]] = None,
    ) -> List[int]:
        if not self.initialized:
            self.initialize()

        if not self.content_ready:
            return []

        return self.content_model.recommend_for_query(
            query, n, exclude_ids=exclude_ids
        )


_recommender_service: Optional[RecommenderService] = None


def get_recommender_service(model_path: Optional[str] = None) -> RecommenderService:
    """Get or create the singleton recommender service."""
    global _recommender_service
    if _recommender_service is None:
        _recommender_service = RecommenderService(model_path=model_path)
    elif model_path and _recommender_service.model_path != model_path:
        _recommender_service = RecommenderService(model_path=model_path)
    return _recommender_service


def reset_recommender_service() -> None:
    """Clear the singleton (used by tests)."""
    global _recommender_service
    _recommender_service = None
