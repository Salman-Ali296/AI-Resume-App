"""Tests for APIKey model."""
import pytest
from datetime import datetime
from models.user import User
from models.api_key import APIKey
from app.extensions import db


class TestAPIKeyModel:
    """Test suite for APIKey model."""
    
    def test_api_key_creation(self, app):
        """Test creating an API key with required fields."""
        with app.app_context():
            # Create a user first
            user = User(
                email='apitest@example.com',
                password_hash='hashed_password'
            )
            db.session.add(user)
            db.session.commit()
            
            # Create API key
            api_key = APIKey(
                user_id=user.id,
                key_hash='hashed_key_123',
                name='Test API Key'
            )
            db.session.add(api_key)
            db.session.commit()
            
            assert api_key.id is not None
            assert api_key.user_id == user.id
            assert api_key.key_hash == 'hashed_key_123'
            assert api_key.name == 'Test API Key'
            assert api_key.is_active is True
            assert api_key.created_at is not None
            assert api_key.last_used is None
    
    def test_api_key_without_name(self, app):
        """Test creating an API key without a name."""
        with app.app_context():
            user = User(
                email='noname@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            api_key = APIKey(
                user_id=user.id,
                key_hash='hashed_key_456'
            )
            db.session.add(api_key)
            db.session.commit()
            
            assert api_key.name is None
            assert api_key.key_hash == 'hashed_key_456'
    
    def test_api_key_is_active_default(self, app):
        """Test that is_active defaults to True."""
        with app.app_context():
            user = User(
                email='active@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            api_key = APIKey(
                user_id=user.id,
                key_hash='hashed_key_789'
            )
            db.session.add(api_key)
            db.session.commit()
            
            assert api_key.is_active is True
    
    def test_api_key_revocation(self, app):
        """Test revoking an API key by setting is_active to False."""
        with app.app_context():
            user = User(
                email='revoke@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            api_key = APIKey(
                user_id=user.id,
                key_hash='hashed_key_revoke'
            )
            db.session.add(api_key)
            db.session.commit()
            
            assert api_key.is_active is True
            
            # Revoke the key
            api_key.is_active = False
            db.session.commit()
            
            assert api_key.is_active is False
    
    def test_api_key_last_used_update(self, app):
        """Test updating last_used timestamp."""
        with app.app_context():
            user = User(
                email='lastused@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            api_key = APIKey(
                user_id=user.id,
                key_hash='hashed_key_used'
            )
            db.session.add(api_key)
            db.session.commit()
            
            assert api_key.last_used is None
            
            # Update last_used
            api_key.last_used = datetime.utcnow()
            db.session.commit()
            
            assert api_key.last_used is not None
            assert isinstance(api_key.last_used, datetime)
    
    def test_api_key_user_relationship(self, app):
        """Test relationship between APIKey and User."""
        with app.app_context():
            user = User(
                email='relationship@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            api_key = APIKey(
                user_id=user.id,
                key_hash='hashed_key_rel',
                name='Relationship Test'
            )
            db.session.add(api_key)
            db.session.commit()
            
            # Test forward relationship
            assert api_key.user.email == 'relationship@example.com'
            
            # Test backward relationship
            assert user.api_keys.count() == 1
            assert user.api_keys.first().name == 'Relationship Test'
    
    def test_api_key_cascade_delete(self, app):
        """Test that API keys are deleted when user is deleted."""
        with app.app_context():
            user = User(
                email='cascade@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            api_key1 = APIKey(
                user_id=user.id,
                key_hash='hashed_key_cascade1'
            )
            api_key2 = APIKey(
                user_id=user.id,
                key_hash='hashed_key_cascade2'
            )
            db.session.add_all([api_key1, api_key2])
            db.session.commit()
            
            user_id = user.id
            
            # Delete user
            db.session.delete(user)
            db.session.commit()
            
            # Verify API keys are deleted
            remaining_keys = APIKey.query.filter_by(user_id=user_id).all()
            assert len(remaining_keys) == 0
    
    def test_api_key_multiple_per_user(self, app):
        """Test that a user can have multiple API keys."""
        with app.app_context():
            user = User(
                email='multiple@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            keys = []
            for i in range(3):
                api_key = APIKey(
                    user_id=user.id,
                    key_hash=f'hashed_key_{i}',
                    name=f'Key {i}'
                )
                keys.append(api_key)
            
            db.session.add_all(keys)
            db.session.commit()
            
            assert user.api_keys.count() == 3
            
            # Verify all keys are associated with the user
            for i, key in enumerate(user.api_keys.all()):
                assert key.name == f'Key {i}'
    
    def test_api_key_to_dict(self, app):
        """Test converting API key to dictionary."""
        with app.app_context():
            user = User(
                email='dict@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            api_key = APIKey(
                user_id=user.id,
                key_hash='hashed_key_dict',
                name='Dict Test Key',
                is_active=True
            )
            db.session.add(api_key)
            db.session.commit()
            
            key_dict = api_key.to_dict()
            
            assert key_dict['id'] == api_key.id
            assert key_dict['user_id'] == user.id
            assert key_dict['name'] == 'Dict Test Key'
            assert key_dict['is_active'] is True
            assert 'key_hash' not in key_dict  # Should not expose key hash
            assert 'created_at' in key_dict
            assert 'last_used' in key_dict
    
    def test_api_key_repr(self, app):
        """Test string representation of API key."""
        with app.app_context():
            user = User(
                email='repr@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            api_key = APIKey(
                user_id=user.id,
                key_hash='hashed_key_repr',
                name='Repr Test'
            )
            db.session.add(api_key)
            db.session.commit()
            
            assert repr(api_key) == f'<APIKey Repr Test for user {user.id}>'
    
    def test_api_key_repr_without_name(self, app):
        """Test string representation of API key without name."""
        with app.app_context():
            user = User(
                email='repr_no_name@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            api_key = APIKey(
                user_id=user.id,
                key_hash='hashed_key_repr_no_name'
            )
            db.session.add(api_key)
            db.session.commit()
            
            assert repr(api_key) == f'<APIKey {api_key.id} for user {user.id}>'
    
    def test_api_key_timestamps(self, app):
        """Test that timestamps are set correctly."""
        with app.app_context():
            user = User(
                email='timestamp@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            api_key = APIKey(
                user_id=user.id,
                key_hash='hashed_key_timestamp'
            )
            db.session.add(api_key)
            db.session.commit()
            
            assert isinstance(api_key.created_at, datetime)
            assert api_key.last_used is None
    
    def test_api_key_query_by_hash(self, app):
        """Test querying API keys by hash (for authentication)."""
        with app.app_context():
            user = User(
                email='query@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            api_key = APIKey(
                user_id=user.id,
                key_hash='unique_hash_12345',
                name='Query Test'
            )
            db.session.add(api_key)
            db.session.commit()
            
            # Query by hash
            found_key = APIKey.query.filter_by(key_hash='unique_hash_12345').first()
            
            assert found_key is not None
            assert found_key.name == 'Query Test'
            assert found_key.user_id == user.id
    
    def test_api_key_query_active_only(self, app):
        """Test querying only active API keys."""
        with app.app_context():
            user = User(
                email='active_query@example.com',
                password_hash='hash'
            )
            db.session.add(user)
            db.session.commit()
            
            active_key = APIKey(
                user_id=user.id,
                key_hash='active_hash',
                is_active=True
            )
            inactive_key = APIKey(
                user_id=user.id,
                key_hash='inactive_hash',
                is_active=False
            )
            db.session.add_all([active_key, inactive_key])
            db.session.commit()
            
            # Query only active keys
            active_keys = APIKey.query.filter_by(user_id=user.id, is_active=True).all()
            
            assert len(active_keys) == 1
            assert active_keys[0].key_hash == 'active_hash'
