"""
Recommender Service - ML-based book recommendations

Implemented:
- PopularityRecommender: rank by popularity_score
- ContentBasedRecommender: TF-IDF + cosine similarity on book text features
- CollaborativeFilteringRecommender: item–item CF or TruncatedSVD on a
  user–item matrix (explicit ratings + implicit purchase weights)
- Hybrid gating: CF when the user/matrix are dense enough, else content,
  else popularity
"""

from __future__ import annotations

import logging
import os
import pickle
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Set, Tuple

import numpy as np
from sklearn.decomposition import TruncatedSVD
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
    Collaborative filtering from a user–item matrix.

    Explicit Review.rating values are preferred; OrderItem purchases are
    folded in as implicit positive scores when no rating exists.

    Method selection (Capstone scale, no deep learning):
    - TruncatedSVD when the matrix is large enough for stable components
    - Item–item cosine similarity otherwise
    """

    MIN_MATRIX_USERS = 3
    MIN_MATRIX_ITEMS = 3
    MIN_MATRIX_INTERACTIONS = 8
    MIN_USER_INTERACTIONS = 2
    SVD_MIN_USERS = 5
    SVD_MIN_ITEMS = 5
    SVD_MIN_INTERACTIONS = 15
    SVD_COMPONENTS = 10
    PURCHASE_IMPLICIT_BASE = 3.0

    def __init__(self):
        self.user_ids: List[int] = []
        self.book_ids: List[int] = []
        self._user_to_idx: Dict[int, int] = {}
        self._book_to_idx: Dict[int, int] = {}
        self.matrix: Optional[np.ndarray] = None
        self.item_similarity: Optional[np.ndarray] = None
        self.reconstructed: Optional[np.ndarray] = None
        self.method: Optional[str] = None
        self.user_rated: Dict[int, Set[int]] = {}
        self._interaction_count = 0
        self._trained = False

    @classmethod
    def _merge_scores(
        cls,
        ratings: List[Dict],
        interactions: List[Dict],
    ) -> Dict[Tuple[int, int], float]:
        """
        Build (user_id, book_id) -> score.

        Explicit ratings win; purchases only fill missing cells (capped 1–5).
        """
        scores: Dict[Tuple[int, int], float] = {}

        for row in ratings:
            user_id = int(row['user_id'])
            book_id = int(row['book_id'])
            rating = float(row.get('rating', 0) or 0)
            if rating <= 0:
                continue
            scores[(user_id, book_id)] = min(5.0, max(1.0, rating))

        for row in interactions:
            user_id = int(row['user_id'])
            book_id = int(row['book_id'])
            key = (user_id, book_id)
            if key in scores:
                continue
            weight = float(row.get('weight', cls.PURCHASE_IMPLICIT_BASE) or 0)
            if weight <= 0:
                continue
            # Purchase weights are quantity * 3.0 in the training payload.
            scores[key] = min(5.0, max(1.0, weight if weight <= 5 else cls.PURCHASE_IMPLICIT_BASE))

        return scores

    def train(self, data: Dict) -> None:
        ratings = data.get('ratings') or []
        interactions = data.get('user_interactions') or []
        scores = self._merge_scores(ratings, interactions)

        if not scores:
            self._reset()
            logger.warning('CollaborativeFilteringRecommender.train() with no scores')
            return

        user_ids = sorted({u for u, _ in scores})
        book_ids = sorted({b for _, b in scores})
        self.user_ids = user_ids
        self.book_ids = book_ids
        self._user_to_idx = {u: i for i, u in enumerate(user_ids)}
        self._book_to_idx = {b: i for i, b in enumerate(book_ids)}
        self._interaction_count = len(scores)

        matrix = np.zeros((len(user_ids), len(book_ids)), dtype=float)
        self.user_rated = {u: set() for u in user_ids}
        for (user_id, book_id), score in scores.items():
            ui = self._user_to_idx[user_id]
            bi = self._book_to_idx[book_id]
            matrix[ui, bi] = score
            self.user_rated[user_id].add(book_id)

        self.matrix = matrix
        self.item_similarity = None
        self.reconstructed = None
        self.method = None

        if not self.matrix_ready:
            self._trained = False
            logger.info(
                'CF matrix too sparse to train (%s users, %s items, %s interactions)',
                len(user_ids),
                len(book_ids),
                self._interaction_count,
            )
            return

        n_users, n_items = matrix.shape
        use_svd = (
            n_users >= self.SVD_MIN_USERS
            and n_items >= self.SVD_MIN_ITEMS
            and self._interaction_count >= self.SVD_MIN_INTERACTIONS
        )

        if use_svd:
            n_components = min(
                self.SVD_COMPONENTS,
                n_users - 1,
                n_items - 1,
                max(1, self._interaction_count - 1),
            )
            if n_components >= 2:
                svd = TruncatedSVD(n_components=n_components, random_state=42)
                user_factors = svd.fit_transform(matrix)
                self.reconstructed = user_factors @ svd.components_
                self.method = 'svd'
            else:
                use_svd = False

        if not use_svd or self.method != 'svd':
            # Item–item: similarity between item rating vectors (columns).
            self.item_similarity = cosine_similarity(matrix.T)
            np.fill_diagonal(self.item_similarity, 0.0)
            self.method = 'item_item'

        self._trained = True
        logger.info(
            'CollaborativeFilteringRecommender trained (%s) on %s users, '
            '%s items, %s interactions',
            self.method,
            n_users,
            n_items,
            self._interaction_count,
        )

    def _reset(self) -> None:
        self.user_ids = []
        self.book_ids = []
        self._user_to_idx = {}
        self._book_to_idx = {}
        self.matrix = None
        self.item_similarity = None
        self.reconstructed = None
        self.method = None
        self.user_rated = {}
        self._interaction_count = 0
        self._trained = False

    @property
    def matrix_ready(self) -> bool:
        return (
            self.matrix is not None
            and len(self.user_ids) >= self.MIN_MATRIX_USERS
            and len(self.book_ids) >= self.MIN_MATRIX_ITEMS
            and self._interaction_count >= self.MIN_MATRIX_INTERACTIONS
        )

    @property
    def is_ready(self) -> bool:
        return bool(self._trained and self.matrix_ready and self.method)

    def can_recommend_for(self, user_id: int) -> bool:
        if not self.is_ready:
            return False
        uid = int(user_id)
        if uid not in self._user_to_idx:
            return False
        return len(self.user_rated.get(uid, ())) >= self.MIN_USER_INTERACTIONS

    def _score_user_vector(self, user_id: int) -> Optional[np.ndarray]:
        if not self.is_ready or self.matrix is None:
            return None
        uid = int(user_id)
        ui = self._user_to_idx.get(uid)
        if ui is None:
            return None

        if self.method == 'svd' and self.reconstructed is not None:
            return self.reconstructed[ui]

        # Item–item weighted sum
        if self.item_similarity is None:
            return None
        user_ratings = self.matrix[ui]
        # scores[j] = sum_i r_i * sim(i,j) / sum_i |sim(i,j)| over rated i
        numer = user_ratings @ self.item_similarity
        denom = np.abs(self.item_similarity).sum(axis=0)
        denom = np.where(denom == 0, 1.0, denom)
        return numer / denom

    def predict(self, user_id: int, book_ids: List[int]) -> List[float]:
        scores_vec = self._score_user_vector(user_id)
        if scores_vec is None:
            return [0.0] * len(book_ids)

        out = []
        for book_id in book_ids:
            bi = self._book_to_idx.get(int(book_id))
            if bi is None:
                out.append(0.0)
            else:
                out.append(float(scores_vec[bi]))
        return out

    def get_recommendations(
        self,
        user_id: int,
        n: int = 10,
        exclude_ids: Optional[Set[int]] = None,
    ) -> List[int]:
        if not self.can_recommend_for(user_id):
            return []

        scores_vec = self._score_user_vector(user_id)
        if scores_vec is None:
            return []

        exclude = set(exclude_ids or set())
        exclude |= set(self.user_rated.get(int(user_id), set()))

        ranked = np.argsort(scores_vec)[::-1]
        results: List[int] = []
        for bi in ranked:
            book_id = self.book_ids[bi]
            if book_id in exclude:
                continue
            if scores_vec[bi] <= 0:
                continue
            results.append(book_id)
            if len(results) >= n:
                break
        return results


class RecommenderService:
    """
    Service for managing recommendation models.

    Usage:
        service = RecommenderService()
        service.initialize()
        service.train_all(books_data, ratings_data, user_interactions)
        recommendations = service.get_recommendations(user_id=1, n=10, algorithm='hybrid')
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
        cf_path = os.path.join(self.model_path, 'cf.pkl')

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

        if not force_retrain and os.path.exists(cf_path):
            try:
                self.cf_model = CollaborativeFilteringRecommender.load(cf_path)
                logger.info('Loaded collaborative filtering model from disk')
            except Exception as e:
                logger.warning('Failed to load CF model: %s', e)
                self.cf_model = CollaborativeFilteringRecommender()
        else:
            self.cf_model = CollaborativeFilteringRecommender()

        self.initialized = True

    @property
    def content_ready(self) -> bool:
        return bool(
            self.content_model
            and getattr(self.content_model, '_trained', False)
            and self.content_model.tfidf_matrix is not None
        )

    @property
    def cf_ready(self) -> bool:
        return bool(self.cf_model and self.cf_model.is_ready)

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

        self.cf_model.train({
            'ratings': ratings_data,
            'user_interactions': user_interactions,
        })
        self.cf_model.save(os.path.join(self.model_path, 'cf.pkl'))

        logger.info('All recommender models trained successfully')

    def _fill_with_popularity(
        self,
        user_id: int,
        recs: List[int],
        n: int,
        exclude: Set[int],
    ) -> List[int]:
        if len(recs) >= n:
            return recs[:n]
        fill = self.popularity_model.get_recommendations(
            user_id, n - len(recs), exclude_ids=exclude | set(recs)
        )
        recs.extend(fill)
        return recs[:n]

    def get_recommendations(
        self,
        user_id: Optional[int] = None,
        n: int = 10,
        algorithm: str = 'hybrid',
        exclude_ids: Optional[Set[int]] = None,
    ) -> List[int]:
        ids, _ = self.recommend_for_user(
            user_id=user_id,
            n=n,
            algorithm=algorithm,
            exclude_ids=exclude_ids,
        )
        return ids

    def recommend_for_user(
        self,
        user_id: Optional[int] = None,
        n: int = 10,
        algorithm: str = 'hybrid',
        exclude_ids: Optional[Set[int]] = None,
    ) -> Tuple[List[int], str]:
        """
        Return (book_ids, algorithm_label).

        hybrid / collaborative: CF when gated, else content, else popularity.
        """
        if not self.initialized:
            self.initialize()

        exclude = set(exclude_ids or set())

        if algorithm == 'popularity' or user_id is None:
            return (
                self.popularity_model.get_recommendations(
                    user_id or 0, n, exclude_ids=exclude
                ),
                'popularity',
            )

        if algorithm == 'content':
            content_recs = (
                self.content_model.get_recommendations(
                    user_id, n, exclude_ids=exclude
                )
                if self.content_ready
                else []
            )
            recs = self._fill_with_popularity(
                user_id, list(content_recs), n, exclude
            )
            return recs, 'content_based' if content_recs else 'popularity'

        if algorithm == 'collaborative':
            if self.cf_ready and self.cf_model.can_recommend_for(user_id):
                cf_exclude = set(exclude) | set(
                    self.cf_model.user_rated.get(int(user_id), set())
                )
                recs = self.cf_model.get_recommendations(
                    user_id, n, exclude_ids=cf_exclude
                )
                if recs:
                    recs = self._fill_recommendations(user_id, recs, n, cf_exclude)
                    return recs, 'collaborative'
            # Strict collaborative request still falls back rather than empty
            return self.recommend_for_user(
                user_id=user_id,
                n=n,
                algorithm='content',
                exclude_ids=exclude,
            )

        # Hybrid: CF (gated) → content → popularity
        if (
            user_id is not None
            and self.cf_ready
            and self.cf_model.can_recommend_for(user_id)
        ):
            cf_exclude = set(exclude) | set(
                self.cf_model.user_rated.get(int(user_id), set())
            )
            recs = self.cf_model.get_recommendations(
                user_id, n, exclude_ids=cf_exclude
            )
            if recs:
                recs = self._fill_recommendations(user_id, recs, n, cf_exclude)
                return recs, 'collaborative'

        if self.content_ready and user_id is not None:
            content_exclude = set(exclude)
            for book_id, _ in self.content_model.user_interactions.get(
                int(user_id), []
            ):
                content_exclude.add(book_id)
            recs = self.content_model.get_recommendations(
                user_id, n, exclude_ids=content_exclude
            )
            recs = self._fill_with_popularity(user_id, recs, n, content_exclude)
            return recs, 'content_based'

        return (
            self.popularity_model.get_recommendations(
                user_id or 0, n, exclude_ids=exclude
            ),
            'popularity',
        )

    def _fill_recommendations(
        self,
        user_id: int,
        recs: List[int],
        n: int,
        exclude: Set[int],
    ) -> List[int]:
        """Fill remaining slots with content then popularity."""
        if len(recs) >= n:
            return recs[:n]

        seen = exclude | set(recs)
        if self.content_ready:
            content_fill = self.content_model.get_recommendations(
                user_id, n - len(recs), exclude_ids=seen
            )
            for book_id in content_fill:
                if book_id not in seen:
                    recs.append(book_id)
                    seen.add(book_id)
                if len(recs) >= n:
                    return recs[:n]

        return self._fill_with_popularity(user_id, recs, n, exclude)

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
