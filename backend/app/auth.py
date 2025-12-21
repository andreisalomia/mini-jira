import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from .models import User


def generate_token(user_id, email, role):
    """Generate JWT token"""
    payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')


def decode_token(token):
    """Decode JWT token"""
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_current_user():
    """Extract current user from Authorization header"""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        return None
    
    try:
        # Format: "Bearer <token>"
        token = auth_header.split(' ')[1]
        payload = decode_token(token)
        
        if not payload:
            return None
        
        return {
            'user_id': payload['user_id'],
            'email': payload['email'],
            'role': payload['role']
        }
    except (IndexError, KeyError):
        return None


def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = get_current_user()
        
        if not current_user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Inject current_user into request context
        request.current_user = current_user
        return f(*args, **kwargs)
    
    return decorated_function


def require_admin(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = get_current_user()
        
        if not current_user:
            return jsonify({'error': 'Authentication required'}), 401
        
        if current_user['role'] != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        request.current_user = current_user
        return f(*args, **kwargs)
    
    return decorated_function


def check_project_membership(user_id, project):
    """Check if user is a member of the project"""
    from .models import User
    user = User.query.get(user_id)
    return user in project.members or project.owner_id == user_id