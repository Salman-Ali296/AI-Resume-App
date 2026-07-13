"""Tests for Analysis model."""
import pytest
from datetime import datetime
from models.analysis import Analysis


class TestAnalysisModel:
    """Test suite for Analysis model."""
    
    def test_analysis_creation(self, app):
        """Test creating an Analysis instance."""
        with app.app_context():
            analysis = Analysis(
                user_id=1,
                resume_id=1,
                job_description='Looking for a Python developer with 3+ years experience.',
                match_score=85.5,
                ats_score=92.0,
                quality_score=88.0,
                extracted_skills={
                    'technical': ['Python', 'Django', 'PostgreSQL'],
                    'soft': ['Communication', 'Teamwork'],
                    'tools': ['Git', 'Docker']
                },
                match_breakdown={
                    'required_skills_score': 90.0,
                    'preferred_skills_score': 80.0,
                    'experience_score': 85.0,
                    'education_score': 100.0,
                    'contextual_fit_score': 75.0
                },
                recommendations=[
                    'Add more context about Python projects',
                    'Emphasize Django experience',
                    'Include specific metrics and achievements'
                ],
                industry='Technology'
            )
            
            assert analysis.user_id == 1
            assert analysis.resume_id == 1
            assert 'Python developer' in analysis.job_description
            assert analysis.match_score == 85.5
            assert analysis.ats_score == 92.0
            assert analysis.quality_score == 88.0
            assert 'Python' in analysis.extracted_skills['technical']
            assert analysis.match_breakdown['required_skills_score'] == 90.0
            assert len(analysis.recommendations) == 3
            assert analysis.industry == 'Technology'
    
    def test_analysis_repr(self, app):
        """Test Analysis string representation."""
        with app.app_context():
            analysis = Analysis(
                user_id=1,
                resume_id=5,
                job_description='Test job description',
                match_score=75.0,
                ats_score=80.0,
                quality_score=85.0,
                extracted_skills={},
                match_breakdown={},
                recommendations=[]
            )
            analysis.id = 10
            
            assert repr(analysis) == '<Analysis 10 for resume 5>'
    
    def test_analysis_to_dict(self, app):
        """Test Analysis to_dict method."""
        with app.app_context():
            analysis = Analysis(
                user_id=1,
                resume_id=1,
                job_description='Software Engineer position',
                match_score=85.5,
                ats_score=92.0,
                quality_score=88.0,
                extracted_skills={
                    'technical': ['Python', 'JavaScript'],
                    'soft': ['Leadership']
                },
                match_breakdown={
                    'required_skills_score': 90.0,
                    'preferred_skills_score': 80.0
                },
                recommendations=['Improve keyword density'],
                industry='Technology'
            )
            analysis.id = 1
            analysis.created_at = datetime(2024, 1, 15, 14, 0, 0)
            
            analysis_dict = analysis.to_dict()
            
            assert analysis_dict['id'] == 1
            assert analysis_dict['user_id'] == 1
            assert analysis_dict['resume_id'] == 1
            assert analysis_dict['job_description'] == 'Software Engineer position'
            assert analysis_dict['match_score'] == 85.5
            assert analysis_dict['ats_score'] == 92.0
            assert analysis_dict['quality_score'] == 88.0
            assert 'Python' in analysis_dict['extracted_skills']['technical']
            assert analysis_dict['match_breakdown']['required_skills_score'] == 90.0
            assert len(analysis_dict['recommendations']) == 1
            assert analysis_dict['industry'] == 'Technology'
            assert analysis_dict['created_at'] == '2024-01-15T14:00:00'
    
    def test_analysis_scores_range(self, app):
        """Test Analysis with various score values."""
        with app.app_context():
            # Test with perfect scores
            analysis_perfect = Analysis(
                user_id=1,
                resume_id=1,
                job_description='Perfect match job',
                match_score=100.0,
                ats_score=100.0,
                quality_score=100.0,
                extracted_skills={},
                match_breakdown={},
                recommendations=[]
            )
            
            assert analysis_perfect.match_score == 100.0
            assert analysis_perfect.ats_score == 100.0
            assert analysis_perfect.quality_score == 100.0
            
            # Test with low scores
            analysis_low = Analysis(
                user_id=1,
                resume_id=2,
                job_description='Poor match job',
                match_score=25.5,
                ats_score=30.0,
                quality_score=40.0,
                extracted_skills={},
                match_breakdown={},
                recommendations=[]
            )
            
            assert analysis_low.match_score == 25.5
            assert analysis_low.ats_score == 30.0
            assert analysis_low.quality_score == 40.0
    
    def test_analysis_complex_jsonb_data(self, app):
        """Test Analysis with complex JSONB fields."""
        with app.app_context():
            complex_skills = {
                'technical': [
                    {'name': 'Python', 'confidence': 95.0, 'category': 'programming'},
                    {'name': 'Django', 'confidence': 88.0, 'category': 'framework'},
                    {'name': 'PostgreSQL', 'confidence': 92.0, 'category': 'database'}
                ],
                'soft': [
                    {'name': 'Leadership', 'confidence': 85.0},
                    {'name': 'Communication', 'confidence': 90.0}
                ],
                'tools': [
                    {'name': 'Git', 'confidence': 98.0},
                    {'name': 'Docker', 'confidence': 87.0}
                ]
            }
            
            complex_breakdown = {
                'required_skills_score': 90.0,
                'required_skills_weight': 0.40,
                'preferred_skills_score': 80.0,
                'preferred_skills_weight': 0.20,
                'experience_score': 85.0,
                'experience_weight': 0.20,
                'education_score': 100.0,
                'education_weight': 0.10,
                'contextual_fit_score': 75.0,
                'contextual_fit_weight': 0.10,
                'missing_skills': ['Kubernetes', 'AWS'],
                'extra_skills': ['Azure', 'GCP']
            }
            
            complex_recommendations = [
                {
                    'type': 'skill_gap',
                    'priority': 'high',
                    'message': 'Add Kubernetes experience to match job requirements'
                },
                {
                    'type': 'keyword_density',
                    'priority': 'medium',
                    'message': 'Increase mentions of Python in work experience'
                },
                {
                    'type': 'ats_optimization',
                    'priority': 'low',
                    'message': 'Remove tables from resume for better ATS compatibility'
                }
            ]
            
            analysis = Analysis(
                user_id=1,
                resume_id=1,
                job_description='Senior Python Developer with cloud experience',
                match_score=85.5,
                ats_score=92.0,
                quality_score=88.0,
                extracted_skills=complex_skills,
                match_breakdown=complex_breakdown,
                recommendations=complex_recommendations,
                industry='Technology'
            )
            
            # Verify complex extracted_skills
            assert len(analysis.extracted_skills['technical']) == 3
            assert analysis.extracted_skills['technical'][0]['name'] == 'Python'
            assert analysis.extracted_skills['technical'][0]['confidence'] == 95.0
            
            # Verify complex match_breakdown
            assert analysis.match_breakdown['required_skills_weight'] == 0.40
            assert 'Kubernetes' in analysis.match_breakdown['missing_skills']
            assert 'Azure' in analysis.match_breakdown['extra_skills']
            
            # Verify complex recommendations
            assert len(analysis.recommendations) == 3
            assert analysis.recommendations[0]['type'] == 'skill_gap'
            assert analysis.recommendations[0]['priority'] == 'high'
    
    def test_analysis_without_industry(self, app):
        """Test Analysis without industry field (nullable)."""
        with app.app_context():
            analysis = Analysis(
                user_id=1,
                resume_id=1,
                job_description='Generic job description',
                match_score=75.0,
                ats_score=80.0,
                quality_score=85.0,
                extracted_skills={},
                match_breakdown={},
                recommendations=[],
                industry=None
            )
            
            assert analysis.industry is None
            
            analysis_dict = analysis.to_dict()
            assert analysis_dict['industry'] is None
    
    def test_analysis_multiple_industries(self, app):
        """Test Analysis with different industry values."""
        with app.app_context():
            industries = ['Technology', 'Healthcare', 'Finance', 'Marketing', 'Engineering']
            
            for idx, industry in enumerate(industries):
                analysis = Analysis(
                    user_id=1,
                    resume_id=idx + 1,
                    job_description=f'{industry} job description',
                    match_score=80.0,
                    ats_score=85.0,
                    quality_score=90.0,
                    extracted_skills={},
                    match_breakdown={},
                    recommendations=[],
                    industry=industry
                )
                
                assert analysis.industry == industry
    
    def test_analysis_empty_collections(self, app):
        """Test Analysis with empty JSONB collections."""
        with app.app_context():
            analysis = Analysis(
                user_id=1,
                resume_id=1,
                job_description='Job with no matches',
                match_score=0.0,
                ats_score=50.0,
                quality_score=60.0,
                extracted_skills={},
                match_breakdown={},
                recommendations=[]
            )
            
            assert analysis.extracted_skills == {}
            assert analysis.match_breakdown == {}
            assert analysis.recommendations == []
