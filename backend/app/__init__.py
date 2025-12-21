from flask import Flask, jsonify
from flask_cors import CORS
from .config import Config
from .extensions import db, migrate


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Register blueprints
    from .api import auth, users, projects, issues, comments
    app.register_blueprint(auth.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(projects.bp)
    app.register_blueprint(issues.bp)
    app.register_blueprint(comments.bp)
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return jsonify({'status': 'ok', 'version': app.config['API_VERSION']})
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app