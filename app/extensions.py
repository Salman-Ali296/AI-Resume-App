"""Flask extensions initialization."""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_session import Session
from redis import Redis
from celery import Celery

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
session = Session()
redis_client: Redis = None
celery: Celery = None


def init_redis(app):
    """Initialize Redis client."""
    global redis_client
    redis_client = Redis.from_url(
        app.config['REDIS_URL'],
        decode_responses=True
    )
    return redis_client


def init_celery(app):
    """Initialize Celery."""
    global celery
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery
