from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import Issue, Project, User, AuditLog
from ..auth import require_auth, check_project_membership
from ..workflows import validate_status_change, can_modify_issue

bp = Blueprint('issues', __name__, url_prefix='/api/v1/issues')


@bp.route('', methods=['GET'])
@require_auth
def list_issues():
    """List issues with optional filters"""
    query = Issue.query.filter_by(is_deleted=False)
    
    # Filters
    project_id = request.args.get('project_id', type=int)
    status = request.args.get('status')
    assignee_id = request.args.get('assignee_id', type=int)
    priority = request.args.get('priority')
    
    if project_id:
        query = query.filter_by(project_id=project_id)
    if status:
        query = query.filter_by(status=status)
    if assignee_id:
        query = query.filter_by(assignee_id=assignee_id)
    if priority:
        query = query.filter_by(priority=priority)
    
    # Search (intentionally using ILIKE - will be slow)
    search = request.args.get('search')
    if search:
        search_pattern = f'%{search}%'
        query = query.filter(
            db.or_(
                Issue.title.ilike(search_pattern),
                Issue.description.ilike(search_pattern)
            )
        )
    
    issues = query.order_by(Issue.created_at.desc()).all()
    return jsonify([i.to_dict() for i in issues])


@bp.route('/<int:issue_id>', methods=['GET'])
@require_auth
def get_issue(issue_id):
    """Get a specific issue with comments"""
    issue = Issue.query.get_or_404(issue_id)
    if issue.is_deleted:
        return jsonify({'error': 'Issue not found'}), 404
    
    # Check project membership
    if not check_project_membership(request.current_user['user_id'], issue.project):
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify(issue.to_dict(include_comments=True))


@bp.route('', methods=['POST'])
@require_auth
def create_issue():
    """Create a new issue"""
    data = request.get_json()
    current_user_id = request.current_user['user_id']
    
    # Validation
    required = ['title', 'project_id']
    if not all(data.get(field) for field in required):
        return jsonify({'error': f'Required fields: {", ".join(required)}'}), 400
    
    # Verify project exists
    project = Project.query.get(data['project_id'])
    if not project or project.is_deleted:
        return jsonify({'error': 'Project not found'}), 404
    
    # Check if user is a project member
    if not check_project_membership(current_user_id, project):
        return jsonify({'error': 'You must be a project member to create issues'}), 403
    
    # Verify assignee if provided and is a member
    assignee_id = data.get('assignee_id')
    if assignee_id:
        assignee = User.query.get(assignee_id)
        if not assignee:
            return jsonify({'error': 'Assignee not found'}), 404
        if not check_project_membership(assignee_id, project):
            return jsonify({'error': 'Assignee must be a project member'}), 400
    
    issue = Issue(
        title=data['title'],
        description=data.get('description'),
        project_id=data['project_id'],
        reporter_id=current_user_id,  # Use authenticated user
        assignee_id=assignee_id,
        status=data.get('status', 'OPEN'),
        priority=data.get('priority', 'MEDIUM')
    )
    
    db.session.add(issue)
    db.session.flush()  # Get the issue ID
    
    # Create audit log
    audit = AuditLog(
        issue_id=issue.id,
        user_id=current_user_id,
        action='created',
        new_value=issue.status
    )
    db.session.add(audit)
    
    db.session.commit()
    
    return jsonify(issue.to_dict()), 201


@bp.route('/<int:issue_id>', methods=['PUT'])
@require_auth
def update_issue(issue_id):
    """Update an issue with workflow validation"""
    issue = Issue.query.get_or_404(issue_id)
    
    if issue.is_deleted:
        return jsonify({'error': 'Issue not found'}), 404
    
    current_user_id = request.current_user['user_id']
    
    # Check if user can modify this issue
    if not can_modify_issue(issue, current_user_id):
        return jsonify({'error': 'You do not have permission to modify this issue'}), 403
    
    data = request.get_json()
    
    # Validate and update status with workflow rules
    if 'status' in data and data['status'] != issue.status:
        is_valid, error_msg = validate_status_change(issue, data['status'], current_user_id)
        
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        old_status = issue.status
        issue.status = data['status']
        
        # Create audit log
        audit = AuditLog(
            issue_id=issue.id,
            user_id=current_user_id,
            action='status_change',
            old_value=old_status,
            new_value=data['status']
        )
        db.session.add(audit)
    
    # Update assignee with validation
    if 'assignee_id' in data and data['assignee_id'] != issue.assignee_id:
        new_assignee_id = data['assignee_id']
        
        # Verify new assignee is a project member
        if new_assignee_id is not None:
            new_assignee = User.query.get(new_assignee_id)
            if not new_assignee:
                return jsonify({'error': 'Assignee not found'}), 404
            if not check_project_membership(new_assignee_id, issue.project):
                return jsonify({'error': 'Assignee must be a project member'}), 400
        
        old_assignee = issue.assignee_id
        issue.assignee_id = new_assignee_id
        
        # Create audit log
        audit = AuditLog(
            issue_id=issue.id,
            user_id=current_user_id,
            action='assigned',
            old_value=str(old_assignee) if old_assignee else None,
            new_value=str(new_assignee_id) if new_assignee_id else None
        )
        db.session.add(audit)
    
    # Simple field updates
    if 'title' in data:
        issue.title = data['title']
    if 'description' in data:
        issue.description = data['description']
    if 'priority' in data:
        issue.priority = data['priority']
    
    db.session.commit()
    return jsonify(issue.to_dict())


@bp.route('/<int:issue_id>', methods=['DELETE'])
@require_auth
def delete_issue(issue_id):
    """Soft delete an issue (project owner or reporter only)"""
    issue = Issue.query.get_or_404(issue_id)
    current_user_id = request.current_user['user_id']
    
    # Only project owner or reporter can delete
    if issue.project.owner_id != current_user_id and issue.reporter_id != current_user_id:
        return jsonify({'error': 'Only project owner or issue reporter can delete issues'}), 403
    
    issue.is_deleted = True
    
    # Audit log
    audit = AuditLog(
        issue_id=issue.id,
        user_id=current_user_id,
        action='deleted',
        old_value='active',
        new_value='deleted'
    )
    db.session.add(audit)
    
    db.session.commit()
    return '', 204


@bp.route('/<int:issue_id>/audit', methods=['GET'])
@require_auth
def get_audit_log(issue_id):
    """Get audit log for an issue"""
    issue = Issue.query.get_or_404(issue_id)
    
    # Check project membership
    if not check_project_membership(request.current_user['user_id'], issue.project):
        return jsonify({'error': 'Access denied'}), 403
    
    logs = AuditLog.query.filter_by(issue_id=issue_id).order_by(AuditLog.timestamp.desc()).all()
    return jsonify([log.to_dict() for log in logs])