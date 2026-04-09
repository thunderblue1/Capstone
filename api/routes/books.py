"""
Books API Routes Module
=======================

Purpose:
    Provides REST API endpoints for book-related operations including
    listing, searching, filtering, and retrieving book details.

Endpoints:
    GET  /api/books                    - List all books with pagination/filtering
    GET  /api/books/featured           - Get featured/popular books
    GET  /api/books/search             - Search books by title/author/description
    GET  /api/books/category/<name>    - Get books by category name
    GET  /api/books/<id>               - Get single book by ID
    GET  /api/books/<id>/reviews       - Get reviews for a book
    GET  /api/books/genres             - Get all unique genres

Usage:
    This blueprint is registered in routes/__init__.py and mounted
    at /api/books. All endpoints return JSON responses.

Dependencies:
    - Flask for routing
    - SQLAlchemy for database queries
    - models.Book and models.Category for data access
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import or_, desc
from models import db, Book, Category
from utils.auth import product_manager_required

books_bp = Blueprint('books', __name__)


@books_bp.route('/', methods=['GET'])
def get_books():
    """
    Get all books with optional filtering and pagination.
    
    Query Parameters:
        page (int): Page number for pagination (default: 1)
        per_page (int): Items per page, max 100 (default: 20)
        category_id (int): Filter by category ID
        genre (str): Filter by genre name
        min_price (float): Minimum price filter
        max_price (float): Maximum price filter
        in_stock (bool): If true, only return books with stock > 0
        sort_by (str): Column to sort by (default: popularity_score)
        sort_order (str): 'asc' or 'desc' (default: desc)
    
    Returns:
        JSON object with books array and pagination metadata
    """
    # ─────────────────────────────────────────────────────────────
    # PAGINATION: Extract and validate page parameters
    # ─────────────────────────────────────────────────────────────
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(per_page, 100)  # Cap at 100 to prevent performance issues
    
    # ─────────────────────────────────────────────────────────────
    # FILTERS: Extract optional filter parameters from query string
    # ─────────────────────────────────────────────────────────────
    category_id = request.args.get('category_id', type=int)
    genre = request.args.get('genre')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    in_stock = request.args.get('in_stock', type=lambda x: x.lower() == 'true')
    
    # ─────────────────────────────────────────────────────────────
    # SORTING: Determine sort column and direction
    # ─────────────────────────────────────────────────────────────
    sort_by = request.args.get('sort_by', 'popularity_score')
    sort_order = request.args.get('sort_order', 'desc')
    
    # ─────────────────────────────────────────────────────────────
    # QUERY BUILDING: Apply filters dynamically based on parameters
    # ─────────────────────────────────────────────────────────────
    query = Book.query
    
    # Apply each filter only if the parameter was provided
    if category_id:
        query = query.filter(Book.category_id == category_id)
    if genre:
        query = query.filter(Book.genre == genre)
    if min_price is not None:
        query = query.filter(Book.price >= min_price)
    if max_price is not None:
        query = query.filter(Book.price <= max_price)
    if in_stock:
        query = query.filter(Book.stock_quantity > 0)
    
    # ─────────────────────────────────────────────────────────────
    # SORTING: Apply sort with fallback to popularity_score
    # ─────────────────────────────────────────────────────────────
    sort_column = getattr(Book, sort_by, Book.popularity_score)
    if sort_order == 'desc':
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)
    
    # ─────────────────────────────────────────────────────────────
    # PAGINATION: Execute query with pagination
    # ─────────────────────────────────────────────────────────────
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'books': [book.to_dict() for book in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'currentPage': page,
        'perPage': per_page,
        'hasNext': pagination.has_next,
        'hasPrev': pagination.has_prev
    })


@books_bp.route('/featured', methods=['GET'])
def get_featured_books():
    """Get featured books (high popularity/rating)"""
    limit = request.args.get('limit', 4, type=int)
    
    books = Book.query\
        .filter(Book.stock_quantity > 0)\
        .order_by(desc(Book.popularity_score), desc(Book.average_rating))\
        .limit(limit)\
        .all()
    
    return jsonify({
        'books': [book.to_dict() for book in books]
    })


@books_bp.route('/search', methods=['GET'])
def search_books():
    """Search books by title, author, or description"""
    query_text = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(per_page, 100)
    
    if not query_text:
        return jsonify({
            'results': [],
            'total': 0,
            'pages': 0,
            'currentPage': page
        })
    
    # Search in title, author, description, genre
    search_filter = or_(
        Book.title.ilike(f'%{query_text}%'),
        Book.author.ilike(f'%{query_text}%'),
        Book.description.ilike(f'%{query_text}%'),
        Book.genre.ilike(f'%{query_text}%'),
        Book.isbn_13.ilike(f'%{query_text}%')
    )
    
    query = Book.query.filter(search_filter).order_by(desc(Book.popularity_score))
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'results': [book.to_dict() for book in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'currentPage': page,
        'query': query_text
    })


@books_bp.route('/category/<category_name>', methods=['GET'])
def get_books_by_category_name(category_name):
    """Get books by category name"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Find category by name (case-insensitive)
    category = Category.query.filter(Category.name.ilike(category_name)).first()
    
    if not category:
        return jsonify({
            'books': [],
            'total': 0,
            'pages': 0,
            'currentPage': page,
            'category': category_name
        })
    
    query = Book.query.filter(Book.category_id == category.id)\
        .order_by(desc(Book.popularity_score))
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'books': [book.to_dict() for book in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'currentPage': page,
        'category': category.to_dict()
    })


