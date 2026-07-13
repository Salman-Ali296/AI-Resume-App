"""Analysis model for storing resume analysis results."""
from datetime import datetime
from app.extensions import db


class Analysis(db.Model):
    """Analysis model for storing resume analysis results and scores.
    
    Stores match scores, ATS scores, quality scores, and detailed analysis data
    including extracted skills, match breakdown, and recommendations in JSONB format.
    Links to both user and resume for comprehensive tracking.
    """
    
    __tablename__ = 'analyses'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    resume_id = db.Column(
        db.Integer,
        db.ForeignKey('resumes.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Job description
    job_description = db.Column(db.Text, nullable=False)
    
    # Scores
    match_score = db.Column(db.Float, nullable=False, index=True)
    ats_score = db.Column(db.Float, nullable=False)
    quality_score = db.Column(db.Float, nullable=False)
    
    # Analysis data stored as JSONB
    extracted_skills = db.Column(db.JSON, nullable=False)
    match_breakdown = db.Column(db.JSON, nullable=False)
    recommendations = db.Column(db.JSON, nullable=False)
    
    # Industry context
    industry = db.Column(db.String(100), nullable=True)
    
    # Timestamp
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default=db.func.now()
    )
    
    # Relationships
    user = db.relationship('User', backref=db.backref('analyses', lazy='dynamic', cascade='all, delete-orphan'))
    resume = db.relationship('Resume', backref=db.backref('analyses', lazy='dynamic', cascade='all, delete-orphan'))
    
    # Indexes
    __table_args__ = (
        db.Index('idx_analyses_user', 'user_id'),
        db.Index('idx_analyses_resume', 'resume_id'),
        db.Index('idx_analyses_created', 'created_at'),
        db.Index('idx_analyses_match_score', 'match_score'),
    )
    
    def __repr__(self):
        """String representation of Analysis."""
        return f'<Analysis {self.id} for resume {self.resume_id}>'
    
    def to_dict(self):
        """Convert analysis to dictionary representation."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'resume_id': self.resume_id,
            'job_description': self.job_description,
            'match_score': self.match_score,
            'ats_score': self.ats_score,
            'quality_score': self.quality_score,
            'extracted_skills': self.extracted_skills,
            'match_breakdown': self.match_breakdown,
            'recommendations': self.recommendations,
            'industry': self.industry,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
