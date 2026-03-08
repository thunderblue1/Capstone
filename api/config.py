"""
Configuration settings for the CuriousBooks API
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'curious-books-secret-key-change-in-production'
    
    # Database
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'curiousbooks')
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
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


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

