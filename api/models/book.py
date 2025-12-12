"""
Book model
"""
from datetime import datetime
from .database import db


class Book(db.Model):
    """Book model matching the database schema"""
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    author = db.Column(db.String(255), nullable=False, index=True)
    isbn_13 = db.Column(db.String(13), unique=True, nullable=False, index=True)
    publisher = db.Column(db.String(255), nullable=True)
    publication_date = db.Column(db.Date, nullable=True)
    language = db.Column(db.String(10), nullable=True, default='en')
    genre = db.Column(db.String(100), nullable=True, index=True)
    description = db.Column(db.Text, nullable=True)
    page_count = db.Column(db.Integer, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(5), nullable=False, default='USD')
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    cover_image_url = db.Column(db.String(500), nullable=True)
    popularity_score = db.Column(db.Float, nullable=True, default=0)
    average_rating = db.Column(db.Float, nullable=True, default=0)
    review_count = db.Column(db.Integer, nullable=True, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reviews = db.relationship('Review', backref='book', lazy='dynamic')
    order_items = db.relationship('OrderItem', backref='book', lazy='dynamic')
    
    def to_dict(self, include_category=False):
        """Convert to dictionary for API responses - matches frontend Book interface"""
        data = {
            'id': str(self.id),
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn_13,
            'publisher': self.publisher,
            'publicationDate': self.publication_date.isoformat() if self.publication_date else None,
            'language': self.language,
            'genre': self.genre,
            'description': self.description,
            'pageCount': self.page_count,
            'price': float(self.price) if self.price else 0,
            'currency': self.currency,
            'stockQuantity': self.stock_quantity,
            'imageUrl': self.cover_image_url or '/images/default-book.jpg',
            'averageRating': self.average_rating or 0,
            'reviewCount': self.review_count or 0,
            'popularityScore': self.popularity_score or 0,
            'categoryId': self.category_id,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_category and self.category:
            data['category'] = self.category.to_dict()
        return data
    
    def update_rating_stats(self):
        """Recalculate average rating and review count from reviews"""
        reviews = self.reviews.all()
        if reviews:
            self.review_count = len(reviews)
            self.average_rating = sum(r.rating for r in reviews) / len(reviews)
        else:
            self.review_count = 0
            self.average_rating = 0
    
    def __repr__(self):
        return f'<Book {self.title}>'

