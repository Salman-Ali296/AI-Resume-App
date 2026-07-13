"""UsageTracking model for subscription limits and usage monitoring."""
from datetime import datetime
from app.extensions import db


class UsageTracking(db.Model):
    """UsageTracking model for monitoring subscription usage limits.
    
    Tracks the number of analyses performed by each user per month.
    Used to enforce tier-based limits (Free: 5, Professional: 50, Enterprise: unlimited).
    Monthly counters are reset on the first day of each month.
    """
    
    __tablename__ = 'usage_tracking'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key to user
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )
    
    # Month tracking (stored as first day of month)
    month = db.Column(db.Date, nullable=False)
    
    # Usage counter
    analysis_count = db.Column(db.Integer, nullable=False, default=0, server_default='0')
    
    # Relationship to user
    user = db.relationship('User', backref=db.backref('usage_tracking', lazy='dynamic', cascade='all, delete-orphan'))
    
    # Indexes and constraints
    __table_args__ = (
        db.Index('idx_usage_user_month', 'user_id', 'month'),
        db.UniqueConstraint('user_id', 'month', name='uq_user_month'),
    )
    
    def __repr__(self):
        """String representation of UsageTracking."""
        return f'<UsageTracking user={self.user_id} month={self.month} count={self.analysis_count}>'
    
    def to_dict(self):
        """Convert usage tracking to dictionary representation."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'month': self.month.isoformat() if self.month else None,
            'analysis_count': self.analysis_count
        }
