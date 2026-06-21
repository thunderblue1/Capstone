"""
Configuration settings for the CuriousBooks API
"""
import os
import tempfile
from datetime import timedelta
from urllib.parse import urlparse

from dotenv import load_dotenv
from sqlalchemy.engine import URL

# Load environment variables from .env file
load_dotenv()

_CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_TIDB_CA = os.path.join(_CONFIG_DIR, 'certs', 'isrgrootx1.pem')
_TIDB_HOST_SUFFIX = '.tidbcloud.com'


def _env(*names, default=''):
    """Return the first non-empty environment variable from names."""
    for name in names:
        value = os.environ.get(name)
        if value is not None and str(value).strip():
            return str(value).strip()
    return default


def _env_bool(*names, default=False):
    raw = _env(*names)
    if not raw:
        return default
    return raw.lower() in ('1', 'true', 'yes', 'on')


def _database_host():
    """Resolve database host from env vars or DATABASE_URL."""
    host = _env('DB_HOST', 'TIDB_HOST')
    if host:
        return host
    database_url = _env('DATABASE_URL')
    if database_url:
        parsed = urlparse(database_url)
        return parsed.hostname or ''
    return 'localhost'


def _database_username():
    """Resolve database username from env vars or DATABASE_URL."""
    user = _env('DB_USER', 'TIDB_USER')
    if user:
        return user
    database_url = _env('DATABASE_URL')
    if database_url:
        parsed = urlparse(database_url)
        return (parsed.username or '').strip()
    return 'root'


def _database_password():
    return _env('DB_PASSWORD', 'TIDB_PASSWORD')


def _database_name():
    return _env('DB_NAME', 'TIDB_DB_NAME', default='curiousbooks')


def _database_port():
    return int(_env('DB_PORT', 'TIDB_PORT', default='3306'))


def _validate_tidb_credentials():
    """Fail fast with a clear message when TiDB Cloud username format is wrong."""
    if not _requires_tidb_tls():
        return
    username = _database_username()
    if username and '.' in username:
        return
    raise ValueError(
        'TiDB Cloud requires a prefixed username such as "4CzX2YavwHHzQ2f.root", '
        f'not "{username or "(empty)"}". '
        'Set TIDB_USER (or DB_USER) to the full USERNAME from the TiDB Cloud Connect dialog. '
        'If you use DATABASE_URL instead, include the prefixed username there too. '
        'See https://docs.pingcap.com/tidbcloud/select-cluster-tier#user-name-prefix'
    )


def _requires_tidb_tls():
    return _database_host().endswith(_TIDB_HOST_SUFFIX)


def _ssl_enabled():
    if _env_bool('TIDB_ENABLE_SSL'):
        return True
    if _requires_tidb_tls():
        return True
    return bool(_env('DB_SSL_CA', 'TIDB_CA_PATH', 'CA_PATH'))


def _resolve_ssl_ca_path(raw):
    """Return a filesystem path to the CA cert (file path, PEM content, or bundled default)."""
    if raw.startswith('-----BEGIN'):
        fd, path = tempfile.mkstemp(prefix='tidb-ca-', suffix='.pem')
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            handle.write(raw)
        return path
    if os.path.isabs(raw):
        return raw
    return os.path.normpath(os.path.join(_CONFIG_DIR, raw))


def _ssl_ca_path():
    """Path to CA cert for TLS (TiDB Cloud)."""
    if not _ssl_enabled():
        return ''
    raw = _env('DB_SSL_CA', 'TIDB_CA_PATH', 'CA_PATH')
    if raw:
        resolved = _resolve_ssl_ca_path(raw)
        if os.path.isfile(resolved):
            return resolved
    if os.path.isfile(_DEFAULT_TIDB_CA):
        return _DEFAULT_TIDB_CA
    return ''


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


def _has_explicit_db_config():
    return all([
        _env('DB_HOST', 'TIDB_HOST'),
        _env('DB_USER', 'TIDB_USER'),
        _env('DB_PASSWORD', 'TIDB_PASSWORD'),
        _env('DB_NAME', 'TIDB_DB_NAME'),
    ])


def _build_database_uri():
    # Prefer explicit DB/TIDB vars — avoids a stale DATABASE_URL overriding settings.
    if _has_explicit_db_config():
        return str(URL.create(
            drivername='mysql+pymysql',
            username=_database_username(),
            password=_database_password(),
            host=_database_host(),
            port=_database_port(),
            database=_database_name(),
        ))
    if _env('DATABASE_URL'):
        return _env('DATABASE_URL')
    return str(URL.create(
        drivername='mysql+pymysql',
        username=_database_username(),
        password=_database_password(),
        host=_database_host(),
        port=_database_port(),
        database=_database_name(),
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
    
    # Database (supports DB_* and TIDB_* env var names)
    DB_HOST = _database_host()
    DB_PORT = str(_database_port())
    DB_USER = _database_username()
    DB_PASSWORD = _database_password()
    DB_NAME = _database_name()
    DB_SSL_CA = _ssl_ca_path()

    _validate_tidb_credentials()
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

