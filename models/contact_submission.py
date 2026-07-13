"""ContactSubmission model for support requests and feature requests."""
from datetime import datetime
from app.extensions import db


class ContactSubmission(db.Model):
    """ContactSubmission model for storing user support requests.
    
    Stores contact form submissions with categorization (Bug Report, Feature Request, General Inquiry).
    Associates submissions with user accounts when authenticated.
    Retains submissions for 2 years for support history.
    """
    
    __tablename__ = 'contact_submissions'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key to user (nullable for unauthenticated submissions)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    
    # Contact information
    email = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    
    # Categorization
    category = db.Column(db.String(50), nullable=False)  # 'bug_report', 'feature_request', 'general_inquiry'
    
    # Timestamp
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default=db.func.now()
    )
    
    # Relationship to user
    user = db.relationship('User', backref=db.backref('contact_submissions', lazy='dynamic'))
    
    # Indexes
    __table_args__ = (
        db.Index('idx_contact_user', 'user_id'),
        db.Index('idx_contact_created', 'created_at'),
    )
    
    def __repr__(self):
        """String representation of ContactSubmission."""
        return f'<ContactSubmission {self.id} from {self.email}>'
    
    def to_dict(self):
        """Convert contact submission to dictionary representation."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'email': self.email,
            'subject': self.subject,
            'message': self.message,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
