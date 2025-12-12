"""
Recommendations API Routes Module
=================================

Purpose:
    Provides REST API endpoints for book recommendations using
    various algorithms including popularity-based, collaborative
    filtering, and content-based approaches.

Endpoints:
    GET /api/recommendations               - General recommendations
    GET /api/recommendations/personalized  - User-specific (auth required)
    GET /api/recommendations/similar/<id>  - Similar books to given book
    GET /api/recommendations/search-based  - Recommendations based on search

Algorithms:
    - 'popularity': Default, uses popularity_score and average_rating
    - 'collaborative_heuristic': Based on user's review/order history
    - 'content_heuristic': Genre/category matching
    - 'search_context': Related to search query

Future ML Integration:
    These endpoints use heuristic algorithms as placeholders.
    Replace with actual ML models by:
    1. Implementing model in services/recommender.py
    2. Updating endpoint functions to call model.predict()
    3. Updating 'algorithm' field in response to track model version

Query Parameters:
    limit (int): Number of recommendations to return (default: 8)
    exclude (list): Book IDs to exclude from results

Usage:
    This blueprint is registered in routes/__init__.py and mounted
    at /api/recommendations.

Dependencies:
    - Flask-JWT-Extended for personalized recommendations
    - models.Book, models.Review, models.Order for data access
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, jwt_required
from sqlalchemy import desc
from models import db, Book, User, Review, Order

recommendations_bp = Blueprint('recommendations', __name__)


@recommendations_bp.route('/', methods=['GET'])
def get_recommendations():
    """
    Get book recommendations.
    
    This is a placeholder that uses simple heuristics.
    Replace with actual ML model predictions when ready.
    """
    limit = request.args.get('limit', 8, type=int)
    exclude_ids = request.args.getlist('exclude', type=int)
    
    # For now, return popular books with good ratings
    query = Book.query.filter(Book.stock_quantity > 0)
    
    if exclude_ids:
        query = query.filter(~Book.id.in_(exclude_ids))
    
    books = query.order_by(
        desc(Book.popularity_score),
        desc(Book.average_rating)
    ).limit(limit).all()
    
    return jsonify({
        'recommendations': [book.to_dict() for book in books],
        'algorithm': 'popularity',  # Track which algorithm was used
        'personalized': False
    })


@recommendations_bp.route('/personalized', methods=['GET'])
@jwt_required()
def get_personalized_recommendations():
    """
    Get personalized recommendations for the logged-in user.
    
    This is a placeholder that uses simple collaborative filtering heuristics.
    Replace with actual ML model when ready.
    """
    user_id = get_jwt_identity()
    limit = request.args.get('limit', 8, type=int)
    
    # Get user's reviewed/ordered books to exclude
    user_book_ids = set()
    
    # Books user has reviewed
    user_reviews = Review.query.filter_by(user_id=user_id).all()
    for review in user_reviews:
        user_book_ids.add(review.book_id)
    
    # Books user has ordered
    user_orders = Order.query.filter_by(user_id=user_id).all()
    for order in user_orders:
        for item in order.items:
            user_book_ids.add(item.book_id)
    
    # Get user's preferred genres/categories from reviews and orders
    preferred_genres = set()
    preferred_categories = set()
    
    for review in user_reviews:
        if review.book.genre:
            preferred_genres.add(review.book.genre)
        if review.book.category_id:
            preferred_categories.add(review.book.category_id)
    
    # Build recommendation query
    query = Book.query.filter(Book.stock_quantity > 0)
    
    if user_book_ids:
        query = query.filter(~Book.id.in_(user_book_ids))
    
    # If user has preferences, filter by them
    if preferred_genres or preferred_categories:
        from sqlalchemy import or_
        filters = []
        if preferred_genres:
            filters.append(Book.genre.in_(preferred_genres))
        if preferred_categories:
            filters.append(Book.category_id.in_(preferred_categories))
        query = query.filter(or_(*filters))
    
    books = query.order_by(
        desc(Book.average_rating),
        desc(Book.popularity_score)
    ).limit(limit).all()
    
    # If not enough books, fill with popular ones
    if len(books) < limit:
        additional_ids = [b.id for b in books]
        additional = Book.query.filter(
            Book.stock_quantity > 0,
            ~Book.id.in_(user_book_ids | set(additional_ids))
        ).order_by(desc(Book.popularity_score)).limit(limit - len(books)).all()
        books.extend(additional)
    
    return jsonify({
        'recommendations': [book.to_dict() for book in books],
        'algorithm': 'collaborative_heuristic',
        'personalized': True,
        'basedOn': {
            'genres': list(preferred_genres),
            'categoryIds': list(preferred_categories)
        }
    })


@recommendations_bp.route('/similar/<int:book_id>', methods=['GET'])
def get_similar_books(book_id):
    """
    Get books similar to a specific book.
    
    This is a placeholder using genre/category matching.
    Replace with content-based filtering model when ready.
    """
    limit = request.args.get('limit', 4, type=int)
    
    book = Book.query.get_or_404(book_id)
    
    # Find books in same genre/category
    query = Book.query.filter(
        Book.id != book_id,
        Book.stock_quantity > 0
    )
    
    # Prioritize same genre
    if book.genre:
        query = query.filter(Book.genre == book.genre)
    elif book.category_id:
        query = query.filter(Book.category_id == book.category_id)
    
    similar_books = query.order_by(
        desc(Book.average_rating),
        desc(Book.popularity_score)
    ).limit(limit).all()
    
    # If not enough, get from same author
    if len(similar_books) < limit and book.author:
        author_books = Book.query.filter(
            Book.id != book_id,
            Book.author == book.author,
            Book.stock_quantity > 0,
            ~Book.id.in_([b.id for b in similar_books])
        ).limit(limit - len(similar_books)).all()
        similar_books.extend(author_books)
    
    return jsonify({
        'book': book.to_dict(),
        'similar': [b.to_dict() for b in similar_books],
        'algorithm': 'content_heuristic'
    })


@recommendations_bp.route('/search-based', methods=['GET'])
def get_search_recommendations():
    """
    Get recommendations based on search query context.
    
    This is a placeholder for search-based recommendations.
    Replace with actual ML model when ready.
    """
    query = request.args.get('q', '')
    limit = request.args.get('limit', 4, type=int)
    exclude_ids = request.args.getlist('exclude', type=int)
    
    if not query:
        # Return popular books if no query
        books = Book.query.filter(Book.stock_quantity > 0)\
            .order_by(desc(Book.popularity_score))\
            .limit(limit).all()
    else:
        # Find books related to search query but not in main results
        from sqlalchemy import or_
        
        search_filter = or_(
            Book.genre.ilike(f'%{query}%'),
            Book.description.ilike(f'%{query}%')
        )
        
        books_query = Book.query.filter(
            search_filter,
            Book.stock_quantity > 0
        )
        
        if exclude_ids:
            books_query = books_query.filter(~Book.id.in_(exclude_ids))
        
        books = books_query.order_by(
            desc(Book.average_rating),
            desc(Book.popularity_score)
        ).limit(limit).all()
    
    return jsonify({
        'recommendations': [book.to_dict() for book in books],
        'algorithm': 'search_context',
        'query': query
    })

