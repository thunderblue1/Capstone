"""
Authentication and authorization utilities
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from models import User


def role_required(*roles):
    """
    Decorator to require specific role(s) for a route.
    
    Usage:
        @role_required('manager', 'admin')
        @jwt_required()
        def my_route():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = get_jwt_identity()
            if not user_id:
                return jsonify({'error': 'Authentication required'}), 401
            
            user = User.query.get(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            if not user.has_role(*roles):
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def manager_required(f):
    """
    Decorator to require manager role for a route.
    
    Usage:
        @manager_required
        @jwt_required()
        def my_route():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user.is_manager():
            return jsonify({'error': 'Manager access required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

