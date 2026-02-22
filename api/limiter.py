"""
Rate limiter for API endpoints.
Import this in route modules and use @limiter.limit() on sensitive routes.
"""
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
