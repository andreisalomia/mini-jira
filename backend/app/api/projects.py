from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import Project, User
from ..auth import require_auth, check_project_membership

bp = Blueprint('projects', __name__, url_prefix='/api/v1/projects')


@bp.route('', methods=['GET'])
@require_auth
def list_projects():
    """List projects where user is a member (excluding soft-deleted)"""
    current_user_id = request.current_user['user_id']
    user = User.query.get(current_user_id)
    
    # Get projects where user is owner or member
    projects = Project.query.filter(
        db.and_(
            Project.is_deleted == False,
            db.or_(
                Project.owner_id == current_user_id,
                Project.members.contains(user)
            )
        )
    ).all()
    
    return jsonify([p.to_dict() for p in projects])


@bp.route('/<int:project_id>', methods=['GET'])
@require_auth
def get_project(project_id):
    """Get a specific project with members"""
    project = Project.query.get_or_404(project_id)
    current_user_id = request.current_user['user_id']
    
    if project.is_deleted:
        return jsonify({'error': 'Project not found'}), 404
    
    # Check membership
    if not check_project_membership(current_user_id, project):
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify(project.to_dict(include_members=True))


@bp.route('', methods=['POST'])
@require_auth
def create_project():
    """Create a new project (authenticated user becomes owner)"""
    data = request.get_json()
    current_user_id = request.current_user['user_id']
    
    if not data.get('name'):
        return jsonify({'error': 'Name required'}), 400
    
    owner = User.query.get(current_user_id)
    
    project = Project(
        name=data['name'],
        description=data.get('description'),
        owner_id=current_user_id
    )
    
    # Add owner as member automatically
    project.members.append(owner)
    
    db.session.add(project)
    db.session.commit()
    
    return jsonify(project.to_dict(include_members=True)), 201


@bp.route('/<int:project_id>', methods=['PUT'])
@require_auth
def update_project(project_id):
    """Update a project (owner only)"""
    project = Project.query.get_or_404(project_id)
    current_user_id = request.current_user['user_id']
    
    if project.is_deleted:
        return jsonify({'error': 'Project not found'}), 404
    
    # Only owner can update project details
    if project.owner_id != current_user_id:
        return jsonify({'error': 'Only project owner can update project'}), 403
    
    data = request.get_json()
    
    if 'name' in data:
        project.name = data['name']
    if 'description' in data:
        project.description = data['description']
    
    db.session.commit()
    return jsonify(project.to_dict())


@bp.route('/<int:project_id>', methods=['DELETE'])
@require_auth
def delete_project(project_id):
    """Soft delete a project (owner only)"""
    project = Project.query.get_or_404(project_id)
    current_user_id = request.current_user['user_id']
    
    # Only owner can delete
    if project.owner_id != current_user_id:
        return jsonify({'error': 'Only project owner can delete project'}), 403
    
    project.is_deleted = True
    db.session.commit()
    return '', 204


@bp.route('/<int:project_id>/members', methods=['POST'])
@require_auth
def add_member(project_id):
    """Add a member to a project (owner only)"""
    project = Project.query.get_or_404(project_id)
    current_user_id = request.current_user['user_id']
    
    if project.is_deleted:
        return jsonify({'error': 'Project not found'}), 404
    
    # Only owner can add members
    if project.owner_id != current_user_id:
        return jsonify({'error': 'Only project owner can add members'}), 403
    
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if user in project.members:
        return jsonify({'error': 'User already a member'}), 400
    
    project.members.append(user)
    db.session.commit()
    
    return jsonify(project.to_dict(include_members=True))


@bp.route('/<int:project_id>/members/<int:user_id>', methods=['DELETE'])
@require_auth
def remove_member(project_id, user_id):
    """Remove a member from a project (owner only)"""
    project = Project.query.get_or_404(project_id)
    current_user_id = request.current_user['user_id']
    
    # Only owner can remove members
    if project.owner_id != current_user_id:
        return jsonify({'error': 'Only project owner can remove members'}), 403
    
    user = User.query.get_or_404(user_id)
    
    if user not in project.members:
        return jsonify({'error': 'User not a member'}), 404
    
    # Don't allow removing the owner
    if project.owner_id == user_id:
        return jsonify({'error': 'Cannot remove project owner'}), 400
    
    project.members.remove(user)
    db.session.commit()
    
    return '', 204