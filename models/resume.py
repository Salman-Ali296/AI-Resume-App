"""Resume model for file storage and metadata."""
from datetime import datetime
from app.extensions import db


class Resume(db.Model):
    """Resume model for storing uploaded resume files and parsed data.
    
    Stores file metadata, S3 path, and parsed resume data in JSONB format.
    Supports soft deletes via is_deleted flag for data retention compliance.
    """
    
    __tablename__ = 'resumes'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key to user
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # File metadata
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_format = db.Column(db.String(10), nullable=False)
    
    # Parsed data stored as JSONB
    parsed_data = db.Column(db.JSON, nullable=False)
    
    # Soft delete flag
    is_deleted = db.Column(db.Boolean, nullable=False, default=False, server_default='false')
    
    # Timestamp
    uploaded_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default=db.func.now()
    )
    
    # Relationship to user
    user = db.relationship('User', backref=db.backref('resumes', lazy='dynamic', cascade='all, delete-orphan'))
    
    # Indexes
    __table_args__ = (
        db.Index('idx_resumes_user', 'user_id'),
        db.Index('idx_resumes_uploaded', 'uploaded_at'),
    )
    
    def __repr__(self):
        """String representation of Resume."""
        return f'<Resume {self.file_name} for user {self.user_id}>'
    
    def to_dict(self):
        """Convert resume to dictionary representation."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'file_name': self.file_name,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_format': self.file_format,
            'parsed_data': self.parsed_data,
            'is_deleted': self.is_deleted,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }
