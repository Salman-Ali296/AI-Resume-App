"""Authentication service for user registration and login."""
import re
import jwt
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict
from models.user import User
from app.extensions import db, bcrypt
from app import extensions
from flask import current_app


class AuthError(Exception):
    """Base exception for authentication errors."""
    pass


class ValidationError(AuthError):
    """Exception for validation errors."""
    pass


class AuthenticationService:
    """Service for handling user authentication operations."""
    
    # Email validation regex (RFC 5322 simplified)
    # Prevents consecutive dots and ensures proper domain structure
    EMAIL_REGEX = re.compile(
        r'^[a-zA-Z0-9][a-zA-Z0-9._%+-]*[a-zA-Z0-9]@[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$|^[a-zA-Z0-9]@[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$'
    )
    
    # Password validation requirements
    MIN_PASSWORD_LENGTH = 8
    PASSWORD_UPPERCASE_REGEX = re.compile(r'[A-Z]')
    PASSWORD_NUMBER_REGEX = re.compile(r'\d')
    
    @classmethod
    def validate_email(cls, email: str) -> Tuple[bool, Optional[str]]:
        """Validate email format.
        
        Args:
            email: Email address to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email:
            return False, "Email is required"
        
        if not cls.EMAIL_REGEX.match(email):
            return False, "Invalid email format"
        
        return True, None
    
    @classmethod
    def validate_password(cls, password: str) -> Tuple[bool, Optional[str]]:
        """Validate password strength.
        
        Requirements:
        - Minimum 8 characters
        - At least 1 uppercase letter
        - At least 1 number
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not password:
            return False, "Password is required"
        
        if len(password) < cls.MIN_PASSWORD_LENGTH:
            return False, f"Password must be at least {cls.MIN_PASSWORD_LENGTH} characters"
        
        if not cls.PASSWORD_UPPERCASE_REGEX.search(password):
            return False, "Password must contain at least 1 uppercase letter"
        
        if not cls.PASSWORD_NUMBER_REGEX.search(password):
            return False, "Password must contain at least 1 number"
        
        return True, None
    
    @classmethod
    def hash_password(cls, password: str) -> str:
        """Hash password using bcrypt with 12 rounds.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        return bcrypt.generate_password_hash(password).decode('utf-8')
    
    @classmethod
    def verify_password(cls, password: str, password_hash: str) -> bool:
        """Verify password against hash.
        
        Args:
            password: Plain text password
            password_hash: Hashed password
            
        Returns:
            True if password matches, False otherwise
        """
        return bcrypt.check_password_hash(password_hash, password)
    
    @classmethod
    def register_user(
        cls,
        email: str,
        password: str,
        subscription_tier: str = 'free'
    ) -> Tuple[Optional[User], Optional[str]]:
        """Register a new user with validation.
        
        Args:
            email: User email address
            password: User password (plain text)
            subscription_tier: Subscription tier (default: 'free')
            
        Returns:
            Tuple of (user, error_message)
            If successful, returns (User object, None)
            If failed, returns (None, error_message)
        """
        # Validate email
        is_valid, error = cls.validate_email(email)
        if not is_valid:
            return None, error
        
        # Validate password
        is_valid, error = cls.validate_password(password)
        if not is_valid:
            return None, error
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return None, "Email already registered"
        
        # Hash password
        password_hash = cls.hash_password(password)
        
        # Create user record
        try:
            user = User(
                email=email,
                password_hash=password_hash,
                subscription_tier=subscription_tier
            )
            db.session.add(user)
            db.session.commit()
            
            return user, None
            
        except Exception as e:
            db.session.rollback()
            return None, f"Failed to create user: {str(e)}"
    
    @classmethod
    def check_rate_limit(cls, ip_address: str) -> Tuple[bool, Optional[str]]:
        """Check if IP address has exceeded login rate limit.
        
        Rate limit: 5 failed attempts per 15 minutes per IP
        
        Args:
            ip_address: Client IP address
            
        Returns:
            Tuple of (is_allowed, error_message)
            If allowed, returns (True, None)
            If rate limited, returns (False, error_message)
        """
        if not ip_address:
            return True, None
        
        rate_limit_key = f"rate_limit:login:{ip_address}"
        
        try:
            # Get current attempt count
            attempts = extensions.redis_client.get(rate_limit_key)
            attempts = int(attempts) if attempts else 0
            
            # Check if limit exceeded (5 attempts)
            if attempts >= 5:
                # Get TTL to inform user when they can try again
                ttl = extensions.redis_client.ttl(rate_limit_key)
                minutes = max(1, ttl // 60)
                return False, f"Too many failed login attempts. Please try again in {minutes} minute(s)."
            
            return True, None
            
        except Exception as e:
            current_app.logger.error(f"Rate limit check error: {e}")
            # On error, allow the request (fail open)
            return True, None
    
    @classmethod
    def record_failed_login(cls, ip_address: str) -> None:
        """Record a failed login attempt for rate limiting.
        
        Args:
            ip_address: Client IP address
        """
        if not ip_address:
            return
        
        rate_limit_key = f"rate_limit:login:{ip_address}"
        
        try:
            # Increment attempt count
            attempts = extensions.redis_client.incr(rate_limit_key)
            
            # Set expiration to 15 minutes (900 seconds) on first attempt
            if attempts == 1:
                extensions.redis_client.expire(rate_limit_key, 900)
                
        except Exception as e:
            current_app.logger.error(f"Failed to record login attempt: {e}")
    
    @classmethod
    def reset_rate_limit(cls, ip_address: str) -> None:
        """Reset rate limit for IP address after successful login.
        
        Args:
            ip_address: Client IP address
        """
        if not ip_address:
            return
        
        rate_limit_key = f"rate_limit:login:{ip_address}"
        
        try:
            extensions.redis_client.delete(rate_limit_key)
        except Exception as e:
            current_app.logger.error(f"Failed to reset rate limit: {e}")
    
    @classmethod
    def login(
        cls,
        email: str,
        password: str,
        ip_address: Optional[str] = None
    ) -> Tuple[Optional[Dict], Optional[str]]:
        """Authenticate user and create session.
        
        Args:
            email: User email address
            password: User password (plain text)
            ip_address: Client IP address for rate limiting (optional)
            
        Returns:
            Tuple of (session_data, error_message)
            If successful, returns (dict with token and user info, None)
            If failed, returns (None, generic error message)
        """
        # Check rate limit
        is_allowed, rate_limit_error = cls.check_rate_limit(ip_address)
        if not is_allowed:
            return None, rate_limit_error
        
        # Validate inputs
        if not email or not password:
            cls.record_failed_login(ip_address)
            return None, "Invalid credentials"
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        # Generic error message for security (don't reveal which credential is wrong)
        if not user:
            cls.record_failed_login(ip_address)
            return None, "Invalid credentials"
        
        # Verify password
        if not cls.verify_password(password, user.password_hash):
            cls.record_failed_login(ip_address)
            return None, "Invalid credentials"
        
        # Reset rate limit on successful login
        cls.reset_rate_limit(ip_address)
        
        # Generate JWT token
        token = cls.generate_session_token(user.id)
        
        # Store session in Redis with 24-hour expiration
        cls.store_session(token, user.id)
        
        # Update last login timestamp
        try:
            user.last_login = datetime.utcnow()
            db.session.commit()
        except Exception as e:
            # Log error but don't fail login
            current_app.logger.warning(f"Failed to update last_login for user {user.id}: {e}")
        
        # Return session data
        session_data = {
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email,
                'subscription_tier': user.subscription_tier
            }
        }
        
        return session_data, None
    
    @classmethod
    def generate_session_token(cls, user_id: int) -> str:
        """Generate JWT session token with 24-hour expiration.
        
        Args:
            user_id: User ID to encode in token
            
        Returns:
            JWT token string
        """
        expiration = datetime.utcnow() + timedelta(hours=current_app.config['JWT_EXPIRATION_HOURS'])
        
        payload = {
            'user_id': user_id,
            'exp': expiration,
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(
            payload,
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        
        return token
    
    @classmethod
    def store_session(cls, token: str, user_id: int) -> None:
        """Store session token in Redis cache.
        
        Args:
            token: JWT token
            user_id: User ID
        """
        # Store with 24-hour TTL
        ttl = current_app.config['JWT_EXPIRATION_HOURS'] * 3600
        extensions.redis_client.setex(
            f"session:{token}",
            ttl,
            str(user_id)
        )
    
    @classmethod
    def validate_session(cls, token: str) -> Tuple[Optional[User], Optional[str]]:
        """Validate session token and return user.
        
        Args:
            token: JWT token
            
        Returns:
            Tuple of (user, error_message)
            If valid, returns (User object, None)
            If invalid, returns (None, error_message)
        """
        if not token:
            return None, "No token provided"
        
        try:
            # Decode JWT token
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            
            user_id = payload.get('user_id')
            if not user_id:
                return None, "Invalid token"
            
            # Check if session exists in Redis
            cached_user_id = extensions.redis_client.get(f"session:{token}")
            if not cached_user_id:
                return None, "Session expired"
            
            # Verify user_id matches
            if str(user_id) != cached_user_id:
                return None, "Invalid session"
            
            # Get user from database
            user = User.query.get(user_id)
            if not user:
                return None, "User not found"
            
            return user, None
            
        except jwt.ExpiredSignatureError:
            return None, "Token expired"
        except jwt.InvalidTokenError:
            return None, "Invalid token"
        except Exception as e:
            current_app.logger.error(f"Session validation error: {e}")
            return None, "Session validation failed"
    
    @classmethod
    def logout(cls, token: str) -> Tuple[bool, Optional[str]]:
        """Logout user by removing session from Redis.
        
        Args:
            token: JWT token
            
        Returns:
            Tuple of (success, error_message)
        """
        if not token:
            return False, "No token provided"
        
        try:
            # Remove session from Redis
            redis_client.delete(f"session:{token}")
            return True, None
        except Exception as e:
            current_app.logger.error(f"Logout error: {e}")
            return False, "Logout failed"
    
    @classmethod
    def generate_reset_token(cls) -> str:
        """Generate a secure random reset token.
        
        Returns:
            32-byte URL-safe token string
        """
        return secrets.token_urlsafe(32)
    
    @classmethod
    def hash_reset_token(cls, token: str) -> str:
        """Hash reset token for secure storage.
        
        Args:
            token: Plain text reset token
            
        Returns:
            Hashed token
        """
        return bcrypt.generate_password_hash(token).decode('utf-8')
    
    @classmethod
    def verify_reset_token(cls, token: str, token_hash: str) -> bool:
        """Verify reset token against hash.
        
        Args:
            token: Plain text reset token
            token_hash: Hashed token
            
        Returns:
            True if token matches, False otherwise
        """
        return bcrypt.check_password_hash(token_hash, token)
    
    @classmethod
    def request_password_reset(cls, email: str) -> Tuple[Optional[str], Optional[str]]:
        """Generate password reset token for user.
        
        Args:
            email: User email address
            
        Returns:
            Tuple of (reset_token, error_message)
            If successful, returns (token string, None)
            If failed, returns (None, error_message)
            
        Note:
            For security, this method returns success even if email doesn't exist
            to prevent email enumeration attacks. The actual token is only returned
            if the email exists.
        """
        # Validate email format
        is_valid, error = cls.validate_email(email)
        if not is_valid:
            return None, error
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        # For security, don't reveal if email exists
        # Return success message but only generate token if user exists
        if not user:
            # Return None token but no error (security measure)
            return None, None
        
        try:
            # Generate reset token
            reset_token = cls.generate_reset_token()
            
            # Hash token for storage
            token_hash = cls.hash_reset_token(reset_token)
            
            # Set expiration to 1 hour from now
            expiration = datetime.utcnow() + timedelta(hours=1)
            
            # Store hashed token and expiration in database
            user.reset_token_hash = token_hash
            user.reset_token_expires = expiration
            db.session.commit()
            
            return reset_token, None
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to generate reset token: {e}")
            return None, "Failed to generate reset token"
    
    @classmethod
    def validate_reset_token(cls, email: str, token: str) -> Tuple[Optional[User], Optional[str]]:
        """Validate password reset token.
        
        Args:
            email: User email address
            token: Reset token
            
        Returns:
            Tuple of (user, error_message)
            If valid, returns (User object, None)
            If invalid, returns (None, error_message)
        """
        if not email or not token:
            return None, "Email and token are required"
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        if not user:
            return None, "Invalid reset token"
        
        # Check if token exists
        if not user.reset_token_hash:
            return None, "Invalid reset token"
        
        # Check if token is expired
        if not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
            return None, "Reset token has expired"
        
        # Verify token
        if not cls.verify_reset_token(token, user.reset_token_hash):
            return None, "Invalid reset token"
        
        return user, None
    
    @classmethod
    def reset_password(
        cls,
        email: str,
        token: str,
        new_password: str
    ) -> Tuple[bool, Optional[str]]:
        """Reset user password using reset token.
        
        Args:
            email: User email address
            token: Reset token
            new_password: New password (plain text)
            
        Returns:
            Tuple of (success, error_message)
            If successful, returns (True, None)
            If failed, returns (False, error_message)
        """
        # Validate new password
        is_valid, error = cls.validate_password(new_password)
        if not is_valid:
            return False, error
        
        # Validate reset token
        user, error = cls.validate_reset_token(email, token)
        if error:
            return False, error
        
        try:
            # Hash new password
            password_hash = cls.hash_password(new_password)
            
            # Update password
            user.password_hash = password_hash
            
            # Clear reset token fields
            user.reset_token_hash = None
            user.reset_token_expires = None
            
            # Update timestamp
            user.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return True, None
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to reset password: {e}")
            return False, "Failed to reset password"
    
    @classmethod
    def send_reset_email(cls, email: str, reset_token: str) -> bool:
        """Send password reset email with token link.
        
        Args:
            email: User email address
            reset_token: Reset token to include in email
            
        Returns:
            True if email sent successfully, False otherwise
            
        Note:
            This is a placeholder implementation. In production, this should
            integrate with an email service (SendGrid, AWS SES, etc.)
        """
        try:
            # Construct reset link
            # In production, this should use the actual frontend URL
            base_url = current_app.config.get('FRONTEND_URL', 'http://localhost:3000')
            reset_link = f"{base_url}/reset-password?email={email}&token={reset_token}"
            
            # Log the reset link (in production, send actual email)
            current_app.logger.info(f"Password reset link for {email}: {reset_link}")
            
            # TODO: Integrate with email service
            # Example:
            # send_email(
            #     to=email,
            #     subject="Password Reset Request",
            #     body=f"Click here to reset your password: {reset_link}"
            # )
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"Failed to send reset email: {e}")
            return False

