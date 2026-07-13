"""User model for authentication and authorization."""
from datetime import datetime
from flask_login import UserMixin
from app.extensions import db


class User(UserMixin, db.Model):
    """User model with authentication fields and subscription management.
    
    Implements authentication for both email/password and OAuth providers.
    Tracks subscription tier for usage limits and feature access.
    """
    
    __tablename__ = 'users'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Authentication fields
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # OAuth fields
    oauth_provider = db.Column(db.String(50), nullable=True)
    oauth_id = db.Column(db.String(255), nullable=True)
    
    # Subscription management
    subscription_tier = db.Column(
        db.String(50), 
        nullable=False, 
        default='free',
        server_default='free'
    )
    
    # Password reset fields
    reset_token_hash = db.Column(db.String(255), nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(
        db.DateTime, 
        nullable=False, 
        default=datetime.utcnow,
        server_default=db.func.now()
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=db.func.now()
    )
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships (will be added as other models are created)
    # resumes = db.relationship('Resume', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    # analyses = db.relationship('Analysis', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    # api_keys = db.relationship('APIKey', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    # Indexes
    __table_args__ = (
        db.Index('idx_users_oauth', 'oauth_provider', 'oauth_id'),
    )
    
    def __repr__(self):
        """String representation of User."""
        return f'<User {self.email}>'
    
    def to_dict(self):
        """Convert user to dictionary representation."""
        return {
            'id': self.id,
            'email': self.email,
            'subscription_tier': self.subscription_tier,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'oauth_provider': self.oauth_provider
        }
