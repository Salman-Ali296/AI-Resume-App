"""Tests for Resume model."""
import pytest
from datetime import datetime
from models.resume import Resume


class TestResumeModel:
    """Test suite for Resume model."""
    
    def test_resume_creation(self, app):
        """Test creating a Resume instance."""
        with app.app_context():
            resume = Resume(
                user_id=1,
                file_name='test_resume.pdf',
                file_path='s3://bucket/user1/resume1/test_resume.pdf',
                file_size=102400,
                file_format='pdf',
                parsed_data={
                    'contact_info': {
                        'name': 'John Doe',
                        'email': 'john@example.com',
                        'phone': '+1234567890'
                    },
                    'work_experience': [],
                    'education': []
                },
                is_deleted=False
            )
            
            assert resume.user_id == 1
            assert resume.file_name == 'test_resume.pdf'
            assert resume.file_path == 's3://bucket/user1/resume1/test_resume.pdf'
            assert resume.file_size == 102400
            assert resume.file_format == 'pdf'
            assert resume.parsed_data['contact_info']['name'] == 'John Doe'
            assert resume.is_deleted is False
    
    def test_resume_repr(self, app):
        """Test Resume string representation."""
        with app.app_context():
            resume = Resume(
                user_id=1,
                file_name='test_resume.pdf',
                file_path='s3://bucket/user1/resume1/test_resume.pdf',
                file_size=102400,
                file_format='pdf',
                parsed_data={},
                is_deleted=False
            )
            
            assert repr(resume) == '<Resume test_resume.pdf for user 1>'
    
    def test_resume_to_dict(self, app):
        """Test Resume to_dict method."""
        with app.app_context():
            resume = Resume(
                user_id=1,
                file_name='test_resume.pdf',
                file_path='s3://bucket/user1/resume1/test_resume.pdf',
                file_size=102400,
                file_format='pdf',
                parsed_data={
                    'contact_info': {
                        'name': 'John Doe',
                        'email': 'john@example.com'
                    }
                },
                is_deleted=False
            )
            resume.id = 1
            resume.uploaded_at = datetime(2024, 1, 15, 12, 0, 0)
            
            resume_dict = resume.to_dict()
            
            assert resume_dict['id'] == 1
            assert resume_dict['user_id'] == 1
            assert resume_dict['file_name'] == 'test_resume.pdf'
            assert resume_dict['file_path'] == 's3://bucket/user1/resume1/test_resume.pdf'
            assert resume_dict['file_size'] == 102400
            assert resume_dict['file_format'] == 'pdf'
            assert resume_dict['parsed_data']['contact_info']['name'] == 'John Doe'
            assert resume_dict['is_deleted'] is False
            assert resume_dict['uploaded_at'] == '2024-01-15T12:00:00'
    
    def test_resume_soft_delete(self, app):
        """Test Resume soft delete flag."""
        with app.app_context():
            resume = Resume(
                user_id=1,
                file_name='test_resume.pdf',
                file_path='s3://bucket/user1/resume1/test_resume.pdf',
                file_size=102400,
                file_format='pdf',
                parsed_data={},
                is_deleted=False
            )
            
            assert resume.is_deleted is False
            
            # Simulate soft delete
            resume.is_deleted = True
            assert resume.is_deleted is True
    
    def test_resume_jsonb_data(self, app):
        """Test Resume JSONB parsed_data field."""
        with app.app_context():
            complex_data = {
                'contact_info': {
                    'name': 'Jane Smith',
                    'email': 'jane@example.com',
                    'phone': '+9876543210',
                    'location': 'New York, NY'
                },
                'work_experience': [
                    {
                        'company': 'Tech Corp',
                        'title': 'Software Engineer',
                        'start_date': '2020-01',
                        'end_date': '2023-12',
                        'description': 'Developed web applications'
                    },
                    {
                        'company': 'Startup Inc',
                        'title': 'Junior Developer',
                        'start_date': '2018-06',
                        'end_date': '2019-12',
                        'description': 'Built mobile apps'
                    }
                ],
                'education': [
                    {
                        'institution': 'University of Example',
                        'degree': 'Bachelor of Science',
                        'field': 'Computer Science',
                        'graduation_date': '2018-05'
                    }
                ],
                'certifications': [
                    'AWS Certified Developer',
                    'Google Cloud Professional'
                ]
            }
            
            resume = Resume(
                user_id=1,
                file_name='complex_resume.pdf',
                file_path='s3://bucket/user1/resume2/complex_resume.pdf',
                file_size=204800,
                file_format='pdf',
                parsed_data=complex_data,
                is_deleted=False
            )
            
            assert len(resume.parsed_data['work_experience']) == 2
            assert resume.parsed_data['work_experience'][0]['company'] == 'Tech Corp'
            assert len(resume.parsed_data['education']) == 1
            assert resume.parsed_data['education'][0]['degree'] == 'Bachelor of Science'
            assert len(resume.parsed_data['certifications']) == 2
    
    def test_resume_file_formats(self, app):
        """Test Resume with different file formats."""
        with app.app_context():
            formats = ['pdf', 'docx', 'txt']
            
            for fmt in formats:
                resume = Resume(
                    user_id=1,
                    file_name=f'test_resume.{fmt}',
                    file_path=f's3://bucket/user1/resume/test_resume.{fmt}',
                    file_size=102400,
                    file_format=fmt,
                    parsed_data={},
                    is_deleted=False
                )
                
                assert resume.file_format == fmt
                assert resume.file_name.endswith(f'.{fmt}')
