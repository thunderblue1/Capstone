"""
Recommendations API Routes Module
=================================

Purpose:
    Provides REST API endpoints for book recommendations using
    popularity heuristics and (when enabled) content-based TF-IDF models.

Endpoints:
    GET /api/recommendations               - General recommendations
    GET /api/recommendations/personalized  - User-specific (auth required)
    GET /api/recommendations/similar/<id>  - Similar books to given book
    GET /api/recommendations/search-based  - Recommendations based on search

When RECOMMENDER_ENABLED is true, endpoints prefer ContentBasedRecommender
and fall back to SQL heuristics when the model cannot produce enough results.
"""
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import desc, or_

from models import Book, Order, Review
from services.recommender import get_recommender_service

recommendations_bp = Blueprint('recommendations', __name__)


def _books_by_ids(book_ids):
    """Fetch books preserving the order of book_ids."""
    if not book_ids:
        return []
    books = Book.query.filter(Book.id.in_(book_ids)).all()
    by_id = {book.id: book for book in books}
    return [by_id[book_id] for book_id in book_ids if book_id in by_id]


def _in_stock_ids(book_ids):
    """Filter recommendation IDs to books that are currently in stock."""
    if not book_ids:
        return []
    rows = Book.query.filter(
        Book.id.in_(book_ids),
        Book.stock_quantity > 0,
    ).with_entities(Book.id).all()
    in_stock = {row[0] for row in rows}
    return [book_id for book_id in book_ids if book_id in in_stock]


def _collect_training_payload():
    """Build books + interaction data for training recommender models."""
    books = Book.query.all()
    books_data = []
    for book in books:
        category_name = book.category.name if book.category else ''
        books_data.append({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'genre': book.genre or '',
            'category_name': category_name,
            'description': book.description or '',
            'popularity_score': book.popularity_score or 0,
        })

    ratings_data = [
        {
            'user_id': review.user_id,
            'book_id': review.book_id,
            'rating': review.rating,
        }
        for review in Review.query.all()
    ]

    user_interactions = []
    for review in Review.query.all():
        user_interactions.append({
            'user_id': review.user_id,
            'book_id': review.book_id,
            'weight': float(review.rating or 1.0),
        })

    for order in Order.query.all():
        for item in order.items:
            user_interactions.append({
                'user_id': order.user_id,
                'book_id': item.book_id,
                'weight': float(item.quantity or 1) * 3.0,
            })

    return books_data, ratings_data, user_interactions


def _ensure_recommender():
    """
    Return a trained RecommenderService when enabled, else None.
    Trains from the current DB if models are not ready.
    """
    if not current_app.config.get('RECOMMENDER_ENABLED'):
        return None

    model_path = current_app.config.get('RECOMMENDER_MODEL_PATH', 'models/recommender')
    service = get_recommender_service(model_path=model_path)
    if not service.initialized:
        service.initialize()

    if not service.content_ready:
        books_data, ratings_data, user_interactions = _collect_training_payload()
        if books_data:
            service.train_all(books_data, ratings_data, user_interactions)

    return service if service.content_ready else None


def _heuristic_similar(book, limit):
    query = Book.query.filter(
        Book.id != book.id,
        Book.stock_quantity > 0,
    )

    if book.genre:
        query = query.filter(Book.genre == book.genre)
    elif book.category_id:
        query = query.filter(Book.category_id == book.category_id)

    similar_books = query.order_by(
        desc(Book.average_rating),
        desc(Book.popularity_score),
    ).limit(limit).all()

    if len(similar_books) < limit and book.author:
        author_books = Book.query.filter(
            Book.id != book.id,
            Book.author == book.author,
            Book.stock_quantity > 0,
            ~Book.id.in_([b.id for b in similar_books]),
        ).limit(limit - len(similar_books)).all()
        similar_books.extend(author_books)

    return similar_books


def _heuristic_personalized(user_id, limit, user_book_ids):
    preferred_genres = set()
    preferred_categories = set()

    user_reviews = Review.query.filter_by(user_id=user_id).all()
    for review in user_reviews:
        if review.book and review.book.genre:
            preferred_genres.add(review.book.genre)
        if review.book and review.book.category_id:
            preferred_categories.add(review.book.category_id)

    query = Book.query.filter(Book.stock_quantity > 0)
    if user_book_ids:
        query = query.filter(~Book.id.in_(user_book_ids))

    if preferred_genres or preferred_categories:
        filters = []
        if preferred_genres:
            filters.append(Book.genre.in_(preferred_genres))
        if preferred_categories:
            filters.append(Book.category_id.in_(preferred_categories))
        query = query.filter(or_(*filters))

    books = query.order_by(
        desc(Book.average_rating),
        desc(Book.popularity_score),
    ).limit(limit).all()

    if len(books) < limit:
        additional_ids = [b.id for b in books]
        additional = Book.query.filter(
            Book.stock_quantity > 0,
            ~Book.id.in_(user_book_ids | set(additional_ids)),
        ).order_by(desc(Book.popularity_score)).limit(limit - len(books)).all()
        books.extend(additional)

    return books, preferred_genres, preferred_categories


