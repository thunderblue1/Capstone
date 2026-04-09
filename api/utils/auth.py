"""
Authentication and authorization utilities.

RBAC: Role is always read from the database (never from JWT or request body)
to prevent vertical privilege escalation. Resource ownership checks prevent
horizontal escalation (users can only access their own resources unless admin).
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from models import User


def _get_current_user():
    """Load current user from DB by JWT identity. Returns (user, error_response)."""
    user_id = get_jwt_identity()
    if not user_id:
        return None, (jsonify({'error': 'Authentication required'}), 401)
    user = User.query.get(user_id)
    if not user:
        return None, (jsonify({'error': 'User not found'}), 404)
    return user, None


def role_required(*roles):
    """
    Decorator to require one of the given roles. Role is read from DB only.

    Usage:
        @role_required('manager', 'admin')
        @jwt_required()
        def my_route():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user, err = _get_current_user()
            if err:
                return err
            if not user.has_role(*roles):
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """
    Decorator to require admin role. Use for user/role management, etc.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user, err = _get_current_user()
        if err:
            return err
        if not user.is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function


def product_manager_required(f):
    """
    Decorator to require role that can add/edit/delete products (manager or admin).
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user, err = _get_current_user()
        if err:
            return err
        if not user.can_add_products():
            return jsonify({'error': 'Insufficient permissions'}), 403
        return f(*args, **kwargs)
    return decorated_function


def manager_required(f):
    """
    Decorator to require manager or admin role for product operations.
    Prefer product_manager_required for clarity; this is kept for compatibility.
    """
    return product_manager_required(f)

