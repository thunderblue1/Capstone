"""
Revoked JWT storage for session hijacking prevention.
When a token is revoked (logout or refresh rotation), its jti is stored here
so the token_in_blocklist_loader can reject it.
"""
from datetime import datetime, timezone
from .database import db


class TokenBlocklist(db.Model):
    """Stores revoked JWT identifiers. Checked on every protected request."""
    __tablename__ = 'token_blocklist'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    type = db.Column(db.String(16), nullable=False)  # 'access' or 'refresh'
    exp = db.Column(db.DateTime, nullable=True)  # token expiry, for optional pruning
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