@recommendations_bp.route('/', methods=['GET'])
def get_recommendations():
    """Get book recommendations (popularity-based)."""
    limit = request.args.get('limit', 8, type=int)
    exclude_ids = request.args.getlist('exclude', type=int)

    query = Book.query.filter(Book.stock_quantity > 0)
    if exclude_ids:
        query = query.filter(~Book.id.in_(exclude_ids))

    books = query.order_by(
        desc(Book.popularity_score),
        desc(Book.average_rating),
    ).limit(limit).all()

    return jsonify({
        'recommendations': [book.to_dict() for book in books],
        'algorithm': 'popularity',
        'personalized': False,
    })


@recommendations_bp.route('/personalized', methods=['GET'])
@jwt_required()
def get_personalized_recommendations():
    """Get personalized recommendations for the logged-in user."""
    user_id = int(get_jwt_identity())
    limit = request.args.get('limit', 8, type=int)

    user_book_ids = set()
    user_reviews = Review.query.filter_by(user_id=user_id).all()
    for review in user_reviews:
        user_book_ids.add(review.book_id)

    user_orders = Order.query.filter_by(user_id=user_id).all()
    for order in user_orders:
        for item in order.items:
            user_book_ids.add(item.book_id)

    service = _ensure_recommender()
    if service is not None:
        # Retrain so this user's latest interactions are in the profile
        books_data, ratings_data, user_interactions = _collect_training_payload()
        service.train_all(books_data, ratings_data, user_interactions)

        recommended_ids = service.get_recommendations(
            user_id=user_id,
            n=limit,
            algorithm='content',
            exclude_ids=user_book_ids,
        )
        recommended_ids = _in_stock_ids(recommended_ids)[:limit]
        books = _books_by_ids(recommended_ids)

        if len(books) < limit:
            fill = Book.query.filter(
                Book.stock_quantity > 0,
                ~Book.id.in_(user_book_ids | {b.id for b in books}),
            ).order_by(desc(Book.popularity_score)).limit(limit - len(books)).all()
            books.extend(fill)

        return jsonify({
            'recommendations': [book.to_dict() for book in books],
            'algorithm': 'content_based',
            'personalized': True,
            'basedOn': {
                'interactionCount': len(user_book_ids),
            },
        })

    books, preferred_genres, preferred_categories = _heuristic_personalized(
        user_id, limit, user_book_ids
    )
    return jsonify({
        'recommendations': [book.to_dict() for book in books],
        'algorithm': 'collaborative_heuristic',
        'personalized': True,
        'basedOn': {
            'genres': list(preferred_genres),
            'categoryIds': list(preferred_categories),
        },
    })


@recommendations_bp.route('/similar/<int:book_id>', methods=['GET'])
def get_similar_books(book_id):
    """Get books similar to a specific book."""
    limit = request.args.get('limit', 4, type=int)
    book = Book.query.get_or_404(book_id)

    service = _ensure_recommender()
    if service is not None:
        similar_ids = service.get_similar_books(book_id, n=limit * 2)
        similar_ids = _in_stock_ids(similar_ids)[:limit]
        similar_books = _books_by_ids(similar_ids)

        if len(similar_books) < limit:
            heuristic = _heuristic_similar(book, limit)
            seen = {b.id for b in similar_books}
            for candidate in heuristic:
                if candidate.id not in seen:
                    similar_books.append(candidate)
                    seen.add(candidate.id)
                if len(similar_books) >= limit:
                    break

        return jsonify({
            'book': book.to_dict(),
            'similar': [b.to_dict() for b in similar_books],
            'algorithm': 'content_based',
        })

    similar_books = _heuristic_similar(book, limit)
    return jsonify({
        'book': book.to_dict(),
        'similar': [b.to_dict() for b in similar_books],
        'algorithm': 'content_heuristic',
    })


@recommendations_bp.route('/search-based', methods=['GET'])
def get_search_recommendations():
    """Get recommendations based on search query context."""
    query_text = request.args.get('q', '')
    limit = request.args.get('limit', 4, type=int)
    exclude_ids = request.args.getlist('exclude', type=int)

    service = _ensure_recommender()
    if service is not None and query_text:
        recommended_ids = service.recommend_for_query(
            query_text,
            n=limit * 2,
            exclude_ids=set(exclude_ids),
        )
        recommended_ids = _in_stock_ids(recommended_ids)[:limit]
        books = _books_by_ids(recommended_ids)

        if books:
            return jsonify({
                'recommendations': [book.to_dict() for book in books],
                'algorithm': 'content_based',
                'query': query_text,
            })

    if not query_text:
        books = Book.query.filter(Book.stock_quantity > 0)\
            .order_by(desc(Book.popularity_score))\
            .limit(limit).all()
    else:
        search_filter = or_(
            Book.genre.ilike(f'%{query_text}%'),
            Book.description.ilike(f'%{query_text}%'),
            Book.title.ilike(f'%{query_text}%'),
            Book.author.ilike(f'%{query_text}%'),
        )
        books_query = Book.query.filter(
            search_filter,
            Book.stock_quantity > 0,
        )
        if exclude_ids:
            books_query = books_query.filter(~Book.id.in_(exclude_ids))

        books = books_query.order_by(
            desc(Book.average_rating),
            desc(Book.popularity_score),
        ).limit(limit).all()

    return jsonify({
        'recommendations': [book.to_dict() for book in books],
        'algorithm': 'search_context',
        'query': query_text,
    })
