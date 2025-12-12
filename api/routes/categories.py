"""
Categories API Routes Module
============================

Purpose:
    Provides REST API endpoints for book category operations including
    listing categories, retrieving category details, and getting books
    within a category.

Endpoints:
    GET /api/categories                 - List all categories
    GET /api/categories/<id>            - Get category by ID
    GET /api/categories/<id>/books      - Get books in a category
    GET /api/categories/name/<name>     - Get category by name

Category Structure:
    Categories support hierarchical structure via parent_id.
    Root categories have parent_id = NULL.
    Use include_subcategories=true to get nested structure.

Query Parameters:
    root_only (bool): If true, only return root categories
    include_subcategories (bool): If true, include nested subcategories

Usage:
    This blueprint is registered in routes/__init__.py and mounted
    at /api/categories. Categories are used for book organization.

Dependencies:
    - models.Category for category data access
    - models.Book for category-book relationships
"""
from flask import Blueprint, jsonify, request
from models import db, Category

categories_bp = Blueprint('categories', __name__)


@categories_bp.route('/', methods=['GET'])
def get_categories():
    """Get all categories"""
    include_subcategories = request.args.get('include_subcategories', 'false').lower() == 'true'
    
    # Get only root categories (no parent)
    if request.args.get('root_only', 'false').lower() == 'true':
        categories = Category.query.filter(Category.parent_id.is_(None)).all()
    else:
        categories = Category.query.all()
    
    return jsonify({
        'categories': [cat.to_dict(include_subcategories=include_subcategories) for cat in categories]
    })


@categories_bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """Get a single category by ID"""
    category = Category.query.get_or_404(category_id)
    return jsonify(category.to_dict(include_parent=True, include_subcategories=True))


@categories_bp.route('/<int:category_id>/books', methods=['GET'])
def get_category_books(category_id):
    """Get all books in a category"""
    from sqlalchemy import desc
    from models import Book
    
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = Book.query.filter(Book.category_id == category_id)\
        .order_by(desc(Book.popularity_score))
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'category': category.to_dict(),
        'books': [book.to_dict() for book in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'currentPage': page
    })


@categories_bp.route('/name/<category_name>', methods=['GET'])
def get_category_by_name(category_name):
    """Get a category by name (case-insensitive)"""
    category = Category.query.filter(Category.name.ilike(category_name)).first()
    
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    
    return jsonify(category.to_dict(include_parent=True, include_subcategories=True))

