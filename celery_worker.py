"""Celery worker entry point."""
import os
from app import create_app
from app.extensions import celery

# Create Flask app to initialize Celery
app = create_app(os.environ.get('FLASK_ENV', 'development'))

# Celery instance is now configured and ready
# Run with: celery -A celery_worker.celery worker --loglevel=info
