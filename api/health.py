"""Health check endpoints."""
from flask import Blueprint, jsonify
from app.extensions import db, redis_client

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'resume-analyzer'
    }), 200


@health_bp.route('/health/detailed', methods=['GET'])
def detailed_health_check():
    """Detailed health check with dependency status."""
    health_status = {
        'status': 'healthy',
        'service': 'resume-analyzer',
        'checks': {}
    }
    
    # Check database connectivity
    try:
        db.session.execute('SELECT 1')
        health_status['checks']['database'] = 'healthy'
    except Exception as e:
        health_status['checks']['database'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    # Check Redis connectivity
    try:
        redis_client.ping()
        health_status['checks']['redis'] = 'healthy'
    except Exception as e:
        health_status['checks']['redis'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return jsonify(health_status), status_code
