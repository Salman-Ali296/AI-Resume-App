"""Tests for SkillTaxonomy model."""
import pytest
from datetime import datetime
from models.skill_taxonomy import SkillTaxonomy
from app.extensions import db


class TestSkillTaxonomyModel:
    """Test suite for SkillTaxonomy model."""
    
    def test_skill_taxonomy_creation(self, app):
        """Test creating a skill taxonomy entry with required fields."""
        with app.app_context():
            skill = SkillTaxonomy(
                skill_name='Python',
                canonical_name='Python',
                category='technical',
                industry='technology',
                synonyms=['python', 'py']
            )
            db.session.add(skill)
            db.session.commit()
            
            assert skill.id is not None
            assert skill.skill_name == 'Python'
            assert skill.canonical_name == 'Python'
            assert skill.category == 'technical'
            assert skill.industry == 'technology'
            assert skill.synonyms == ['python', 'py']
            assert skill.created_at is not None
    
    def test_skill_taxonomy_without_synonyms(self, app):
        """Test creating a skill without synonyms."""
        with app.app_context():
            skill = SkillTaxonomy(
                skill_name='Leadership',
                canonical_name='Leadership',
                category='soft'
            )
            db.session.add(skill)
            db.session.commit()
            
            assert skill.synonyms is None
    
    def test_skill_taxonomy_without_industry(self, app):
        """Test creating a skill without industry specification."""
        with app.app_context():
            skill = SkillTaxonomy(
                skill_name='Communication',
                canonical_name='Communication',
                category='soft'
            )
            db.session.add(skill)
            db.session.commit()
            
            assert skill.industry is None
    
    def test_skill_taxonomy_categories(self, app):
        """Test different skill categories."""
        with app.app_context():
            categories = ['technical', 'soft', 'domain', 'tools', 'languages']
            
            for category in categories:
                skill = SkillTaxonomy(
                    skill_name=f'{category}_skill',
                    canonical_name=f'{category}_skill',
                    category=category
                )
                db.session.add(skill)
            
            db.session.commit()
            
            # Verify all categories were saved
            for category in categories:
                found = SkillTaxonomy.query.filter_by(category=category).first()
                assert found is not None
                assert found.category == category
    
    def test_skill_taxonomy_industries(self, app):
        """Test different industry associations."""
        with app.app_context():
            industries = ['technology', 'healthcare', 'finance', 'marketing', 'engineering']
            
            for industry in industries:
                skill = SkillTaxonomy(
                    skill_name=f'{industry}_skill',
                    canonical_name=f'{industry}_skill',
                    category='domain',
                    industry=industry
                )
                db.session.add(skill)
            
            db.session.commit()
            
            # Verify all industries were saved
            for industry in industries:
                found = SkillTaxonomy.query.filter_by(industry=industry).first()
                assert found is not None
                assert found.industry == industry
    
    def test_skill_taxonomy_synonym_mapping(self, app):
        """Test skill with multiple synonyms."""
        with app.app_context():
            skill = SkillTaxonomy(
                skill_name='JavaScript',
                canonical_name='JavaScript',
                category='technical',
                industry='technology',
                synonyms=['JS', 'javascript', 'js', 'ECMAScript']
            )
            db.session.add(skill)
            db.session.commit()
            
            assert len(skill.synonyms) == 4
            assert 'JS' in skill.synonyms
            assert 'ECMAScript' in skill.synonyms
    
    def test_skill_taxonomy_query_by_name(self, app):
        """Test querying skills by name."""
        with app.app_context():
            skill = SkillTaxonomy(
                skill_name='Machine Learning',
                canonical_name='Machine Learning',
                category='technical',
                industry='technology',
                synonyms=['ML', 'machine learning']
            )
            db.session.add(skill)
            db.session.commit()
            
            # Query by skill name
            found = SkillTaxonomy.query.filter_by(skill_name='Machine Learning').first()
            assert found is not None
            assert found.canonical_name == 'Machine Learning'
    
    def test_skill_taxonomy_query_by_canonical_name(self, app):
        """Test querying skills by canonical name."""
        with app.app_context():
            # Create synonym entry
            skill = SkillTaxonomy(
                skill_name='ML',
                canonical_name='Machine Learning',
                category='technical',
                industry='technology'
            )
            db.session.add(skill)
            db.session.commit()
            
            # Query by canonical name
            found = SkillTaxonomy.query.filter_by(canonical_name='Machine Learning').first()
            assert found is not None
            assert found.skill_name == 'ML'
    
    def test_skill_taxonomy_query_by_category(self, app):
        """Test querying skills by category."""
        with app.app_context():
            technical_skills = [
                SkillTaxonomy(skill_name='Python', canonical_name='Python', category='technical'),
                SkillTaxonomy(skill_name='Java', canonical_name='Java', category='technical')
            ]
            soft_skills = [
                SkillTaxonomy(skill_name='Leadership', canonical_name='Leadership', category='soft')
            ]
            
            db.session.add_all(technical_skills + soft_skills)
            db.session.commit()
            
            # Query technical skills
            tech_skills = SkillTaxonomy.query.filter_by(category='technical').all()
            assert len(tech_skills) == 2
            
            # Query soft skills
            soft_skills_result = SkillTaxonomy.query.filter_by(category='soft').all()
            assert len(soft_skills_result) == 1
    
    def test_skill_taxonomy_query_by_industry(self, app):
        """Test querying skills by industry."""
        with app.app_context():
            tech_skill = SkillTaxonomy(
                skill_name='Cloud Computing',
                canonical_name='Cloud Computing',
                category='technical',
                industry='technology'
            )
            healthcare_skill = SkillTaxonomy(
                skill_name='HIPAA Compliance',
                canonical_name='HIPAA Compliance',
                category='domain',
                industry='healthcare'
            )
            db.session.add_all([tech_skill, healthcare_skill])
            db.session.commit()
            
            # Query technology skills
            tech_skills = SkillTaxonomy.query.filter_by(industry='technology').all()
            assert len(tech_skills) == 1
            assert tech_skills[0].skill_name == 'Cloud Computing'
            
            # Query healthcare skills
            healthcare_skills = SkillTaxonomy.query.filter_by(industry='healthcare').all()
            assert len(healthcare_skills) == 1
            assert healthcare_skills[0].skill_name == 'HIPAA Compliance'
    
    def test_skill_taxonomy_to_dict(self, app):
        """Test converting skill taxonomy to dictionary."""
        with app.app_context():
            skill = SkillTaxonomy(
                skill_name='React',
                canonical_name='React',
                category='tools',
                industry='technology',
                synonyms=['ReactJS', 'React.js']
            )
            db.session.add(skill)
            db.session.commit()
            
            skill_dict = skill.to_dict()
            
            assert skill_dict['id'] == skill.id
            assert skill_dict['skill_name'] == 'React'
            assert skill_dict['canonical_name'] == 'React'
            assert skill_dict['category'] == 'tools'
            assert skill_dict['industry'] == 'technology'
            assert skill_dict['synonyms'] == ['ReactJS', 'React.js']
            assert 'created_at' in skill_dict
    
    def test_skill_taxonomy_repr(self, app):
        """Test string representation of skill taxonomy."""
        with app.app_context():
            skill = SkillTaxonomy(
                skill_name='SQL',
                canonical_name='SQL',
                category='technical'
            )
            db.session.add(skill)
            db.session.commit()
            
            assert repr(skill) == '<SkillTaxonomy SQL (technical)>'
    
    def test_skill_taxonomy_timestamps(self, app):
        """Test that timestamps are set correctly."""
        with app.app_context():
            skill = SkillTaxonomy(
                skill_name='Docker',
                canonical_name='Docker',
                category='tools'
            )
            db.session.add(skill)
            db.session.commit()
            
            assert isinstance(skill.created_at, datetime)
    
    def test_skill_taxonomy_multiple_entries_same_canonical(self, app):
        """Test multiple skill entries mapping to same canonical name."""
        with app.app_context():
            # Create multiple entries for JavaScript variations
            js_entries = [
                SkillTaxonomy(skill_name='JavaScript', canonical_name='JavaScript', category='technical'),
                SkillTaxonomy(skill_name='JS', canonical_name='JavaScript', category='technical'),
                SkillTaxonomy(skill_name='javascript', canonical_name='JavaScript', category='technical')
            ]
            db.session.add_all(js_entries)
            db.session.commit()
            
            # Query all entries with same canonical name
            js_skills = SkillTaxonomy.query.filter_by(canonical_name='JavaScript').all()
            assert len(js_skills) == 3
            
            # Verify all have same canonical name
            for skill in js_skills:
                assert skill.canonical_name == 'JavaScript'
    
    def test_skill_taxonomy_empty_synonyms_array(self, app):
        """Test creating a skill with empty synonyms array."""
        with app.app_context():
            skill = SkillTaxonomy(
                skill_name='Unique Skill',
                canonical_name='Unique Skill',
                category='domain',
                synonyms=[]
            )
            db.session.add(skill)
            db.session.commit()
            
            assert skill.synonyms == []
