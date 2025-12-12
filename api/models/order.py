"""
Order and OrderItem models
"""
from datetime import datetime
from .database import db


class Order(db.Model):
    """Order model matching the database schema"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(5), nullable=False, default='USD')
    status = db.Column(db.Enum('Pending', 'Paid', 'Shipped', 'Delivered', 'Cancelled', name='order_status'), 
                       nullable=False, default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy='joined', cascade='all, delete-orphan')
    
    def calculate_total(self):
        """Recalculate total from order items"""
        self.total_amount = sum(item.subtotal for item in self.items)
        return self.total_amount
    
    def to_dict(self, include_items=True, include_user=False):
        """Convert to dictionary for API responses"""
        data = {
            'id': str(self.id),
            'userId': str(self.user_id),
            'totalAmount': float(self.total_amount) if self.total_amount else 0,
            'currency': self.currency,
            'status': self.status,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_items:
            data['items'] = [item.to_dict() for item in self.items]
        if include_user and self.user:
            data['user'] = self.user.to_dict()
        return data
    
    def __repr__(self):
        return f'<Order {self.id}>'


class OrderItem(db.Model):
    """OrderItem model matching the database schema"""
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, index=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Composite index
    __table_args__ = (
        db.Index('idx_orderitems_book', 'book_id'),
    )
    
    @property
    def subtotal(self):
        """Calculate subtotal for this item"""
        return float(self.unit_price) * self.quantity if self.unit_price else 0
    
    def to_dict(self, include_book=True):
        """Convert to dictionary for API responses"""
        data = {
            'id': str(self.id),
            'orderId': str(self.order_id),
            'bookId': str(self.book_id),
            'quantity': self.quantity,
            'unitPrice': float(self.unit_price) if self.unit_price else 0,
            'subtotal': self.subtotal
        }
        if include_book and self.book:
            data['book'] = self.book.to_dict()
        return data
    
    def __repr__(self):
        return f'<OrderItem {self.id}>'

