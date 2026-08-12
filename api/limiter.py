"""
Rate limiter for API endpoints.
Import this in route modules and use @limiter.limit() on sensitive routes.
"""
from flask import current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


def _key_func():
    """Prefer first X-Forwarded-For hop when behind a proxy; else remote addr."""
    from flask import request

    forwarded = request.headers.get('X-Forwarded-For', '')
    if forwarded:
        return forwarded.split(',')[0].strip() or get_remote_address()
    return get_remote_address()


limiter = Limiter(key_func=_key_func)


def auth_limit():
    """Strict limit for login/register/change-password (anti-cracking)."""
    return current_app.config.get('RATELIMIT_AUTH', '5 per minute')


def authenticated_limit():
    """Generous limit for authenticated CRUD / write endpoints."""
    return current_app.config.get('RATELIMIT_AUTHENTICATED', '60 per minute')
