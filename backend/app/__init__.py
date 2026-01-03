from flask import Flask, jsonify, request, g
from flask_cors import CORS
from .config import Config
from .extensions import db, migrate
from prometheus_flask_exporter import PrometheusMetrics
from pythonjsonlogger import jsonlogger
import logging
import sys
import uuid

def _configure_logging(app):
    """Configure JSON logging with request context support."""
    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
    handler.setFormatter(formatter)
    
    app.logger.handlers.clear()
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    app.logger.propagate = False

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    _configure_logging(app)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Setup Prometheus metrics
    metrics = PrometheusMetrics(app)
    
    @app.before_request
    def attach_request_id():
        g.request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
    
    @app.after_request
    def log_request(response):
        app.logger.info(
            'request.completed',
            extra={
                'request_id': getattr(g, 'request_id', None),
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'remote_addr': request.remote_addr
            }
        )
        return response
    
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
    
    # Chaos endpoints for testing
    @app.route('/api/v1/chaos/slow')
    def chaos_slow():
        import time, random
        delay = random.randint(2, 5)
        app.logger.info(f'Slow request: {delay}s delay')
        time.sleep(delay)
        return jsonify({'delay': delay})
    
    @app.route('/api/v1/chaos/error')
    def chaos_error():
        app.logger.error('Intentional error endpoint called')
        raise Exception('Chaos!')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error(
            'server.error',
            extra={
                'request_id': getattr(g, 'request_id', None),
                'path': request.path,
                'error': str(e)
            }
        )
        return jsonify({'error': 'Internal server error'}), 500
    
    return app
