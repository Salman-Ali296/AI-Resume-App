"""Pytest configuration and fixtures."""
import pytest
from app import create_app
from app.extensions import db as _db
import fakeredis


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    app = create_app('testing')
    
    # Replace Redis client with fakeredis for testing
    from app import extensions
    extensions.redis_client = fakeredis.FakeStrictRedis(decode_responses=True)
    
    return app


@pytest.fixture(scope='session')
def db(app):
    """Create database for testing."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()


@pytest.fixture(scope='function')
def session(db):
    """Create a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()
    
    session = db.create_scoped_session(
        options={'bind': connection, 'binds': {}}
    )
    db.session = session
    
    yield session
    
    transaction.rollback()
    connection.close()
    session.remove()


@pytest.fixture(scope='function', autouse=True)
def clear_redis(app):
    """Clear Redis before each test."""
    from app import extensions
    if extensions.redis_client:
        extensions.redis_client.flushdb()


@pytest.fixture(scope='function')
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()
