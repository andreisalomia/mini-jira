"""
Workflow rules and state transitions for issues
"""

# Valid status transitions
VALID_TRANSITIONS = {
    'OPEN': ['IN_PROGRESS'],
    'IN_PROGRESS': ['DONE', 'OPEN'],
    'DONE': ['IN_PROGRESS']  # Allow reopening
}


def can_transition(from_status, to_status):
    """Check if a status transition is valid"""
    if from_status == to_status:
        return True
    return to_status in VALID_TRANSITIONS.get(from_status, [])


def can_move_to_done(issue, user_id):
    """
    Business rule: Only assignees can move issues to DONE
    """
    if issue.status == 'DONE':
        return True  # Already done
    
    if issue.assignee_id is None:
        return False  # Unassigned issues can't be closed
    
    return issue.assignee_id == user_id


def can_comment_on_issue(issue, user_id):
    """
    Business rule: Only project members can comment
    """
    from .models import User
    user = User.query.get(user_id)
    
    if not user:
        return False
    
    # Check if user is a project member or owner
    return user in issue.project.members or issue.project.owner_id == user_id


def can_modify_issue(issue, user_id):
    """
    Check if user can modify an issue
    - Project members can modify
    - Assignee can always modify
    - Reporter can always modify
    """
    if issue.assignee_id == user_id or issue.reporter_id == user_id:
        return True
    
    from .models import User
    user = User.query.get(user_id)
    
    if not user:
        return False
    
    return user in issue.project.members or issue.project.owner_id == user_id


def validate_status_change(issue, new_status, user_id):
    """
    Validate a status change request
    Returns (is_valid, error_message)
    """
    # Check if transition is valid
    if not can_transition(issue.status, new_status):
        return False, f"Invalid transition from {issue.status} to {new_status}"
    
    # Special rule for moving to DONE
    if new_status == 'DONE' and not can_move_to_done(issue, user_id):
        return False, "Only the assignee can move an issue to DONE"
    
    return True, None