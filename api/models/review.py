"""
Review model
"""
from datetime import datetime
from .database import db


class Review(db.Model):
    """Review model matching the database schema"""
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False, index=True)
    rating = db.Column(db.Float, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Composite index for book reviews
    __table_args__ = (
        db.Index('idx_reviews_book', 'book_id'),
    )
    
    def to_dict(self, include_user=True, include_book=False):
        """Convert to dictionary for API responses - matches frontend Review interface"""
        data = {
            'id': str(self.id),
            'bookId': str(self.book_id),
            'rating': self.rating,
            'text': self.comment,
            'date': self.created_at.isoformat() if self.created_at else None
        }
        if include_user and self.user:
            data['reviewerName'] = self.user.username
            data['userId'] = str(self.user_id)
        if include_book and self.book:
            data['book'] = self.book.to_dict()
        return data
    
    def __repr__(self):
        return f'<Review {self.id} for Book {self.book_id}>'

