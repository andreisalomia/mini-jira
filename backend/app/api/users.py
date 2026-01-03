import logging
from flask import Blueprint, request, jsonify, g
from werkzeug.security import generate_password_hash
from ..extensions import db
from ..models import User
from ..auth import require_auth, require_admin

bp = Blueprint('users', __name__, url_prefix='/api/v1/users')
logger = logging.getLogger(__name__)


@bp.route('', methods=['GET'])
@require_auth
def list_users():
    """List all users"""
    users = User.query.all()
    logger.info(
        'users.list',
        extra={
            'request_id': getattr(g, 'request_id', None),
            'user_id': request.current_user['user_id'],
            'user_count': len(users)
        }
    )
    return jsonify([u.to_dict() for u in users])


@bp.route('/<int:user_id>', methods=['GET'])
@require_auth
def get_user(user_id):
    """Get a specific user"""
    user = User.query.get_or_404(user_id)
    logger.info(
        'users.get',
        extra={
            'request_id': getattr(g, 'request_id', None),
            'user_id': request.current_user['user_id'],
            'target_user_id': user_id
        }
    )
    return jsonify(user.to_dict())


@bp.route('/<int:user_id>', methods=['PUT'])
@require_auth
def update_user(user_id):
    """Update a user (self or admin only)"""
    user = User.query.get_or_404(user_id)
    current_user = request.current_user
    
    # Users can only update themselves unless admin
    if current_user['user_id'] != user_id and current_user['role'] != 'admin':
        logger.warning(
            'users.update.access_denied',
            extra={
                'request_id': getattr(g, 'request_id', None),
                'user_id': current_user['user_id'],
                'target_user_id': user_id
            }
        )
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json() or {}
    updated_fields = []
    
    if 'email' in data:
        # Check if new email is taken
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user_id:
            logger.info(
                'users.update.duplicate_email',
                extra={
                    'request_id': getattr(g, 'request_id', None),
                    'user_id': current_user['user_id'],
                    'target_user_id': user_id,
                    'email': data['email']
                }
            )
            return jsonify({'error': 'Email already exists'}), 400
        user.email = data['email']
        updated_fields.append('email')
    
    # Only admins can change roles
    if 'role' in data:
        if current_user['role'] != 'admin':
            logger.warning(
                'users.update.role_denied',
                extra={
                    'request_id': getattr(g, 'request_id', None),
                    'user_id': current_user['user_id'],
                    'target_user_id': user_id,
                    'attempted_role': data.get('role')
                }
            )
            return jsonify({'error': 'Only admins can change roles'}), 403
        user.role = data['role']
        updated_fields.append('role')
    
    if 'password' in data:
        user.password_hash = generate_password_hash(data['password'])
        updated_fields.append('password')
    
    db.session.commit()
    logger.info(
        'users.update.success',
        extra={
            'request_id': getattr(g, 'request_id', None),
            'user_id': current_user['user_id'],
            'target_user_id': user_id,
            'updated_fields': updated_fields
        }
    )
    return jsonify(user.to_dict())


@bp.route('/<int:user_id>', methods=['DELETE'])
@require_admin
def delete_user(user_id):
    """Delete a user (admin only, hard delete)"""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    logger.info(
        'users.delete.success',
        extra={
            'request_id': getattr(g, 'request_id', None),
            'user_id': request.current_user['user_id'],
            'target_user_id': user_id
        }
    )
    return '', 204
