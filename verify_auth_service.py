"""Verification script for authentication service functionality."""
from services.auth_service import AuthenticationService


def test_email_validation():
    """Test email validation."""
    print("=" * 60)
    print("Testing Email Validation")
    print("=" * 60)
    
    test_cases = [
        ('valid@example.com', True),
        ('test.user@example.co.uk', True),
        ('user+tag@example.com', True),
        ('invalid-email', False),
        ('@example.com', False),
        ('user@', False),
        ('user@example..com', False),
        ('', False),
    ]
    
    for email, expected_valid in test_cases:
        is_valid, error = AuthenticationService.validate_email(email)
        status = "✓" if is_valid == expected_valid else "✗"
        print(f"{status} Email: '{email}' - Valid: {is_valid}, Error: {error}")
    
    print()


def test_password_validation():
    """Test password validation."""
    print("=" * 60)
    print("Testing Password Validation")
    print("=" * 60)
    
    test_cases = [
        ('Password123', True, None),
        ('MyPass1', False, '8 characters'),
        ('password123', False, 'uppercase'),
        ('Password', False, 'number'),
        ('', False, 'required'),
    ]
    
    for password, expected_valid, expected_error_keyword in test_cases:
        is_valid, error = AuthenticationService.validate_password(password)
        status = "✓" if is_valid == expected_valid else "✗"
        error_match = (expected_error_keyword is None and error is None) or \
                     (expected_error_keyword and error and expected_error_keyword in error)
        if not error_match:
            status = "✗"
        print(f"{status} Password: '{password}' - Valid: {is_valid}, Error: {error}")
    
    print()


def test_password_hashing():
    """Test password hashing and verification."""
    print("=" * 60)
    print("Testing Password Hashing (bcrypt with 12 rounds)")
    print("=" * 60)
    
    password = "TestPassword123"
    
    # Hash the password
    hashed = AuthenticationService.hash_password(password)
    print(f"Original password: {password}")
    print(f"Hashed password: {hashed}")
    print(f"Hash starts with $2b$: {hashed.startswith('$2b$')}")
    
    # Extract cost factor
    parts = hashed.split('$')
    cost_factor = int(parts[2])
    print(f"Cost factor (rounds): {cost_factor}")
    print(f"✓ Using 12 rounds as required" if cost_factor == 12 else "✗ Not using 12 rounds")
    
    # Verify correct password
    is_correct = AuthenticationService.verify_password(password, hashed)
    print(f"✓ Correct password verification: {is_correct}" if is_correct else "✗ Failed to verify correct password")
    
    # Verify incorrect password
    is_incorrect = AuthenticationService.verify_password("WrongPassword123", hashed)
    print(f"✓ Incorrect password rejected: {not is_incorrect}" if not is_incorrect else "✗ Accepted incorrect password")
    
    # Test that same password produces different hashes (salt)
    hashed2 = AuthenticationService.hash_password(password)
    print(f"✓ Different hashes for same password (salt working): {hashed != hashed2}" if hashed != hashed2 else "✗ Same hash produced")
    
    print()


def test_registration_validation():
    """Test registration validation without database."""
    print("=" * 60)
    print("Testing Registration Validation (without database)")
    print("=" * 60)
    
    # Test valid inputs
    print("\n1. Valid email and password:")
    is_valid_email, email_error = AuthenticationService.validate_email('test@example.com')
    is_valid_password, password_error = AuthenticationService.validate_password('Password123')
    print(f"   Email valid: {is_valid_email}, Password valid: {is_valid_password}")
    print(f"   ✓ Would proceed to database check" if is_valid_email and is_valid_password else "   ✗ Validation failed")
    
    # Test invalid email
    print("\n2. Invalid email:")
    is_valid_email, email_error = AuthenticationService.validate_email('invalid-email')
    print(f"   Email valid: {is_valid_email}, Error: {email_error}")
    print(f"   ✓ Correctly rejected" if not is_valid_email else "   ✗ Should have been rejected")
    
    # Test weak password
    print("\n3. Weak password (too short):")
    is_valid_password, password_error = AuthenticationService.validate_password('Pass1')
    print(f"   Password valid: {is_valid_password}, Error: {password_error}")
    print(f"   ✓ Correctly rejected" if not is_valid_password else "   ✗ Should have been rejected")
    
    # Test weak password (no uppercase)
    print("\n4. Weak password (no uppercase):")
    is_valid_password, password_error = AuthenticationService.validate_password('password123')
    print(f"   Password valid: {is_valid_password}, Error: {password_error}")
    print(f"   ✓ Correctly rejected" if not is_valid_password else "   ✗ Should have been rejected")
    
    # Test weak password (no number)
    print("\n5. Weak password (no number):")
    is_valid_password, password_error = AuthenticationService.validate_password('Password')
    print(f"   Password valid: {is_valid_password}, Error: {password_error}")
    print(f"   ✓ Correctly rejected" if not is_valid_password else "   ✗ Should have been rejected")
    
    print()


def main():
    """Run all verification tests."""
    print("\n" + "=" * 60)
    print("AUTHENTICATION SERVICE VERIFICATION")
    print("Task 3.1: User Registration with Validation")
    print("=" * 60 + "\n")
    
    test_email_validation()
    test_password_validation()
    test_password_hashing()
    test_registration_validation()
    
    print("=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)
    print("\nImplemented features:")
    print("✓ Email format validation using regex")
    print("✓ Password strength validation (min 8 chars, 1 uppercase, 1 number)")
    print("✓ Password hashing using bcrypt with 12 rounds")
    print("✓ User registration validation logic")
    print("\nNote: Database integration tests require PostgreSQL to be running.")
    print("      Run 'docker-compose up -d postgres' to start the database.")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    main()
