"""Tests for ContactSubmission model."""
import pytest
from datetime import datetime
from models.user import User
from models.contact_submission import ContactSubmission
from app.extensions import db


class TestContactSubmissionModel:
    """Test suite for ContactSubmission model."""
    
    def test_contact_submission_creation(self, app):
        """Test creating a contact submission with required fields."""
        with app.app_context():
            # Create a user first
            user = User(
                email='contact@example.com',
                password_hash='hashed_password'
            )
            db.session.add(user)
            db.session.commit()
            
            # Create contact submission
            submission = ContactSubmission(
                user_id=user.id,
                email='contact@example.com',
                subject='Test Subject',
                message='This is a test message',
                category='general_inquiry'
            )
            db.session.add(submission)
            db.session.commit()
            
            assert submission.id is not None
            assert submission.user_id == user.id
            assert submission.email == 'contact@example.com'
            assert submission.subject == 'Test Subject'
            assert submission.message == 'This is a test message'
            assert submission.category == 'general_inquiry'
            assert submission.created_at is not None
    
    def test_contact_submission_without_user(self, app):
        """Test creating a contact submission without a user (unauthenticated)."""
        with app.app_context():
            submission = ContactSubmission(
                email='anonymous@example.com',
                subject='Anonymous Inquiry',
                message='Message from unauthenticated user',
                category='general_inquiry'
            )
            db.session.add(submission)
            db.session.commit()
            
            assert submission.id is not None
            assert submission.user_id is None
            assert submission.email == 'anonymous@example.com'
    
    def test_contact_submission_categories(self, app):
        """Test different submission categories."""
        with app.app_context():
            categories = ['bug_report', 'feature_request', 'general_inquiry']
            
            for category in categories:
                submission = ContactSubmission(
                    email=f'{category}@example.com',
                    subject=f'{category} subject',
                    message=f'{category} message',
                    category=category
                )
                db.session.add(submission)
            
            db.session.commit()
            
            # Verify all categories were saved
            for category in categories:
                found = ContactSubmission.query.filter_by(category=category).first()
                assert found is not None
                assert found.category == category
    
    def test_contact_submission_user_relationship(self, app):
        """Test relationship between ContactSubmission and User."""
        with app.app_context():
            user = User(
                email='relationship@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            submission = ContactSubmission(
                user_id=user.id,
                email='relationship@example.com',
                subject='Relationship Test',
                message='Testing relationship',
                category='general_inquiry'
            )
            db.session.add(submission)
            db.session.commit()
            
            # Test forward relationship
            assert submission.user.email == 'relationship@example.com'
            
            # Test backward relationship
            assert user.contact_submissions.count() == 1
            assert user.contact_submissions.first().subject == 'Relationship Test'
    
    def test_contact_submission_user_deletion_set_null(self, app):
        """Test that user_id is set to NULL when user is deleted."""
        with app.app_context():
            user = User(
                email='setnull@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            submission = ContactSubmission(
                user_id=user.id,
                email='setnull@example.com',
                subject='Set Null Test',
                message='Testing SET NULL behavior',
                category='bug_report'
            )
            db.session.add(submission)
            db.session.commit()
            
            submission_id = submission.id
            
            # Delete user
            db.session.delete(user)
            db.session.commit()
            
            # Verify submission still exists but user_id is NULL
            remaining_submission = ContactSubmission.query.get(submission_id)
            assert remaining_submission is not None
            assert remaining_submission.user_id is None
            assert remaining_submission.email == 'setnull@example.com'
    
    def test_contact_submission_multiple_per_user(self, app):
        """Test that a user can have multiple contact submissions."""
        with app.app_context():
            user = User(
                email='multiple@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            submissions = []
            for i in range(3):
                submission = ContactSubmission(
                    user_id=user.id,
                    email='multiple@example.com',
                    subject=f'Subject {i}',
                    message=f'Message {i}',
                    category='general_inquiry'
                )
                submissions.append(submission)
            
            db.session.add_all(submissions)
            db.session.commit()
            
            assert user.contact_submissions.count() == 3
    
    def test_contact_submission_to_dict(self, app):
        """Test converting contact submission to dictionary."""
        with app.app_context():
            user = User(
                email='dict@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            submission = ContactSubmission(
                user_id=user.id,
                email='dict@example.com',
                subject='Dict Test',
                message='Testing to_dict method',
                category='feature_request'
            )
            db.session.add(submission)
            db.session.commit()
            
            submission_dict = submission.to_dict()
            
            assert submission_dict['id'] == submission.id
            assert submission_dict['user_id'] == user.id
            assert submission_dict['email'] == 'dict@example.com'
            assert submission_dict['subject'] == 'Dict Test'
            assert submission_dict['message'] == 'Testing to_dict method'
            assert submission_dict['category'] == 'feature_request'
            assert 'created_at' in submission_dict
    
    def test_contact_submission_repr(self, app):
        """Test string representation of contact submission."""
        with app.app_context():
            submission = ContactSubmission(
                email='repr@example.com',
                subject='Repr Test',
                message='Testing repr',
                category='bug_report'
            )
            db.session.add(submission)
            db.session.commit()
            
            assert repr(submission) == f'<ContactSubmission {submission.id} from repr@example.com>'
    
    def test_contact_submission_timestamps(self, app):
        """Test that timestamps are set correctly."""
        with app.app_context():
            submission = ContactSubmission(
                email='timestamp@example.com',
                subject='Timestamp Test',
                message='Testing timestamps',
                category='general_inquiry'
            )
            db.session.add(submission)
            db.session.commit()
            
            assert isinstance(submission.created_at, datetime)
    
    def test_contact_submission_query_by_category(self, app):
        """Test querying submissions by category."""
        with app.app_context():
            bug_report = ContactSubmission(
                email='bug@example.com',
                subject='Bug Report',
                message='Found a bug',
                category='bug_report'
            )
            feature_request = ContactSubmission(
                email='feature@example.com',
                subject='Feature Request',
                message='Need a feature',
                category='feature_request'
            )
            db.session.add_all([bug_report, feature_request])
            db.session.commit()
            
            # Query bug reports
            bug_reports = ContactSubmission.query.filter_by(category='bug_report').all()
            assert len(bug_reports) == 1
            assert bug_reports[0].subject == 'Bug Report'
            
            # Query feature requests
            feature_requests = ContactSubmission.query.filter_by(category='feature_request').all()
            assert len(feature_requests) == 1
            assert feature_requests[0].subject == 'Feature Request'
    
    def test_contact_submission_long_message(self, app):
        """Test creating a submission with a long message."""
        with app.app_context():
            long_message = 'A' * 5000  # 5000 character message
            
            submission = ContactSubmission(
                email='long@example.com',
                subject='Long Message',
                message=long_message,
                category='general_inquiry'
            )
            db.session.add(submission)
            db.session.commit()
            
            assert len(submission.message) == 5000
            assert submission.message == long_message
