"""
Database initialization and configuration
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError

db = SQLAlchemy()

_ACCESS_DENIED_HINT = (
    'TiDB/MySQL access denied (1045). Checklist:\n'
    '  1. TiDB Cloud → Connect → Reset Password, copy the NEW password immediately.\n'
    '  2. Render → set TIDB_DATABASE_URL with the full mysql:// connection string.\n'
    '  3. TiDB Cloud → Settings → Networking → enable Public Endpoint / allow Render IPs.\n'
    '  4. Confirm the host in TIDB_DATABASE_URL matches the TiDB Connect dialog.'
)

_LOCALHOST_HINT = (
    'Cannot connect to MySQL on localhost. On Render, set TIDB_DATABASE_URL in the dashboard '
    '(the api/.env file is not deployed). Example:\n'
    '  TIDB_DATABASE_URL=mysql://4CzX2YavwHHzQ2f.root:password@gateway01.us-west-2.prod.aws.tidbcloud.com:4000/curious_books\n'
    '  TIDB_ENABLE_SSL=true'
)


def init_db(app):
    """Initialize the database with the Flask app"""
    db.init_app(app)

    with app.app_context():
        from . import User, Book, Category, Review, Order, OrderItem, TokenBlocklist

        try:
            db.create_all()
        except OperationalError as exc:
            message = str(exc.orig) if getattr(exc, 'orig', None) else str(exc)
            if '1045' in message or 'Access denied' in message:
                raise RuntimeError(f'{_ACCESS_DENIED_HINT}\n\nOriginal error: {message}') from exc
            if '2003' in message and 'localhost' in message:
                raise RuntimeError(f'{_LOCALHOST_HINT}\n\nOriginal error: {message}') from exc
            raise

    return db
