"""Basic application tests."""
import pytest


def test_app_creation(app):
    """Test that the application is created successfully."""
    assert app is not None
    assert app.config['TESTING'] is True


def test_health_check(client):
    """Test basic health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['service'] == 'resume-analyzer'


def test_config_loading(app):
    """Test that configuration is loaded correctly."""
    assert app.config['SQLALCHEMY_DATABASE_URI'] is not None
    assert app.config['REDIS_URL'] is not None
    assert app.config['CELERY_BROKER_URL'] is not None
    assert app.config['MAX_CONTENT_LENGTH'] == 5 * 1024 * 1024  # 5MB
    assert app.config['BCRYPT_LOG_ROUNDS'] == 12


def test_database_connection_pooling(app):
    """Test that database connection pooling is configured correctly."""
    pool_config = app.config['SQLALCHEMY_ENGINE_OPTIONS']
    assert pool_config['pool_size'] == 10
    assert pool_config['max_overflow'] == 90
    assert pool_config['pool_size'] + pool_config['max_overflow'] == 100


def test_404_error_handler(client):
    """Test 404 error handler."""
    response = client.get('/nonexistent-endpoint')
    assert response.status_code == 404
    data = response.get_json()
    assert data['error'] == 'Not Found'
