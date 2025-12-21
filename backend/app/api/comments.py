from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import Comment, Issue, User
from ..auth import require_auth
from ..workflows import can_comment_on_issue

bp = Blueprint('comments', __name__, url_prefix='/api/v1/comments')


@bp.route('', methods=['POST'])
@require_auth
def create_comment():
    """Create a new comment on an issue (project members only)"""
    data = request.get_json()
    current_user_id = request.current_user['user_id']
    
    # Validation
    if not all([data.get('content'), data.get('issue_id')]):
        return jsonify({'error': 'content and issue_id required'}), 400
    
    # Verify issue exists
    issue = Issue.query.get(data['issue_id'])
    if not issue or issue.is_deleted:
        return jsonify({'error': 'Issue not found'}), 404
    
    # Check if user can comment (must be project member)
    if not can_comment_on_issue(issue, current_user_id):
        return jsonify({'error': 'Only project members can comment on issues'}), 403
    
    comment = Comment(
        content=data['content'],
        issue_id=data['issue_id'],
        author_id=current_user_id  # Use authenticated user
    )
    
    db.session.add(comment)
    db.session.commit()
    
    return jsonify(comment.to_dict()), 201


@bp.route('/<int:comment_id>', methods=['GET'])
@require_auth
def get_comment(comment_id):
    """Get a specific comment"""
    comment = Comment.query.get_or_404(comment_id)
    if comment.is_deleted:
        return jsonify({'error': 'Comment not found'}), 404
    return jsonify(comment.to_dict())


@bp.route('/<int:comment_id>', methods=['PUT'])
@require_auth
def update_comment(comment_id):
    """Update a comment (author only)"""
    comment = Comment.query.get_or_404(comment_id)
    current_user_id = request.current_user['user_id']
    
    if comment.is_deleted:
        return jsonify({'error': 'Comment not found'}), 404
    
    # Only author can edit
    if comment.author_id != current_user_id:
        return jsonify({'error': 'You can only edit your own comments'}), 403
    
    data = request.get_json()
    
    if 'content' in data:
        comment.content = data['content']
    
    db.session.commit()
    return jsonify(comment.to_dict())


@bp.route('/<int:comment_id>', methods=['DELETE'])
@require_auth
def delete_comment(comment_id):
    """Soft delete a comment (author only)"""
    comment = Comment.query.get_or_404(comment_id)
    current_user_id = request.current_user['user_id']
    
    # Only author can delete
    if comment.author_id != current_user_id:
        return jsonify({'error': 'You can only delete your own comments'}), 403
    
    comment.is_deleted = True
    db.session.commit()
    return '', 204