@books_bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """Get a single book by ID"""
    book = Book.query.get_or_404(book_id)
    return jsonify(book.to_dict(include_category=True))


@books_bp.route('/<int:book_id>/reviews', methods=['GET'])
def get_book_reviews(book_id):
    """Get reviews for a specific book"""
    from models import Review
    
    book = Book.query.get_or_404(book_id)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pagination = book.reviews.order_by(desc(Review.created_at))\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'reviews': [review.to_dict() for review in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'currentPage': page,
        'averageRating': book.average_rating,
        'reviewCount': book.review_count
    })


@books_bp.route('/genres', methods=['GET'])
def get_genres():
    """Get all unique genres"""
    genres = db.session.query(Book.genre)\
        .filter(Book.genre.isnot(None))\
        .distinct()\
        .order_by(Book.genre)\
        .all()
    
    return jsonify({
        'genres': [g[0] for g in genres if g[0]]
    })


# ─────────────────────────────────────────────────────────────
# MANAGER-ONLY CRUD OPERATIONS
# ─────────────────────────────────────────────────────────────

@books_bp.route('/', methods=['POST'])
@jwt_required()
@product_manager_required
def create_book():
    """
    Create a new book (Manager only)
    
    Request Body:
        {
            "title": "Book Title",
            "author": "Author Name",
            "isbn13": "9781234567890",
            "publisher": "Publisher Name",
            "publicationDate": "2024-01-01",
            "language": "en",
            "genre": "Fiction",
            "description": "Book description",
            "pageCount": 300,
            "price": 29.99,
            "currency": "USD",
            "stockQuantity": 100,
            "coverImageUrl": "https://example.com/image.jpg",
            "categoryId": 1
        }
    
    Returns:
        201: Book created successfully
        400: Invalid request data
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Required fields
    required_fields = ['title', 'author', 'isbn13', 'price']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Check if ISBN already exists
    if Book.query.filter_by(isbn_13=data['isbn13']).first():
        return jsonify({'error': 'Book with this ISBN already exists'}), 409
    
    # Create new book
    book = Book(
        title=data['title'],
        author=data['author'],
        isbn_13=data['isbn13'],
        publisher=data.get('publisher'),
        publication_date=data.get('publicationDate'),
        language=data.get('language', 'en'),
        genre=data.get('genre'),
        description=data.get('description'),
        page_count=data.get('pageCount'),
        price=data['price'],
        currency=data.get('currency', 'USD'),
        stock_quantity=data.get('stockQuantity', 0),
        cover_image_url=data.get('coverImageUrl'),
        category_id=data.get('categoryId')
    )
    
    db.session.add(book)
    db.session.commit()
    
    return jsonify({
        'message': 'Book created successfully',
        'book': book.to_dict(include_category=True)
    }), 201


@books_bp.route('/<int:book_id>', methods=['PUT'])
@jwt_required()
@product_manager_required
def update_book(book_id):
    """
    Update an existing book (Manager only)
    
    Request Body:
        Partial book data to update (all fields optional)
    
    Returns:
        200: Book updated successfully
        404: Book not found
    """
    book = Book.query.get_or_404(book_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Update fields if provided
    if 'title' in data:
        book.title = data['title']
    if 'author' in data:
        book.author = data['author']
    if 'isbn13' in data:
        # Check if ISBN is already used by another book
        existing = Book.query.filter_by(isbn_13=data['isbn13']).first()
        if existing and existing.id != book_id:
            return jsonify({'error': 'ISBN already in use'}), 409
        book.isbn_13 = data['isbn13']
    if 'publisher' in data:
        book.publisher = data['publisher']
    if 'publicationDate' in data:
        book.publication_date = data['publicationDate']
    if 'language' in data:
        book.language = data['language']
    if 'genre' in data:
        book.genre = data['genre']
    if 'description' in data:
        book.description = data['description']
    if 'pageCount' in data:
        book.page_count = data['pageCount']
    if 'price' in data:
        book.price = data['price']
    if 'currency' in data:
        book.currency = data['currency']
    if 'stockQuantity' in data:
        book.stock_quantity = data['stockQuantity']
    if 'coverImageUrl' in data:
        book.cover_image_url = data['coverImageUrl']
    if 'categoryId' in data:
        book.category_id = data['categoryId']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Book updated successfully',
        'book': book.to_dict(include_category=True)
    })


@books_bp.route('/<int:book_id>', methods=['DELETE'])
@jwt_required()
@product_manager_required
def delete_book(book_id):
    """
    Delete a book (Manager only)
    
    Returns:
        200: Book deleted successfully
        404: Book not found
        400: Cannot delete book (e.g., has orders)
    """
    book = Book.query.get_or_404(book_id)
    
    # Check if book has associated orders
    from models import OrderItem
    order_items = OrderItem.query.filter_by(book_id=book_id).first()
    if order_items:
        return jsonify({
            'error': 'Cannot delete book with existing orders. Consider marking as out of stock instead.'
        }), 400
    
    db.session.delete(book)
    db.session.commit()
    
    return jsonify({
        'message': 'Book deleted successfully'
    })

