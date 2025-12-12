"""
Database initialization and configuration
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    """Initialize the database with the Flask app"""
    db.init_app(app)
    
    with app.app_context():
        # Import all models to register them
        from . import User, Book, Category, Review, Order, OrderItem
        
        # Create tables if they don't exist
        db.create_all()
    
    return db

