"""
Seed the database with test data
Run with: python seed.py
"""
from app import create_app
from app.extensions import db
from app.models import User, Project, Issue, Comment
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Clear existing data
    print("Clearing existing data...")
    Comment.query.delete()
    Issue.query.delete()
    Project.query.delete()
    User.query.delete()
    db.session.commit()
    
    # Create users
    print("Creating users...")
    admin = User(
        email='admin@test.com',
        password_hash=generate_password_hash('password'),
        role='admin'
    )
    
    alice = User(
        email='alice@test.com',
        password_hash=generate_password_hash('password'),
        role='member'
    )
    
    bob = User(
        email='bob@test.com',
        password_hash=generate_password_hash('password'),
        role='member'
    )
    
    charlie = User(
        email='charlie@test.com',
        password_hash=generate_password_hash('password'),
        role='member'
    )
    
    db.session.add_all([admin, alice, bob, charlie])
    db.session.commit()
    
    # Create projects
    print("Creating projects...")
    project1 = Project(
        name='Website Redesign',
        description='Complete overhaul of company website',
        owner_id=alice.id
    )
    project1.members.extend([alice, bob])
    
    project2 = Project(
        name='Mobile App',
        description='iOS and Android mobile application',
        owner_id=bob.id
    )
    project2.members.extend([bob, charlie, alice])
    
    db.session.add_all([project1, project2])
    db.session.commit()
    
    # Create issues
    print("Creating issues...")
    issue1 = Issue(
        title='Design new homepage',
        description='Create mockups for the new homepage design',
        project_id=project1.id,
        reporter_id=alice.id,
        assignee_id=bob.id,
        status='IN_PROGRESS',
        priority='HIGH'
    )
    
    issue2 = Issue(
        title='Setup database schema',
        description='Design and implement the database schema for user data',
        project_id=project1.id,
        reporter_id=alice.id,
        assignee_id=alice.id,
        status='DONE',
        priority='CRITICAL'
    )
    
    issue3 = Issue(
        title='Implement user authentication',
        description='Add JWT-based authentication to the API',
        project_id=project2.id,
        reporter_id=bob.id,
        assignee_id=charlie.id,
        status='OPEN',
        priority='HIGH'
    )
    
    issue4 = Issue(
        title='Write API documentation',
        description='Document all API endpoints with examples',
        project_id=project2.id,
        reporter_id=bob.id,
        status='OPEN',
        priority='MEDIUM'
    )
    
    issue5 = Issue(
        title='Fix login bug',
        description='Users getting logged out randomly',
        project_id=project2.id,
        reporter_id=charlie.id,
        assignee_id=alice.id,
        status='IN_PROGRESS',
        priority='CRITICAL'
    )
    
    db.session.add_all([issue1, issue2, issue3, issue4, issue5])
    db.session.commit()
    
    # Create comments
    print("Creating comments...")
    comment1 = Comment(
        content='I think we should go with a minimalist design',
        issue_id=issue1.id,
        author_id=alice.id
    )
    
    comment2 = Comment(
        content='Agreed! I\'ll start working on the mockups',
        issue_id=issue1.id,
        author_id=bob.id
    )
    
    comment3 = Comment(
        content='Schema looks good, ready for review',
        issue_id=issue2.id,
        author_id=alice.id
    )
    
    comment4 = Comment(
        content='Found the root cause - session timeout was set too low',
        issue_id=issue5.id,
        author_id=alice.id
    )
    
    db.session.add_all([comment1, comment2, comment3, comment4])
    db.session.commit()
    
    print("\nSeed data created successfully!")
    print("\nTest accounts:")
    print("  admin@test.com / password (admin)")
    print("  alice@test.com / password (member)")
    print("  bob@test.com / password (member)")
    print("  charlie@test.com / password (member)")
    print(f"\nCreated:")
    print(f"  {User.query.count()} users")
    print(f"  {Project.query.count()} projects")
    print(f"  {Issue.query.count()} issues")
    print(f"  {Comment.query.count()} comments")