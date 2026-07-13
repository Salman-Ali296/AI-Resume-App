"""Flask application factory."""
import logging
import sys
from flask import Flask
from config import get_config
from app.extensions import (
    db, migrate, bcrypt, login_manager, session,
    init_redis, init_celery
)


def create_app(config_name=None):
    """Create and configure Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Initialize logging
    setup_logging(app)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    session.init_app(app)
    
    # Initialize Redis
    init_redis(app)
    
    # Initialize Celery
    init_celery(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    app.logger.info(f'Application started with {config_name or "default"} configuration')
    
    return app


def setup_logging(app):
    """Configure structured logging."""
    log_level = getattr(logging, app.config['LOG_LEVEL'])
    
    # Create formatter
    formatter = logging.Formatter(
        app.config['LOG_FORMAT'],
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # Configure app logger
    app.logger.setLevel(log_level)
    app.logger.addHandler(console_handler)
    
    # Configure SQLAlchemy logger
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)


def register_blueprints(app):
    """Register Flask blueprints."""
    # Import blueprints here to avoid circular imports
    from api.health import health_bp
    
    # Register health check endpoint
    app.register_blueprint(health_bp)
    
    # Additional blueprints will be registered as they are implemented
    # from api.auth import auth_bp
    # from api.resumes import resumes_bp
    # from api.analytics import analytics_bp
    # from api.exports import exports_bp
    
    # app.register_blueprint(auth_bp, url_prefix='/api/auth')
    # app.register_blueprint(resumes_bp, url_prefix='/api/resumes')
    # app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    # app.register_blueprint(exports_bp, url_prefix='/api/exports')


def register_error_handlers(app):
    """Register error handlers."""
    from flask import jsonify
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad Request',
            'message': str(error)
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required'
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'error': 'Forbidden',
            'message': 'Insufficient permissions'
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'Resource not found'
        }), 404
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return jsonify({
            'error': 'Too Many Requests',
            'message': 'Rate limit exceeded. Please try again later.'
        }), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Internal server error: {error}')
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500
    
    @app.errorhandler(503)
    def service_unavailable(error):
        return jsonify({
            'error': 'Service Unavailable',
            'message': 'System is currently overloaded. Please try again later.'
        }), 503
