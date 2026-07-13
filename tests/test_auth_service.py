"""Tests for authentication service."""
import pytest
from services.auth_service import AuthenticationService, ValidationError
from models.user import User
from app.extensions import db


class TestEmailValidation:
    """Test suite for email validation."""
    
    def test_valid_email(self):
        """Test valid email formats."""
        valid_emails = [
            'user@example.com',
            'test.user@example.com',
            'user+tag@example.co.uk',
            'user_name@example-domain.com',
            'user123@test.org',
        ]
        
        for email in valid_emails:
            is_valid, error = AuthenticationService.validate_email(email)
            assert is_valid is True, f"Email {email} should be valid"
            assert error is None
    
    def test_invalid_email_format(self):
        """Test invalid email formats."""
        invalid_emails = [
            'notanemail',
            '@example.com',
            'user@',
            'user@.com',
            'user @example.com',
            'user@example',
            '',
            'user@@example.com',
            'user@example..com',
        ]
        
        for email in invalid_emails:
            is_valid, error = AuthenticationService.validate_email(email)
            assert is_valid is False, f"Email {email} should be invalid"
            assert error is not None
    
    def test_empty_email(self):
        """Test empty email."""
        is_valid, error = AuthenticationService.validate_email('')
        assert is_valid is False
        assert error == "Email is required"
    
    def test_none_email(self):
        """Test None email."""
        is_valid, error = AuthenticationService.validate_email(None)
        assert is_valid is False
        assert error == "Email is required"


class TestPasswordValidation:
    """Test suite for password validation."""
    
    def test_valid_password(self):
        """Test valid passwords."""
        valid_passwords = [
            'Password1',
            'MyPass123',
            'Secure1234',
            'Test1234',
            'Abcdefgh1',
        ]
        
        for password in valid_passwords:
            is_valid, error = AuthenticationService.validate_password(password)
            assert is_valid is True, f"Password {password} should be valid"
            assert error is None
    
    def test_password_too_short(self):
        """Test password shorter than 8 characters."""
        short_passwords = [
            'Pass1',
            'Test1',
            'Abc123',
            'A1',
        ]
        
        for password in short_passwords:
            is_valid, error = AuthenticationService.validate_password(password)
            assert is_valid is False
            assert "at least 8 characters" in error
    
    def test_password_no_uppercase(self):
        """Test password without uppercase letter."""
        no_uppercase_passwords = [
            'password1',
            'test12345',
            'mypass123',
        ]
        
        for password in no_uppercase_passwords:
            is_valid, error = AuthenticationService.validate_password(password)
            assert is_valid is False
            assert "uppercase letter" in error
    
    def test_password_no_number(self):
        """Test password without number."""
        no_number_passwords = [
            'Password',
            'MyPassword',
            'TestPass',
        ]
        
        for password in no_number_passwords:
            is_valid, error = AuthenticationService.validate_password(password)
            assert is_valid is False
            assert "number" in error
    
    def test_empty_password(self):
        """Test empty password."""
        is_valid, error = AuthenticationService.validate_password('')
        assert is_valid is False
        assert error == "Password is required"
    
    def test_none_password(self):
        """Test None password."""
        is_valid, error = AuthenticationService.validate_password(None)
        assert is_valid is False
        assert error == "Password is required"


