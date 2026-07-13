"""Tests for UsageTracking model."""
import pytest
from datetime import date
from models.user import User
from models.usage_tracking import UsageTracking
from app.extensions import db


class TestUsageTrackingModel:
    """Test suite for UsageTracking model."""
    
    def test_usage_tracking_creation(self, app):
        """Test creating a usage tracking record with required fields."""
        with app.app_context():
            # Create a user first
            user = User(
                email='usage@example.com',
                password_hash='hashed_password'
            )
            db.session.add(user)
            db.session.commit()
            
            # Create usage tracking record
            usage = UsageTracking(
                user_id=user.id,
                month=date(2024, 1, 1),
                analysis_count=5
            )
            db.session.add(usage)
            db.session.commit()
            
            assert usage.id is not None
            assert usage.user_id == user.id
            assert usage.month == date(2024, 1, 1)
            assert usage.analysis_count == 5
    
    def test_usage_tracking_default_count(self, app):
        """Test that analysis_count defaults to 0."""
        with app.app_context():
            user = User(
                email='default@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            usage = UsageTracking(
                user_id=user.id,
                month=date(2024, 2, 1)
            )
            db.session.add(usage)
            db.session.commit()
            
            assert usage.analysis_count == 0
    
    def test_usage_tracking_unique_constraint(self, app):
        """Test that user_id and month combination must be unique."""
        with app.app_context():
            user = User(
                email='unique@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            usage1 = UsageTracking(
                user_id=user.id,
                month=date(2024, 3, 1),
                analysis_count=3
            )
            db.session.add(usage1)
            db.session.commit()
            
            # Try to create duplicate
            usage2 = UsageTracking(
                user_id=user.id,
                month=date(2024, 3, 1),
                analysis_count=5
            )
            db.session.add(usage2)
            
            with pytest.raises(Exception):  # IntegrityError
                db.session.commit()
            
            db.session.rollback()
    
    def test_usage_tracking_increment(self, app):
        """Test incrementing analysis count."""
        with app.app_context():
            user = User(
                email='increment@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            usage = UsageTracking(
                user_id=user.id,
                month=date(2024, 4, 1),
                analysis_count=0
            )
            db.session.add(usage)
            db.session.commit()
            
            # Increment count
            usage.analysis_count += 1
            db.session.commit()
            
            assert usage.analysis_count == 1
            
            # Increment again
            usage.analysis_count += 1
            db.session.commit()
            
            assert usage.analysis_count == 2
    
    def test_usage_tracking_user_relationship(self, app):
        """Test relationship between UsageTracking and User."""
        with app.app_context():
            user = User(
                email='relationship@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            usage = UsageTracking(
                user_id=user.id,
                month=date(2024, 5, 1),
                analysis_count=10
            )
            db.session.add(usage)
            db.session.commit()
            
            # Test forward relationship
            assert usage.user.email == 'relationship@example.com'
            
            # Test backward relationship
            assert user.usage_tracking.count() == 1
            assert user.usage_tracking.first().analysis_count == 10
    
    def test_usage_tracking_cascade_delete(self, app):
        """Test that usage tracking records are deleted when user is deleted."""
        with app.app_context():
            user = User(
                email='cascade@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            usage1 = UsageTracking(
                user_id=user.id,
                month=date(2024, 1, 1),
                analysis_count=5
            )
            usage2 = UsageTracking(
                user_id=user.id,
                month=date(2024, 2, 1),
                analysis_count=3
            )
            db.session.add_all([usage1, usage2])
            db.session.commit()
            
            user_id = user.id
            
            # Delete user
            db.session.delete(user)
            db.session.commit()
            
            # Verify usage records are deleted
            remaining_usage = UsageTracking.query.filter_by(user_id=user_id).all()
            assert len(remaining_usage) == 0
    
    def test_usage_tracking_multiple_months(self, app):
        """Test that a user can have multiple usage records for different months."""
        with app.app_context():
            user = User(
                email='multiple@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            months = [
                (date(2024, 1, 1), 5),
                (date(2024, 2, 1), 10),
                (date(2024, 3, 1), 3)
            ]
            
            for month, count in months:
                usage = UsageTracking(
                    user_id=user.id,
                    month=month,
                    analysis_count=count
                )
                db.session.add(usage)
            
            db.session.commit()
            
            assert user.usage_tracking.count() == 3
            
            # Verify counts
            jan_usage = UsageTracking.query.filter_by(
                user_id=user.id,
                month=date(2024, 1, 1)
            ).first()
            assert jan_usage.analysis_count == 5
    
    def test_usage_tracking_to_dict(self, app):
        """Test converting usage tracking to dictionary."""
        with app.app_context():
            user = User(
                email='dict@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            usage = UsageTracking(
                user_id=user.id,
                month=date(2024, 6, 1),
                analysis_count=15
            )
            db.session.add(usage)
            db.session.commit()
            
            usage_dict = usage.to_dict()
            
            assert usage_dict['id'] == usage.id
            assert usage_dict['user_id'] == user.id
            assert usage_dict['month'] == '2024-06-01'
            assert usage_dict['analysis_count'] == 15
    
    def test_usage_tracking_repr(self, app):
        """Test string representation of usage tracking."""
        with app.app_context():
            user = User(
                email='repr@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            usage = UsageTracking(
                user_id=user.id,
                month=date(2024, 7, 1),
                analysis_count=20
            )
            db.session.add(usage)
            db.session.commit()
            
            expected = f'<UsageTracking user={user.id} month=2024-07-01 count=20>'
            assert repr(usage) == expected
    
    def test_usage_tracking_query_by_month(self, app):
        """Test querying usage by specific month."""
        with app.app_context():
            user = User(
                email='query@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            usage = UsageTracking(
                user_id=user.id,
                month=date(2024, 8, 1),
                analysis_count=7
            )
            db.session.add(usage)
            db.session.commit()
            
            # Query by month
            found_usage = UsageTracking.query.filter_by(
                user_id=user.id,
                month=date(2024, 8, 1)
            ).first()
            
            assert found_usage is not None
            assert found_usage.analysis_count == 7
