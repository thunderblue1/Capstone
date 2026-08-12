"""
IP cooldown helpers for temporary denial after rate-limit trips.

Cooldown is idempotent: the first 429 sets a fixed expiry; further hits
return the same remaining window and do not extend it.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from flask import current_app, jsonify, request

from models import IpCooldown, db

logger = logging.getLogger(__name__)

# Paths that must remain reachable during cooldown (ops + payment webhooks)
_COOLDOWN_EXEMPT_PATHS = frozenset({
    '/',
    '/api/health',
    '/api/health/db',
    '/api/orders/stripe/webhook',
})


def client_ip() -> str:
    """Best-effort client IP (honors first X-Forwarded-For hop when present)."""
    forwarded = request.headers.get('X-Forwarded-For', '')
    if forwarded:
        return forwarded.split(',')[0].strip() or (request.remote_addr or 'unknown')
    return request.remote_addr or 'unknown'


def _as_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def remaining_seconds(blocked_until: datetime) -> int:
    delta = _as_utc(blocked_until) - datetime.now(timezone.utc)
    return max(0, int(delta.total_seconds()))


def get_active_cooldown(ip: str | None = None) -> IpCooldown | None:
    ip = ip or client_ip()
    row = IpCooldown.query.filter_by(ip_address=ip).first()
    if not row:
        return None
    if remaining_seconds(row.blocked_until) <= 0:
        db.session.delete(row)
        db.session.commit()
        return None
    return row


def is_path_exempt(path: str | None = None) -> bool:
    path = path if path is not None else request.path
    return path in _COOLDOWN_EXEMPT_PATHS


def activate_cooldown(ip: str | None = None, reason: str = 'rate_limit') -> IpCooldown:
    """
    Place IP on cooldown if not already active.
    Does not extend an existing cooldown (idempotent denial window).
    """
    ip = ip or client_ip()
    existing = get_active_cooldown(ip)
    if existing:
        return existing

    minutes = int(current_app.config.get('IP_COOLDOWN_MINUTES', 45))
    blocked_until = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    row = IpCooldown.query.filter_by(ip_address=ip).first()
    if row:
        row.blocked_until = blocked_until
        row.reason = reason
        row.created_at = datetime.now(timezone.utc)
    else:
        row = IpCooldown(
            ip_address=ip,
            blocked_until=blocked_until,
            reason=reason,
        )
        db.session.add(row)
    db.session.commit()

    logger.warning(
        'IP cooldown activated',
        extra={
            'event': 'IP_COOLDOWN',
            'ip': ip,
            'path': request.path,
            'method': request.method,
            'reason': reason,
            'blocked_until': blocked_until.isoformat(),
            'retry_after_seconds': remaining_seconds(blocked_until),
        },
    )
    return row


def cooldown_response(row: IpCooldown):
    """Standard 429 body + Retry-After for temporary denial (no extra endpoints)."""
    seconds = remaining_seconds(row.blocked_until)
    body = {
        'error': 'Too many requests. Access temporarily limited. Please try again later.',
        'retryAfterSeconds': seconds,
    }
    response = jsonify(body)
    response.status_code = 429
    response.headers['Retry-After'] = str(seconds)
    return response


def log_boundary_hit(status: int, *, cooldown: bool = False):
    """Log when a client hits a rate or cooldown boundary."""
    logger.warning(
        'Rate boundary hit',
        extra={
            'event': 'RATE_BOUNDARY',
            'ip': client_ip(),
            'path': request.path,
            'method': request.method,
            'status': status,
            'cooldown': cooldown,
        },
    )
