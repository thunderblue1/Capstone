"""
Configuration settings for the CuriousBooks API
"""
import os
from datetime import timedelta
from dotenv import load_dotenv
from sqlalchemy.engine import URL

# Load environment variables from .env file
load_dotenv()

_CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))


def _ssl_ca_path():
    """Path to CA cert for TLS (TiDB Cloud). Accepts DB_SSL_CA or CA_PATH."""
    raw = (os.environ.get('DB_SSL_CA') or os.environ.get('CA_PATH') or '').strip()
    if not raw:
        return ''
    if os.path.isabs(raw):
        return raw
    return os.path.normpath(os.path.join(_CONFIG_DIR, raw))


def _database_connect_args():
    """PyMySQL TLS options when a CA certificate path is configured."""
    ca_path = _ssl_ca_path()
    if not ca_path:
        return {}
    return {
        'ssl_verify_cert': True,
        'ssl_verify_identity': True,
        'ssl_ca': ca_path,
    }


def _build_database_uri():
    if os.environ.get('DATABASE_URL'):
        return os.environ.get('DATABASE_URL')
    return str(URL.create(
        drivername='mysql+pymysql',
        username=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASSWORD', ''),
        host=os.environ.get('DB_HOST', 'localhost'),
        port=int(os.environ.get('DB_PORT', '3306')),
        database=os.environ.get('DB_NAME', 'curiousbooks'),
    ))


def _build_engine_options():
    connect_args = _database_connect_args()
    if not connect_args:
        return {}
    return {
        'connect_args': connect_args,
        'pool_recycle': 300,  # TiDB Cloud closes idle connections
    }


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'curious-books-secret-key-change-in-production'
    
    # Database
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'curiousbooks')
    DB_SSL_CA = _ssl_ca_path()

    SQLALCHEMY_DATABASE_URI = _build_database_uri()
    SQLALCHEMY_ENGINE_OPTIONS = _build_engine_options()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Settings (longer = less frequent re-login; override with JWT_ACCESS_HOURS, JWT_REFRESH_DAYS)
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.environ.get('JWT_ACCESS_HOURS', 24)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.environ.get('JWT_REFRESH_DAYS', 60)))
    
    # API key(s) for /api/* (optional). When non-empty, requests must send X-API-Key matching one value.
    # - API_KEYS: comma-separated list (e.g. "newkey,oldkey") for rotation; all are accepted.
    # - API_KEY: single key; used if API_KEYS is not set (backward compatible).
    _api_keys_raw = os.environ.get('API_KEYS', '').strip()
    if _api_keys_raw:
        API_KEYS = frozenset(k.strip() for k in _api_keys_raw.split(',') if k.strip())
    else:
        _single = os.environ.get('API_KEY', '').strip()
        API_KEYS = frozenset({_single}) if _single else frozenset()
    # Legacy: single key for clients that read API_KEY (e.g. first of set, or original single key)
    API_KEY = next(iter(API_KEYS), '')

    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5173,http://localhost:3000').split(',')
    
    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # Recommender Service
    RECOMMENDER_ENABLED = os.environ.get('RECOMMENDER_ENABLED', 'false').lower() == 'true'
    RECOMMENDER_MODEL_PATH = os.environ.get('RECOMMENDER_MODEL_PATH', 'models/recommender')
    
    # Rate limiting (default: 200/hour per IP; auth endpoints have stricter limits)
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', '200 per hour')
    RATELIMIT_STORAGE_URI = os.environ.get('RATELIMIT_STORAGE_URI', '')  # e.g. redis:// for production
    RATELIMIT_AUTH = os.environ.get('RATELIMIT_AUTH', '5 per minute')  # login, register

    # Stripe Configuration
    # Default to test keys for development - override with .env file in production
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', 'pk_test_51ShmmmKTQjdI7MuphPr7dXH7LtoHmO5LZxgYam9dJaIsgoi9DurxSo2peJ1ZGMMH9sSHdFcIxQ6OvKCRz4RPoDbs00pjQBAbfZ')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_51ShmmmKTQjdI7MupENFcBi5BsxFOEtA7eJxJaPfN3YP11LcjpLA9BMnCxkhxApE7pVSQF44TDAm7cNDD3lAPxnUR00RKHnDpdK')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', None)


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ENGINE_OPTIONS = {}


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

