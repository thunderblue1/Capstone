"""
CuriousBooks API - Flask Backend
Main application entry point
"""
import logging
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter.errors import RateLimitExceeded
from config import config, database_diagnostics
from limiter import limiter
from models import init_db, TokenBlocklist, db
from routes import register_routes
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from utils.ip_cooldown import (
    activate_cooldown,
    cooldown_response,
    get_active_cooldown,
    is_path_exempt,
    log_boundary_hit,
)

logger = logging.getLogger(__name__)


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
    app.config.setdefault('RATELIMIT_DEFAULT', '120 per minute;2000 per hour')
    if app.config.get('RATELIMIT_STORAGE_URI'):
        limiter.storage_uri = app.config['RATELIMIT_STORAGE_URI']
    limiter.default_limits = [app.config.get('RATELIMIT_DEFAULT', '120 per minute;2000 per hour')]

    logger.info('Database config: %s', database_diagnostics())

    # Initialize database
    init_db(app)

    # Require revoked tokens to be rejected (session hijacking prevention)
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload.get('jti')
        if not jti:
            return False
        return db.session.query(TokenBlocklist.id).filter_by(jti=jti).first() is not None

    @app.before_request
    def enforce_ip_cooldown():
        """Reject cooled-down IPs early with the same 429 + Retry-After payload."""
        if is_path_exempt():
            return None
        if not request.path.startswith('/api/'):
            return None
        row = get_active_cooldown()
        if row:
            log_boundary_hit(429, cooldown=True)
            return cooldown_response(row)
        return None
    
    # Register API routes
    register_routes(app)

    # Require API key on all /api/* when any key is configured (supports rotation via multiple keys)
    valid_api_keys = app.config.get('API_KEYS') or frozenset()
    if valid_api_keys:

        @app.before_request
        def require_api_key():
            if request.path in ('/', '/api/health', '/api/health/db'):
                return None
            if request.path == '/api/orders/stripe/webhook':
                return None  # Stripe calls this; verified by signature
            if request.path.startswith('/api/'):
                if request.headers.get('X-API-Key') not in valid_api_keys:
                    return jsonify({'error': 'Invalid or missing API key'}), 403
            return None

    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    @limiter.exempt
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'CuriousBooks API',
            'version': '1.0.0'
        })

    @app.route('/api/health/db', methods=['GET'])
    @limiter.exempt
    def health_check_db():
        info = database_diagnostics()
        try:
            db.session.execute(text('SELECT 1'))
            info['status'] = 'connected'
            return jsonify(info)
        except OperationalError as exc:
            message = str(exc.orig) if getattr(exc, 'orig', None) else str(exc)
            info['status'] = 'error'
            info['error'] = message
            if '1045' in message or 'Access denied' in message:
                info['hint'] = (
                    'Reset the TiDB password in TiDB Cloud Connect, update TIDB_PASSWORD on Render, '
                    'and allow Render outbound IPs in TiDB Cloud → Settings → Networking.'
                )
            return jsonify(info), 503
    
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
    @app.errorhandler(RateLimitExceeded)
    def rate_limit_handler(error):
        """On limiter trip: start 45-min IP cooldown and return Retry-After."""
        row = activate_cooldown(reason='rate_limit')
        log_boundary_hit(429, cooldown=False)
        return cooldown_response(row)

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
