"""
API Routes for CuriousBooks
"""
from .books import books_bp
from .categories import categories_bp
from .auth import auth_bp
from .reviews import reviews_bp
from .orders import orders_bp
from .recommendations import recommendations_bp


def register_routes(app):
    """Register all blueprints with the Flask app"""
    app.register_blueprint(books_bp, url_prefix='/api/books')
    app.register_blueprint(categories_bp, url_prefix='/api/categories')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(reviews_bp, url_prefix='/api/reviews')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(recommendations_bp, url_prefix='/api/recommendations')


__all__ = [
    'register_routes',
    'books_bp',
    'categories_bp', 
    'auth_bp',
    'reviews_bp',
    'orders_bp',
    'recommendations_bp'
]

