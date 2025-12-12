"""
Category model
"""
from .database import db


class Category(db.Model):
    """Category model matching the database schema"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True, index=True)
    
    # Self-referential relationship for subcategories
    parent = db.relationship('Category', remote_side=[id], backref='subcategories')
    
    # Relationship to books
    books = db.relationship('Book', backref='category', lazy='dynamic')
    
    def to_dict(self, include_parent=False, include_subcategories=False):
        """Convert to dictionary for API responses"""
        data = {
            'id': self.id,
            'name': self.name,
            'parentId': self.parent_id
        }
        if include_parent and self.parent:
            data['parent'] = self.parent.to_dict()
        if include_subcategories:
            data['subcategories'] = [sub.to_dict() for sub in self.subcategories]
        return data
    
    def __repr__(self):
        return f'<Category {self.name}>'