class TestPasswordHashing:
    """Test suite for password hashing."""
    
    def test_hash_password(self):
        """Test password hashing."""
        password = 'TestPassword123'
        hashed = AuthenticationService.hash_password(password)
        
        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed != password
        assert len(hashed) > 0
    
    def test_hash_password_different_each_time(self):
        """Test that hashing same password produces different hashes (due to salt)."""
        password = 'TestPassword123'
        hash1 = AuthenticationService.hash_password(password)
        hash2 = AuthenticationService.hash_password(password)
        
        # Hashes should be different due to random salt
        assert hash1 != hash2
    
    def test_verify_password_correct(self):
        """Test verifying correct password."""
        password = 'TestPassword123'
        hashed = AuthenticationService.hash_password(password)
        
        assert AuthenticationService.verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test verifying incorrect password."""
        password = 'TestPassword123'
        wrong_password = 'WrongPassword123'
        hashed = AuthenticationService.hash_password(password)
        
        assert AuthenticationService.verify_password(wrong_password, hashed) is False


class TestUserRegistration:
    """Test suite for user registration."""
    
    def test_register_user_success(self, app):
        """Test successful user registration."""
        with app.app_context():
            user, error = AuthenticationService.register_user(
                email='newuser@example.com',
                password='Password123'
            )
            
            assert error is None
            assert user is not None
            assert user.id is not None
            assert user.email == 'newuser@example.com'
            assert user.password_hash != 'Password123'
            assert user.subscription_tier == 'free'
            
            # Verify password hash works
            assert AuthenticationService.verify_password('Password123', user.password_hash)
    
    def test_register_user_with_custom_tier(self, app):
        """Test user registration with custom subscription tier."""
        with app.app_context():
            user, error = AuthenticationService.register_user(
                email='premium@example.com',
                password='Password123',
                subscription_tier='professional'
            )
            
            assert error is None
            assert user is not None
            assert user.subscription_tier == 'professional'
    
    def test_register_user_invalid_email(self, app):
        """Test registration with invalid email."""
        with app.app_context():
            user, error = AuthenticationService.register_user(
                email='invalid-email',
                password='Password123'
            )
            
            assert user is None
            assert error is not None
            assert "email" in error.lower()
    
    def test_register_user_weak_password(self, app):
        """Test registration with weak password."""
        with app.app_context():
            # Too short
            user, error = AuthenticationService.register_user(
                email='test@example.com',
                password='Pass1'
            )
            assert user is None
            assert "8 characters" in error
            
            # No uppercase
            user, error = AuthenticationService.register_user(
                email='test@example.com',
                password='password123'
            )
            assert user is None
            assert "uppercase" in error
            
            # No number
            user, error = AuthenticationService.register_user(
                email='test@example.com',
                password='Password'
            )
            assert user is None
            assert "number" in error
    
    def test_register_user_duplicate_email(self, app):
        """Test registration with duplicate email."""
        with app.app_context():
            # Register first user
            user1, error1 = AuthenticationService.register_user(
                email='duplicate@example.com',
                password='Password123'
            )
            assert error1 is None
            assert user1 is not None
            
            # Try to register with same email
            user2, error2 = AuthenticationService.register_user(
                email='duplicate@example.com',
                password='DifferentPass123'
            )
            assert user2 is None
            assert error2 is not None
            assert "already registered" in error2.lower()
    
    def test_register_user_persists_to_database(self, app):
        """Test that registered user is persisted to database."""
        with app.app_context():
            user, error = AuthenticationService.register_user(
                email='persist@example.com',
                password='Password123'
            )
            
            assert error is None
            assert user is not None
            
            # Query database to verify persistence
            db_user = User.query.filter_by(email='persist@example.com').first()
            assert db_user is not None
            assert db_user.id == user.id
            assert db_user.email == user.email
    
    def test_register_user_bcrypt_rounds(self, app):
        """Test that password is hashed with bcrypt (12 rounds as per config)."""
        with app.app_context():
            user, error = AuthenticationService.register_user(
                email='bcrypt@example.com',
                password='Password123'
            )
            
            assert error is None
            assert user is not None
            
            # Bcrypt hashes start with $2b$ (or $2a$/$2y$) followed by cost factor
            # Format: $2b$12$... where 12 is the number of rounds
            assert user.password_hash.startswith('$2b$')
            
            # Extract cost factor (should be 12)
            parts = user.password_hash.split('$')
            cost_factor = int(parts[2])
            assert cost_factor == 12
    
    def test_register_user_empty_fields(self, app):
        """Test registration with empty fields."""
        with app.app_context():
            # Empty email
            user, error = AuthenticationService.register_user(
                email='',
                password='Password123'
            )
            assert user is None
            assert error is not None
            
            # Empty password
            user, error = AuthenticationService.register_user(
                email='test@example.com',
                password=''
            )
            assert user is None
            assert error is not None
    
    def test_register_user_case_sensitive_email(self, app):
        """Test that email comparison is case-sensitive in database."""
        with app.app_context():
            # Register with lowercase
            user1, error1 = AuthenticationService.register_user(
                email='test@example.com',
                password='Password123'
            )
            assert error1 is None
            
            # Try to register with different case
            # Note: This behavior depends on database collation
            # PostgreSQL default is case-sensitive for email comparison
            user2, error2 = AuthenticationService.register_user(
                email='Test@example.com',
                password='Password123'
            )
            
            # This test documents current behavior
            # In production, you might want case-insensitive email comparison
            if user2 is None:
                assert "already registered" in error2.lower()


class TestUserLogin:
    """Test suite for user login."""
    
    def test_login_success(self, app):
        """Test successful login."""
        with app.app_context():
            # Register a user first
            user, _ = AuthenticationService.register_user(
                email='login@example.com',
                password='Password123'
            )
            assert user is not None
            
            # Login with correct credentials
            session_data, error = AuthenticationService.login(
                email='login@example.com',
                password='Password123'
            )
            
            assert error is None
            assert session_data is not None
            assert 'token' in session_data
            assert 'user' in session_data
            assert session_data['user']['email'] == 'login@example.com'
            assert session_data['user']['subscription_tier'] == 'free'
            assert isinstance(session_data['token'], str)
            assert len(session_data['token']) > 0
    
    def test_login_invalid_email(self, app):
        """Test login with non-existent email."""
        with app.app_context():
            session_data, error = AuthenticationService.login(
                email='nonexistent@example.com',
                password='Password123'
            )
            
            assert session_data is None
            assert error is not None
            assert error == "Invalid credentials"  # Generic error message
    
    def test_login_invalid_password(self, app):
        """Test login with incorrect password."""
        with app.app_context():
            # Register a user first
            user, _ = AuthenticationService.register_user(
                email='wrongpass@example.com',
                password='Password123'
            )
            assert user is not None
            
            # Login with wrong password
            session_data, error = AuthenticationService.login(
                email='wrongpass@example.com',
                password='WrongPassword123'
            )
            
            assert session_data is None
            assert error is not None
            assert error == "Invalid credentials"  # Generic error message
    
    def test_login_empty_email(self, app):
        """Test login with empty email."""
        with app.app_context():
            session_data, error = AuthenticationService.login(
                email='',
                password='Password123'
            )
            
            assert session_data is None
            assert error == "Invalid credentials"
    
    def test_login_empty_password(self, app):
        """Test login with empty password."""
        with app.app_context():
            session_data, error = AuthenticationService.login(
                email='test@example.com',
                password=''
            )
            
            assert session_data is None
            assert error == "Invalid credentials"
    
    def test_login_generic_error_message(self, app):
        """Test that login returns generic error message for security."""
        with app.app_context():
            # Register a user
            user, _ = AuthenticationService.register_user(
                email='security@example.com',
                password='Password123'
            )
            
            # Test with wrong email
            _, error1 = AuthenticationService.login(
                email='wrong@example.com',
                password='Password123'
            )
            
            # Test with wrong password
            _, error2 = AuthenticationService.login(
                email='security@example.com',
                password='WrongPassword123'
            )
            
            # Both should return the same generic error
            assert error1 == error2 == "Invalid credentials"
    
    def test_login_updates_last_login(self, app):
        """Test that login updates last_login timestamp."""
        with app.app_context():
            # Register a user
            user, _ = AuthenticationService.register_user(
                email='timestamp@example.com',
                password='Password123'
            )
            assert user.last_login is None
            
            # Login
            session_data, error = AuthenticationService.login(
                email='timestamp@example.com',
                password='Password123'
            )
            assert error is None
            
            # Check that last_login was updated
            db.session.refresh(user)
            assert user.last_login is not None
    
    def test_login_token_stored_in_redis(self, app):
        """Test that session token is stored in Redis."""
        with app.app_context():
            from app.extensions import redis_client
            
            # Register and login
            user, _ = AuthenticationService.register_user(
                email='redis@example.com',
                password='Password123'
            )
            
            session_data, error = AuthenticationService.login(
                email='redis@example.com',
                password='Password123'
            )
            assert error is None
            
            token = session_data['token']
            
            # Check Redis
            cached_user_id = redis_client.get(f"session:{token}")
            assert cached_user_id is not None
            assert int(cached_user_id) == user.id
    
    def test_login_token_has_expiration(self, app):
        """Test that session token has 24-hour expiration in Redis."""
        with app.app_context():
            from app.extensions import redis_client
            
            # Register and login
            user, _ = AuthenticationService.register_user(
                email='expiry@example.com',
                password='Password123'
            )
            
            session_data, error = AuthenticationService.login(
                email='expiry@example.com',
                password='Password123'
            )
            assert error is None
            
            token = session_data['token']
            
            # Check TTL in Redis (should be around 24 hours = 86400 seconds)
            ttl = redis_client.ttl(f"session:{token}")
            assert ttl > 0
            assert ttl <= 86400  # 24 hours
            assert ttl > 86000  # Should be close to 24 hours


class TestSessionValidation:
    """Test suite for session validation."""
    
    def test_validate_session_success(self, app):
        """Test successful session validation."""
        with app.app_context():
            # Register and login
            user, _ = AuthenticationService.register_user(
                email='validate@example.com',
                password='Password123'
            )
            
            session_data, _ = AuthenticationService.login(
                email='validate@example.com',
                password='Password123'
            )
            
            token = session_data['token']
            
            # Validate session
            validated_user, error = AuthenticationService.validate_session(token)
            
            assert error is None
            assert validated_user is not None
            assert validated_user.id == user.id
            assert validated_user.email == user.email
    
    def test_validate_session_no_token(self, app):
        """Test validation with no token."""
        with app.app_context():
            user, error = AuthenticationService.validate_session('')
            assert user is None
            assert error == "No token provided"
            
            user, error = AuthenticationService.validate_session(None)
            assert user is None
            assert error == "No token provided"
    
    def test_validate_session_invalid_token(self, app):
        """Test validation with invalid token."""
        with app.app_context():
            user, error = AuthenticationService.validate_session('invalid-token')
            assert user is None
            assert error is not None
    
    def test_validate_session_expired_redis(self, app):
        """Test validation when session expired in Redis."""
        with app.app_context():
            from app.extensions import redis_client
            
            # Register and login
            user, _ = AuthenticationService.register_user(
                email='expired@example.com',
                password='Password123'
            )
            
            session_data, _ = AuthenticationService.login(
                email='expired@example.com',
                password='Password123'
            )
            
            token = session_data['token']
            
            # Delete from Redis to simulate expiration
            redis_client.delete(f"session:{token}")
            
            # Validate session
            validated_user, error = AuthenticationService.validate_session(token)
            
            assert validated_user is None
            assert error == "Session expired"


class TestLogout:
    """Test suite for logout."""
    
    def test_logout_success(self, app):
        """Test successful logout."""
        with app.app_context():
            from app.extensions import redis_client
            
            # Register and login
            user, _ = AuthenticationService.register_user(
                email='logout@example.com',
                password='Password123'
            )
            
            session_data, _ = AuthenticationService.login(
                email='logout@example.com',
                password='Password123'
            )
            
            token = session_data['token']
            
            # Verify session exists
            assert redis_client.get(f"session:{token}") is not None
            
            # Logout
            success, error = AuthenticationService.logout(token)
            
            assert success is True
            assert error is None
            
            # Verify session removed from Redis
            assert redis_client.get(f"session:{token}") is None
    
    def test_logout_no_token(self, app):
        """Test logout with no token."""
        with app.app_context():
            success, error = AuthenticationService.logout('')
            assert success is False
            assert error == "No token provided"
            
            success, error = AuthenticationService.logout(None)
            assert success is False
            assert error == "No token provided"
    
    def test_logout_invalid_token(self, app):
        """Test logout with invalid token (should still succeed)."""
        with app.app_context():
            # Logout with non-existent token should succeed
            # (idempotent operation)
            success, error = AuthenticationService.logout('nonexistent-token')
            assert success is True
            assert error is None


class TestRateLimiting:
    """Test suite for login rate limiting."""
    
    def test_rate_limit_allows_initial_attempts(self, app):
        """Test that rate limiting allows first few attempts."""
        with app.app_context():
            ip_address = '192.168.1.100'
            
            # First 5 attempts should be allowed
            for i in range(5):
                is_allowed, error = AuthenticationService.check_rate_limit(ip_address)
                assert is_allowed is True
                assert error is None
                
                # Record failed attempt
                AuthenticationService.record_failed_login(ip_address)
    
    def test_rate_limit_blocks_after_5_attempts(self, app):
        """Test that rate limiting blocks after 5 failed attempts."""
        with app.app_context():
            from app.extensions import redis_client
            ip_address = '192.168.1.101'
            
            # Make 5 failed attempts
            for i in range(5):
                AuthenticationService.record_failed_login(ip_address)
            
            # 6th attempt should be blocked
            is_allowed, error = AuthenticationService.check_rate_limit(ip_address)
            assert is_allowed is False
            assert error is not None
            assert "Too many failed login attempts" in error
            assert "minute" in error
    
    def test_rate_limit_login_integration(self, app):
        """Test rate limiting integrated with login flow."""
        with app.app_context():
            # Register a user
            user, _ = AuthenticationService.register_user(
                email='ratelimit@example.com',
                password='Password123'
            )
            assert user is not None
            
            ip_address = '192.168.1.102'
            
            # Make 5 failed login attempts
            for i in range(5):
                session_data, error = AuthenticationService.login(
                    email='ratelimit@example.com',
                    password='WrongPassword',
                    ip_address=ip_address
                )
                assert session_data is None
                assert error == "Invalid credentials"
            
            # 6th attempt should be rate limited
            session_data, error = AuthenticationService.login(
                email='ratelimit@example.com',
                password='WrongPassword',
                ip_address=ip_address
            )
            assert session_data is None
            assert "Too many failed login attempts" in error
    
    def test_rate_limit_resets_on_successful_login(self, app):
        """Test that rate limit resets after successful login."""
        with app.app_context():
            # Register a user
            user, _ = AuthenticationService.register_user(
                email='resetlimit@example.com',
                password='Password123'
            )
            assert user is not None
            
            ip_address = '192.168.1.103'
            
            # Make 3 failed attempts
            for i in range(3):
                AuthenticationService.login(
                    email='resetlimit@example.com',
                    password='WrongPassword',
                    ip_address=ip_address
                )
            
            # Successful login should reset the counter
            session_data, error = AuthenticationService.login(
                email='resetlimit@example.com',
                password='Password123',
                ip_address=ip_address
            )
            assert error is None
            assert session_data is not None
            
            # Should be able to make failed attempts again
            for i in range(5):
                is_allowed, error = AuthenticationService.check_rate_limit(ip_address)
                assert is_allowed is True
                AuthenticationService.record_failed_login(ip_address)
    
    def test_rate_limit_expires_after_15_minutes(self, app):
        """Test that rate limit has 15-minute expiration."""
        with app.app_context():
            from app.extensions import redis_client
            ip_address = '192.168.1.104'
            
            # Record a failed attempt
            AuthenticationService.record_failed_login(ip_address)
            
            # Check TTL (should be around 900 seconds = 15 minutes)
            rate_limit_key = f"rate_limit:login:{ip_address}"
            ttl = redis_client.ttl(rate_limit_key)
            
            assert ttl > 0
            assert ttl <= 900  # 15 minutes
            assert ttl > 890  # Should be close to 15 minutes
    
    def test_rate_limit_different_ips_independent(self, app):
        """Test that rate limits are independent per IP address."""
        with app.app_context():
            ip1 = '192.168.1.105'
            ip2 = '192.168.1.106'
            
            # Block IP1
            for i in range(5):
                AuthenticationService.record_failed_login(ip1)
            
            # IP1 should be blocked
            is_allowed, error = AuthenticationService.check_rate_limit(ip1)
            assert is_allowed is False
            
            # IP2 should still be allowed
            is_allowed, error = AuthenticationService.check_rate_limit(ip2)
            assert is_allowed is True
    
    def test_rate_limit_without_ip_address(self, app):
        """Test that rate limiting handles missing IP address gracefully."""
        with app.app_context():
            # Register a user
            user, _ = AuthenticationService.register_user(
                email='noip@example.com',
                password='Password123'
            )
            
            # Login without IP address should work
            session_data, error = AuthenticationService.login(
                email='noip@example.com',
                password='Password123',
                ip_address=None
            )
            assert error is None
            assert session_data is not None
            
            # Failed login without IP should also work
            session_data, error = AuthenticationService.login(
                email='noip@example.com',
                password='WrongPassword',
                ip_address=None
            )
            assert session_data is None
            assert error == "Invalid credentials"
    
    def test_rate_limit_empty_ip_address(self, app):
        """Test that rate limiting handles empty IP address."""
        with app.app_context():
            # Empty IP should be allowed
            is_allowed, error = AuthenticationService.check_rate_limit('')
            assert is_allowed is True
            assert error is None
            
            # Recording with empty IP should not crash
            AuthenticationService.record_failed_login('')
            AuthenticationService.reset_rate_limit('')
    
    def test_rate_limit_counter_increments_correctly(self, app):
        """Test that failed attempt counter increments correctly."""
        with app.app_context():
            from app.extensions import redis_client
            ip_address = '192.168.1.107'
            rate_limit_key = f"rate_limit:login:{ip_address}"
            
            # Record attempts and verify counter
            for expected_count in range(1, 6):
                AuthenticationService.record_failed_login(ip_address)
                actual_count = int(redis_client.get(rate_limit_key))
                assert actual_count == expected_count
    
    def test_rate_limit_error_message_includes_time(self, app):
        """Test that rate limit error message includes time remaining."""
        with app.app_context():
            ip_address = '192.168.1.108'
            
            # Block the IP
            for i in range(5):
                AuthenticationService.record_failed_login(ip_address)
            
            # Check error message
            is_allowed, error = AuthenticationService.check_rate_limit(ip_address)
            assert is_allowed is False
            assert "minute" in error.lower()
            # Should mention time remaining
            assert any(char.isdigit() for char in error)
