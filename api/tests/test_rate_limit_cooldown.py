"""Rate limit trip activates a fixed 45-minute IP cooldown with Retry-After."""
import os

os.environ.setdefault('FLASK_ENV', 'testing')

import pytest

from App import create_app
from limiter import limiter
from models import IpCooldown, db
from utils.ip_cooldown import remaining_seconds


@pytest.fixture
def limited_app():
    """App with rate limiting enabled at init (required for Flask-Limiter storage)."""
    application = create_app('testing_with_rate_limit')
    with application.app_context():
        db.drop_all()
        db.create_all()
    yield application
    limiter.enabled = False


@pytest.fixture
def limited_client(limited_app):
    return limited_app.test_client()


def test_rate_limit_activates_cooldown_with_retry_after(limited_client, limited_app):
    payload = {'email': 'nobody@example.com', 'password': 'wrong'}

    assert limited_client.post('/api/auth/login', json=payload).status_code == 401
    assert limited_client.post('/api/auth/login', json=payload).status_code == 401

    blocked = limited_client.post('/api/auth/login', json=payload)
    assert blocked.status_code == 429
    data = blocked.get_json()
    assert 'retryAfterSeconds' in data
    assert data['retryAfterSeconds'] > 0
    assert blocked.headers.get('Retry-After') == str(data['retryAfterSeconds'])

    with limited_app.app_context():
        row = IpCooldown.query.filter_by(ip_address='127.0.0.1').first()
        assert row is not None
        assert remaining_seconds(row.blocked_until) > 40 * 60

    # Cooldown is idempotent: further hits do not extend, same denial shape
    again = limited_client.get('/api/books/')
    assert again.status_code == 429
    again_data = again.get_json()
    assert again_data['retryAfterSeconds'] <= data['retryAfterSeconds']
    assert 'temporarily limited' in again_data['error'].lower()

    # Health stays reachable during cooldown
    assert limited_client.get('/api/health').status_code == 200
