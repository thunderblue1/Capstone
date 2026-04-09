"""
User model
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .database import db

# Use constants so role is never taken from client input
try:
    from constants.roles import CUSTOMER, MANAGER, ADMIN, PRODUCT_MANAGER_ROLES
except ImportError:
    CUSTOMER, MANAGER, ADMIN = 'customer', 'manager', 'admin'
    PRODUCT_MANAGER_ROLES = (MANAGER, ADMIN)


class User(db.Model):
    """User model matching the database schema"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(255), nullable=True)
    last_name = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(50), nullable=False, default=CUSTOMER)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', backref='user', lazy='dynamic')
    reviews = db.relationship('Review', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_email=False):
        """Convert to dictionary for API responses"""
        data = {
            'id': self.id,
            'username': self.username,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'role': self.role,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }
        if include_email:
            data['email'] = self.email
        return data
    
    def has_role(self, *roles):
        """Check if user has any of the specified roles (role from DB only)"""
        return self.role in roles

    def is_admin(self):
        """Check if user is an admin"""
        return self.role == ADMIN

    def can_add_products(self):
        """Check if user can add/edit/delete products (manager or admin)"""
        return self.role in PRODUCT_MANAGER_ROLES

    def is_manager(self):
        """Check if user is a manager (can add products)"""
        return self.role == MANAGER
    
    def __repr__(self):
        return f'<User {self.username}>'

