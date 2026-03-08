"""
CuriousBooks API - Flask Backend
Main application entry point
"""
import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import config
from limiter import limiter
from models import init_db, TokenBlocklist, db
from routes import register_routes


def create_app(config_name=None):
    """Application factory for creating Flask app instances"""
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.url_map.strict_slashes = False  # Don't redirect URLs without trailing slashes
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    CORS(app, origins=app.config.get('CORS_ORIGINS', ['http://localhost:5173']))
    jwt = JWTManager(app)
    
    # Rate limiting (default in-memory; set RATELIMIT_STORAGE_URI for Redis in production)
    limiter.init_app(app)
    app.config.setdefault('RATELIMIT_DEFAULT', '200 per hour')
    if app.config.get('RATELIMIT_STORAGE_URI'):
        limiter.storage_uri = app.config['RATELIMIT_STORAGE_URI']
    limiter.default_limits = [app.config.get('RATELIMIT_DEFAULT', '200 per hour')]
    
    # Initialize database
    init_db(app)

    # Require revoked tokens to be rejected (session hijacking prevention)
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload.get('jti')
        if not jti:
            return False
        return db.session.query(TokenBlocklist.id).filter_by(jti=jti).first() is not None
    
    # Register API routes
    register_routes(app)

    # Require API key on all /api/* when any key is configured (supports rotation via multiple keys)
    valid_api_keys = app.config.get('API_KEYS') or frozenset()
    if valid_api_keys:

        @app.before_request
        def require_api_key():
            from flask import request
            if request.path == '/' or request.path == '/api/health':
                return None
            if request.path == '/api/orders/stripe/webhook':
                return None  # Stripe calls this; verified by signature
            if request.path.startswith('/api/'):
                if request.headers.get('X-API-Key') not in valid_api_keys:
                    return jsonify({'error': 'Invalid or missing API key'}), 403
            return None

    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'CuriousBooks API',
            'version': '1.0.0'
        })
    
    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Welcome to CuriousBooks API',
            'version': '1.0.0',
            'docs': '/api/docs',
            'endpoints': {
                'books': '/api/books',
                'categories': '/api/categories',
                'auth': '/api/auth',
                'reviews': '/api/reviews',
                'orders': '/api/orders',
                'recommendations': '/api/recommendations'
            }
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400
    
    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    # Run the development server
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║           CuriousBooks API Server Starting               ║
    ╠══════════════════════════════════════════════════════════╣
    ║  Running on: http://localhost:{port}                       ║
    ║  Environment: {'development' if debug else 'production'}                           ║
    ║                                                          ║
    ║  API Endpoints:                                          ║
    ║  • GET  /api/books           - List all books            ║
    ║  • GET  /api/books/featured  - Featured books            ║
    ║  • GET  /api/books/search    - Search books              ║
    ║  • GET  /api/categories      - List categories           ║
    ║  • POST /api/auth/login      - User login                ║
    ║  • POST /api/auth/register   - User registration         ║
    ║  • POST /api/orders/checkout - Create order              ║
    ║  • GET  /api/recommendations - Get recommendations       ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    app.run(debug=debug, host="0.0.0.0", port=port)
