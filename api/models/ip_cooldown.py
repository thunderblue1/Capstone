"""
Temporary IP cooldown after rate-limit violations.
Fixed expiry from first trip; repeated hits do not extend the window.
"""
from datetime import datetime, timezone
from .database import db


class IpCooldown(db.Model):
    """Stores IPs temporarily denied after exceeding rate limits."""
    __tablename__ = 'ip_cooldown'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ip_address = db.Column(db.String(45), nullable=False, unique=True, index=True)
    blocked_until = db.Column(db.DateTime, nullable=False, index=True)
    reason = db.Column(db.String(64), nullable=False, default='rate_limit')
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
