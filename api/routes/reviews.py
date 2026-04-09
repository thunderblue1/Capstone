"""
Reviews API Routes Module
=========================

Purpose:
    Provides REST API endpoints for book review operations including
    creating, reading, updating, and deleting reviews. Also manages
    book rating statistics.

Endpoints:
    GET    /api/reviews              - List reviews with filtering
    GET    /api/reviews/<id>         - Get single review
    POST   /api/reviews              - Create new review (auth required)
    PUT    /api/reviews/<id>         - Update review (auth required, owner only)
    DELETE /api/reviews/<id>         - Delete review (auth required, owner only)
    GET    /api/reviews/book/<id>    - Get all reviews for a book

Rating System:
    - Ratings are 0-5 (inclusive)
    - One review per user per book
    - Book average_rating and review_count auto-update on changes

Authorization:
    - Creating reviews requires authentication
    - Updating/deleting requires ownership (user_id must match)

Usage:
    This blueprint is registered in routes/__init__.py and mounted
    at /api/reviews. Rating stats are computed via Book.update_rating_stats().

Dependencies:
    - Flask-JWT-Extended for authentication
    - models.Review, models.Book, models.User for data access
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc
from models import db, Review, Book, User

reviews_bp = Blueprint('reviews', __name__)


@reviews_bp.route('/', methods=['GET'])
@jwt_required(optional=True)
def get_reviews():
    """Get all reviews with optional filtering. Filtering by user_id allowed only for own id or admin."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    book_id = request.args.get('book_id', type=int)
    user_id = request.args.get('user_id', type=int)

    # Horizontal escalation prevention: listing another user's reviews only as owner or admin
    if user_id is not None:
        current_id = get_jwt_identity()
        if not current_id:
            return jsonify({'error': 'Authentication required to filter by user'}), 401
        current_user = User.query.get(current_id)
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        if str(current_user.id) != str(user_id) and not current_user.is_admin():
            return jsonify({'error': 'Not authorized to list reviews for this user'}), 403
    
    query = Review.query
    
    if book_id:
        query = query.filter(Review.book_id == book_id)
    if user_id is not None:
        query = query.filter(Review.user_id == user_id)
    
    query = query.order_by(desc(Review.created_at))
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'reviews': [review.to_dict() for review in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'currentPage': page
    })


@reviews_bp.route('/<int:review_id>', methods=['GET'])
def get_review(review_id):
    """Get a single review by ID"""
    review = Review.query.get_or_404(review_id)
    return jsonify(review.to_dict(include_book=True))


@reviews_bp.route('/', methods=['POST'])
@jwt_required()
def create_review():
    """Create a new review"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    book_id = data.get('bookId')
    rating = data.get('rating')
    comment = data.get('text') or data.get('comment')
    
    if not book_id:
        return jsonify({'error': 'bookId is required'}), 400
    if rating is None:
        return jsonify({'error': 'rating is required'}), 400
    if not (0 <= rating <= 5):
        return jsonify({'error': 'rating must be between 0 and 5'}), 400
    
    # Check if book exists
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    # Check if user already reviewed this book
    existing = Review.query.filter_by(user_id=user_id, book_id=book_id).first()
    if existing:
        return jsonify({'error': 'You have already reviewed this book'}), 409
    
    # Create review
    review = Review(
        user_id=user_id,
        book_id=book_id,
        rating=rating,
        comment=comment
    )
    
    db.session.add(review)
    
    # Update book rating stats
    book.update_rating_stats()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Review created successfully',
        'review': review.to_dict()
    }), 201


@reviews_bp.route('/<int:review_id>', methods=['PUT'])
@jwt_required()
def update_review(review_id):
    """Update an existing review"""
    user_id = get_jwt_identity()
    review = Review.query.get_or_404(review_id)
    
    # Check ownership
    if str(review.user_id) != str(user_id):
        return jsonify({'error': 'Not authorized to update this review'}), 403
    
    data = request.get_json()
    
    if 'rating' in data:
        rating = data['rating']
        if not (0 <= rating <= 5):
            return jsonify({'error': 'rating must be between 0 and 5'}), 400
        review.rating = rating
    
    if 'text' in data:
        review.comment = data['text']
    elif 'comment' in data:
        review.comment = data['comment']
    
    # Update book rating stats
    review.book.update_rating_stats()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Review updated successfully',
        'review': review.to_dict()
    })


@reviews_bp.route('/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    """Delete a review"""
    user_id = get_jwt_identity()
    review = Review.query.get_or_404(review_id)
    
    # Check ownership
    if str(review.user_id) != str(user_id):
        return jsonify({'error': 'Not authorized to delete this review'}), 403
    
    book = review.book
    db.session.delete(review)
    
    # Update book rating stats
    book.update_rating_stats()
    
    db.session.commit()
    
    return jsonify({'message': 'Review deleted successfully'})


@reviews_bp.route('/book/<int:book_id>', methods=['GET'])
def get_book_reviews(book_id):
    """Get all reviews for a specific book"""
    book = Book.query.get_or_404(book_id)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pagination = Review.query.filter_by(book_id=book_id)\
        .order_by(desc(Review.created_at))\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'bookId': str(book_id),
        'reviews': [review.to_dict() for review in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'currentPage': page,
        'averageRating': book.average_rating,
        'reviewCount': book.review_count
    })

