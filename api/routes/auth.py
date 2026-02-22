"""
Authentication API Routes Module
================================

Purpose:
    Provides REST API endpoints for user authentication and account
    management including registration, login, token refresh, and
    profile updates.

Endpoints:
    POST /api/auth/register        - Register a new user account
    POST /api/auth/login           - Authenticate and receive JWT tokens
    POST /api/auth/refresh         - Refresh expired access token
    GET  /api/auth/me              - Get current user profile
    PUT  /api/auth/me              - Update current user profile
    POST /api/auth/change-password - Change user password
    POST /api/auth/logout          - Revoke current token(s); send refreshToken in body to revoke both

Authentication:
    Uses JWT (JSON Web Tokens) with access and refresh token pattern.
    Access tokens expire in 15 minutes, refresh tokens in 30 days.
    Protected routes require Bearer token in Authorization header.

Usage:
    This blueprint is registered in routes/__init__.py and mounted
    at /api/auth. Tokens should be stored client-side (localStorage).

Dependencies:
    - Flask-JWT-Extended for token management
    - Werkzeug for password hashing (via User model)
    - models.User for user data access
"""
from datetime import datetime, timezone
import jwt as pyjwt
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from limiter import limiter
from models import db, User, TokenBlocklist

auth_bp = Blueprint('auth', __name__)

# Stricter rate limit for auth (brute-force protection)
def _auth_limit():
    return current_app.config.get('RATELIMIT_AUTH', '5 per minute')


def _revoke_token(jti: str, token_type: str, exp=None):
    """Add token jti to blocklist so it can no longer be used."""
    db.session.add(TokenBlocklist(jti=jti, type=token_type, exp=exp))
    db.session.commit()


@auth_bp.route('/register', methods=['POST'])
@limiter.limit(_auth_limit)
def register():
    """Register a new user"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Required fields
    required = ['email', 'password', 'username']
    for field in required:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Check if email or username already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already taken'}), 409
    
    # Create new user
    user = User(
        email=data['email'],
        username=data['username'],
        first_name=data.get('firstName'),
        last_name=data.get('lastName')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    # Generate tokens
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict(include_email=True),
        'accessToken': access_token,
        'refreshToken': refresh_token
    }), 201


@auth_bp.route('/login', methods=['POST'])
@limiter.limit(_auth_limit)
def login():
    """Login with email and password"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    # Find user by email
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Generate tokens
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(include_email=True),
        'accessToken': access_token,
        'refreshToken': refresh_token
    })


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token and rotate refresh token (old refresh token is revoked)."""
    identity = get_jwt_identity()
    old_refresh = get_jwt()
    old_jti = old_refresh.get('jti')
    old_exp = old_refresh.get('exp')
    exp_dt = datetime.fromtimestamp(old_exp, tz=timezone.utc) if old_exp else None

    access_token = create_access_token(identity=identity)
    new_refresh_token = create_refresh_token(identity=identity)

    if old_jti:
        _revoke_token(old_jti, 'refresh', exp=exp_dt)

    return jsonify({
        'accessToken': access_token,
        'refreshToken': new_refresh_token
    })


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user info"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict(include_email=True))


@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_current_user():
    """Update current user info"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Update allowed fields
    if 'firstName' in data:
        user.first_name = data['firstName']
    if 'lastName' in data:
        user.last_name = data['lastName']
    if 'username' in data:
        # Check if username is taken
        existing = User.query.filter_by(username=data['username']).first()
        if existing and existing.id != user.id:
            return jsonify({'error': 'Username already taken'}), 409
        user.username = data['username']
    
    db.session.commit()
    
    return jsonify({
        'message': 'User updated successfully',
        'user': user.to_dict(include_email=True)
    })


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change password for current user"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    current_password = data.get('currentPassword')
    new_password = data.get('newPassword')
    
    if not current_password or not new_password:
        return jsonify({'error': 'Current and new password are required'}), 400
    
    if not user.check_password(current_password):
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    user.set_password(new_password)
    db.session.commit()
    
    return jsonify({'message': 'Password changed successfully'})


@auth_bp.route('/logout', methods=['POST'])
@jwt_required(verify_type=False)
def logout():
    """
    Revoke the token in the Authorization header.
    Optionally send { "refreshToken": "..." } in body to revoke the refresh token as well,
    so both tokens are invalidated in one call.
    """
    token = get_jwt()
    jti = token.get('jti')
    ttype = token.get('type', 'access')
    exp = token.get('exp')
    exp_dt = datetime.fromtimestamp(exp, tz=timezone.utc) if exp else None

    if jti:
        _revoke_token(jti, ttype, exp=exp_dt)

    data = request.get_json() or {}
    refresh_token_raw = data.get('refreshToken')
    if refresh_token_raw:
        try:
            secret = current_app.config['JWT_SECRET_KEY']
            payload = pyjwt.decode(
                refresh_token_raw,
                secret,
                algorithms=['HS256'],
                options={'verify_exp': False}
            )
            ref_jti = payload.get('jti')
            ref_exp = payload.get('exp')
            ref_exp_dt = datetime.fromtimestamp(ref_exp, tz=timezone.utc) if ref_exp else None
            if ref_jti:
                _revoke_token(ref_jti, 'refresh', exp=ref_exp_dt)
        except Exception:
            pass

    return jsonify({'message': 'Logged out successfully'})

