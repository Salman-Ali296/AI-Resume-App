"""SkillTaxonomy model for NLP skill database."""
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY
from app.extensions import db


class SkillTaxonomy(db.Model):
    """SkillTaxonomy model for maintaining skill database for NLP extraction.
    
    Stores canonical skill names, categories, synonyms, and industry associations.
    Used by NLP engine for skill extraction, categorization, and synonym resolution.
    Supports fuzzy matching and contextual skill identification.
    """
    
    __tablename__ = 'skill_taxonomy'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Skill names
    skill_name = db.Column(db.String(255), nullable=False, index=True)
    canonical_name = db.Column(db.String(255), nullable=False, index=True)
    
    # Categorization
    category = db.Column(db.String(50), nullable=False, index=True)  # 'technical', 'soft', 'domain', 'tools', 'languages'
    industry = db.Column(db.String(100), nullable=True, index=True)  # 'technology', 'healthcare', 'finance', 'marketing', 'engineering'
    
    # Synonyms stored as array
    synonyms = db.Column(ARRAY(db.Text), nullable=True)
    
    # Timestamp
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default=db.func.now()
    )
    
    # Indexes
    __table_args__ = (
        db.Index('idx_skills_name', 'skill_name'),
        db.Index('idx_skills_canonical', 'canonical_name'),
        db.Index('idx_skills_category', 'category'),
        db.Index('idx_skills_industry', 'industry'),
    )
    
    def __repr__(self):
        """String representation of SkillTaxonomy."""
        return f'<SkillTaxonomy {self.canonical_name} ({self.category})>'
    
    def to_dict(self):
        """Convert skill taxonomy to dictionary representation."""
        return {
            'id': self.id,
            'skill_name': self.skill_name,
            'canonical_name': self.canonical_name,
            'category': self.category,
            'industry': self.industry,
            'synonyms': self.synonyms,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
