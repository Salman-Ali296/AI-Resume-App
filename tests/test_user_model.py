"""Tests for User model."""
import pytest
from datetime import datetime
from models.user import User
from app.extensions import db


class TestUserModel:
    """Test suite for User model."""
    
    def test_user_creation(self, app):
        """Test creating a user with required fields."""
        with app.app_context():
            user = User(
                email='test@example.com',
                password_hash='hashed_password_123',
                subscription_tier='free'
            )
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert user.email == 'test@example.com'
            assert user.password_hash == 'hashed_password_123'
            assert user.subscription_tier == 'free'
            assert user.created_at is not None
            assert user.updated_at is not None
            assert user.last_login is None
            assert user.oauth_provider is None
            assert user.oauth_id is None
    
    def test_user_with_oauth(self, app):
        """Test creating a user with OAuth fields."""
        with app.app_context():
            user = User(
                email='oauth@example.com',
                password_hash='',  # OAuth users may not have password
                oauth_provider='google',
                oauth_id='google_123456',
                subscription_tier='professional'
            )
            db.session.add(user)
            db.session.commit()
            
            assert user.oauth_provider == 'google'
            assert user.oauth_id == 'google_123456'
            assert user.subscription_tier == 'professional'
    
    def test_user_email_unique(self, app):
        """Test that email must be unique."""
        with app.app_context():
            user1 = User(
                email='unique@example.com',
                password_hash='hash1'
            )
            db.session.add(user1)
            db.session.commit()
            
            user2 = User(
                email='unique@example.com',
                password_hash='hash2'
            )
            db.session.add(user2)
            
            with pytest.raises(Exception):  # IntegrityError
                db.session.commit()
            
            db.session.rollback()
    
    def test_user_default_subscription_tier(self, app):
        """Test that subscription_tier defaults to 'free'."""
        with app.app_context():
            user = User(
                email='default@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            assert user.subscription_tier == 'free'
    
    def test_user_timestamps(self, app):
        """Test that timestamps are set correctly."""
        with app.app_context():
            user = User(
                email='timestamp@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            assert isinstance(user.created_at, datetime)
            assert isinstance(user.updated_at, datetime)
            assert user.created_at <= user.updated_at
    
    def test_user_last_login_update(self, app):
        """Test updating last_login timestamp."""
        with app.app_context():
            user = User(
                email='login@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            assert user.last_login is None
            
            # Update last_login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            assert user.last_login is not None
            assert isinstance(user.last_login, datetime)
    
    def test_user_to_dict(self, app):
        """Test converting user to dictionary."""
        with app.app_context():
            user = User(
                email='dict@example.com',
                password_hash='hash',
                subscription_tier='enterprise',
                oauth_provider='linkedin'
            )
            db.session.add(user)
            db.session.commit()
            
            user_dict = user.to_dict()
            
            assert user_dict['id'] == user.id
            assert user_dict['email'] == 'dict@example.com'
            assert user_dict['subscription_tier'] == 'enterprise'
            assert user_dict['oauth_provider'] == 'linkedin'
            assert 'password_hash' not in user_dict  # Should not expose password
            assert 'created_at' in user_dict
            assert 'updated_at' in user_dict
    
    def test_user_repr(self, app):
        """Test string representation of user."""
        with app.app_context():
            user = User(
                email='repr@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            assert repr(user) == '<User repr@example.com>'
    
    def test_user_subscription_tiers(self, app):
        """Test different subscription tiers."""
        with app.app_context():
            tiers = ['free', 'professional', 'enterprise']
            
            for tier in tiers:
                user = User(
                    email=f'{tier}@example.com',
                    password_hash='hash',
                    subscription_tier=tier
                )
                db.session.add(user)
            
            db.session.commit()
            
            for tier in tiers:
                user = User.query.filter_by(email=f'{tier}@example.com').first()
                assert user.subscription_tier == tier
    
    def test_user_oauth_index(self, app):
        """Test querying users by OAuth provider and ID."""
        with app.app_context():
            user = User(
                email='oauth_index@example.com',
                password_hash='hash',
                oauth_provider='google',
                oauth_id='google_789'
            )
            db.session.add(user)
            db.session.commit()
            
            # Query by OAuth fields
            found_user = User.query.filter_by(
                oauth_provider='google',
                oauth_id='google_789'
            ).first()
            
            assert found_user is not None
            assert found_user.email == 'oauth_index@example.com'
