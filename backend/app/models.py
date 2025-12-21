from datetime import datetime
from .extensions import db

# Association table for project members (many-to-many)
project_members = db.Table('project_members',
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('joined_at', db.DateTime, default=datetime.utcnow)
)


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='member')  # admin, member
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    owned_projects = db.relationship('Project', back_populates='owner', foreign_keys='Project.owner_id')
    assigned_issues = db.relationship('Issue', back_populates='assignee', foreign_keys='Issue.assignee_id')
    comments = db.relationship('Comment', back_populates='author', cascade='all, delete-orphan')
    member_of_projects = db.relationship('Project', secondary=project_members, back_populates='members')
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat()
        }


class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)  # Soft delete
    
    # Relationships
    owner = db.relationship('User', back_populates='owned_projects', foreign_keys=[owner_id])
    members = db.relationship('User', secondary=project_members, back_populates='member_of_projects')
    issues = db.relationship('Issue', back_populates='project', cascade='all, delete-orphan')
    
    def to_dict(self, include_members=False):
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'owner_id': self.owner_id,
            'created_at': self.created_at.isoformat(),
            'is_deleted': self.is_deleted
        }
        if include_members:
            data['members'] = [m.to_dict() for m in self.members]
        return data


class Issue(db.Model):
    __tablename__ = 'issues'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default='OPEN')  # OPEN, IN_PROGRESS, DONE
    priority = db.Column(db.String(20), nullable=False, default='MEDIUM')  # LOW, MEDIUM, HIGH, CRITICAL
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)  # Soft delete
    
    # Relationships
    project = db.relationship('Project', back_populates='issues')
    assignee = db.relationship('User', back_populates='assigned_issues', foreign_keys=[assignee_id])
    reporter = db.relationship('User', foreign_keys=[reporter_id])
    comments = db.relationship('Comment', back_populates='issue', cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', back_populates='issue', cascade='all, delete-orphan')
    
    def to_dict(self, include_comments=False):
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'project_id': self.project_id,
            'assignee_id': self.assignee_id,
            'reporter_id': self.reporter_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_deleted': self.is_deleted
        }
        if include_comments:
            data['comments'] = [c.to_dict() for c in self.comments if not c.is_deleted]
        return data


class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    issue_id = db.Column(db.Integer, db.ForeignKey('issues.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)  # Soft delete
    
    # Relationships
    issue = db.relationship('Issue', back_populates='comments')
    author = db.relationship('User', back_populates='comments')
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'issue_id': self.issue_id,
            'author_id': self.author_id,
            'author_email': self.author.email if self.author else None,
            'created_at': self.created_at.isoformat(),
            'is_deleted': self.is_deleted
        }


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issues.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # e.g., 'status_change', 'assigned', 'created'
    old_value = db.Column(db.String(255))
    new_value = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    issue = db.relationship('Issue', back_populates='audit_logs')
    user = db.relationship('User')
    
    def to_dict(self):
        return {
            'id': self.id,
            'issue_id': self.issue_id,
            'user_id': self.user_id,
            'action': self.action,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'timestamp': self.timestamp.isoformat()
        }