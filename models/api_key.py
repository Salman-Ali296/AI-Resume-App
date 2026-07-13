"""APIKey model for API authentication."""
from datetime import datetime
from app.extensions import db


class APIKey(db.Model):
    """APIKey model for API authentication and authorization.
    
    Stores hashed API keys for secure authentication of API requests.
    Supports key revocation via is_active flag and tracks usage.
    """
    
    __tablename__ = 'api_keys'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key to user
    user_id = db.Column(
        db.Integer, 
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # API key fields
    key_hash = db.Column(db.String(255), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=True)
    
    # Status and tracking
    is_active = db.Column(db.Boolean, nullable=False, default=True, server_default='true')
    
    # Timestamps
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default=db.func.now()
    )
    last_used = db.Column(db.DateTime, nullable=True)
    
    # Relationship to user
    user = db.relationship('User', backref=db.backref('api_keys', lazy='dynamic', cascade='all, delete-orphan'))
    
    # Indexes
    __table_args__ = (
        db.Index('idx_api_keys_user', 'user_id'),
        db.Index('idx_api_keys_hash', 'key_hash'),
    )
    
    def __repr__(self):
        """String representation of APIKey."""
        return f'<APIKey {self.name or self.id} for user {self.user_id}>'
    
    def to_dict(self):
        """Convert API key to dictionary representation."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_used': self.last_used.isoformat() if self.last_used else None
        }
