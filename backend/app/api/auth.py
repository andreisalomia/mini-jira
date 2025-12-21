from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from ..extensions import db
from ..models import User
from ..auth import generate_token, require_auth

bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')


@bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    # Validation
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    # Check if user exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    user = User(
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        role=data.get('role', 'member')
    )
    
    db.session.add(user)
    db.session.commit()
    
    # Generate token
    token = generate_token(user.id, user.email, user.role)
    
    return jsonify({
        'user': user.to_dict(),
        'token': token
    }), 201


@bp.route('/login', methods=['POST'])
def login():
    """Login and get JWT token"""
    data = request.get_json()
    
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Generate token
    token = generate_token(user.id, user.email, user.role)
    
    return jsonify({
        'user': user.to_dict(),
        'token': token
    })


@bp.route('/me', methods=['GET'])
@require_auth
def get_current_user():
    """Get current user info from token"""
    user = User.query.get(request.current_user['user_id'])
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict())