"""AuditLog model for security auditing and compliance."""
from datetime import datetime
from sqlalchemy.dialects.postgresql import INET
from app.extensions import db


class AuditLog(db.Model):
    """AuditLog model for security auditing and compliance tracking.
    
    Logs all data access events, authentication events, and data modifications.
    Stores user actions with IP address and user agent for security monitoring.
    Used for compliance, security auditing, and incident investigation.
    """
    
    __tablename__ = 'audit_log'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key to user (nullable for unauthenticated actions)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    
    # Action details
    action = db.Column(db.String(100), nullable=False, index=True)  # 'login', 'logout', 'upload_resume', 'delete_resume', etc.
    resource_type = db.Column(db.String(50), nullable=False)  # 'user', 'resume', 'analysis', 'api_key', etc.
    resource_id = db.Column(db.Integer, nullable=True)
    
    # Request metadata
    ip_address = db.Column(INET, nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    
    # Timestamp
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default=db.func.now(),
        index=True
    )
    
    # Relationship to user
    user = db.relationship('User', backref=db.backref('audit_logs', lazy='dynamic'))
    
    # Indexes
    __table_args__ = (
        db.Index('idx_audit_user', 'user_id'),
        db.Index('idx_audit_created', 'created_at'),
        db.Index('idx_audit_action', 'action'),
    )
    
    def __repr__(self):
        """String representation of AuditLog."""
        return f'<AuditLog {self.action} by user {self.user_id} at {self.created_at}>'
    
    def to_dict(self):
        """Convert audit log to dictionary representation."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'ip_address': str(self.ip_address) if self.ip_address else None,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
