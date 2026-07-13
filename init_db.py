"""Database initialization script."""
import os
from app import create_app
from app.extensions import db

def init_database():
    """Initialize the database."""
    app = create_app(os.environ.get('FLASK_ENV', 'development'))
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")
        
        # You can add seed data here if needed
        print("Database initialization complete.")

if __name__ == '__main__':
    init_database()
