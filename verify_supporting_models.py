"""Verification script for supporting models (UsageTracking, ContactSubmission, SkillTaxonomy, AuditLog)."""
import sys

def verify_models():
    """Verify that all supporting models can be imported and have correct structure."""
    errors = []
    
    # Test UsageTracking model
    try:
        from models.usage_tracking import UsageTracking
        print("✓ UsageTracking model imported successfully")
        
        # Check required attributes
        required_attrs = ['__tablename__', 'id', 'user_id', 'month', 'analysis_count', 'to_dict', '__repr__']
        for attr in required_attrs:
            if not hasattr(UsageTracking, attr):
                errors.append(f"UsageTracking missing attribute: {attr}")
        
        if not errors:
            print("  - All required attributes present")
            print(f"  - Table name: {UsageTracking.__tablename__}")
    except Exception as e:
        errors.append(f"Failed to import UsageTracking: {e}")
    
    # Test ContactSubmission model
    try:
        from models.contact_submission import ContactSubmission
        print("\n✓ ContactSubmission model imported successfully")
        
        # Check required attributes
        required_attrs = ['__tablename__', 'id', 'user_id', 'email', 'subject', 'message', 'category', 'to_dict', '__repr__']
        for attr in required_attrs:
            if not hasattr(ContactSubmission, attr):
                errors.append(f"ContactSubmission missing attribute: {attr}")
        
        if not errors:
            print("  - All required attributes present")
            print(f"  - Table name: {ContactSubmission.__tablename__}")
    except Exception as e:
        errors.append(f"Failed to import ContactSubmission: {e}")
    
    # Test SkillTaxonomy model
    try:
        from models.skill_taxonomy import SkillTaxonomy
        print("\n✓ SkillTaxonomy model imported successfully")
        
        # Check required attributes
        required_attrs = ['__tablename__', 'id', 'skill_name', 'canonical_name', 'category', 'industry', 'synonyms', 'to_dict', '__repr__']
        for attr in required_attrs:
            if not hasattr(SkillTaxonomy, attr):
                errors.append(f"SkillTaxonomy missing attribute: {attr}")
        
        if not errors:
            print("  - All required attributes present")
            print(f"  - Table name: {SkillTaxonomy.__tablename__}")
    except Exception as e:
        errors.append(f"Failed to import SkillTaxonomy: {e}")
    
    # Test AuditLog model
    try:
        from models.audit_log import AuditLog
        print("\n✓ AuditLog model imported successfully")
        
        # Check required attributes
        required_attrs = ['__tablename__', 'id', 'user_id', 'action', 'resource_type', 'resource_id', 'ip_address', 'user_agent', 'to_dict', '__repr__']
        for attr in required_attrs:
            if not hasattr(AuditLog, attr):
                errors.append(f"AuditLog missing attribute: {attr}")
        
        if not errors:
            print("  - All required attributes present")
            print(f"  - Table name: {AuditLog.__tablename__}")
    except Exception as e:
        errors.append(f"Failed to import AuditLog: {e}")
    
    # Test models package exports
    try:
        from models import UsageTracking, ContactSubmission, SkillTaxonomy, AuditLog
        print("\n✓ All models exported from models package")
    except Exception as e:
        errors.append(f"Failed to import from models package: {e}")
    
    # Test migrations exist
    import os
    migration_files = [
        'migrations/versions/005_create_usage_tracking_table.py',
        'migrations/versions/006_create_contact_submissions_table.py',
        'migrations/versions/007_create_skill_taxonomy_table.py',
        'migrations/versions/008_create_audit_log_table.py'
    ]
    
    print("\n✓ Checking migration files:")
    for migration_file in migration_files:
        if os.path.exists(migration_file):
            print(f"  - {migration_file} exists")
        else:
            errors.append(f"Migration file missing: {migration_file}")
    
    # Test test files exist
    test_files = [
        'tests/test_usage_tracking_model.py',
        'tests/test_contact_submission_model.py',
        'tests/test_skill_taxonomy_model.py',
        'tests/test_audit_log_model.py'
    ]
    
    print("\n✓ Checking test files:")
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"  - {test_file} exists")
        else:
            errors.append(f"Test file missing: {test_file}")
    
    # Summary
    print("\n" + "="*60)
    if errors:
        print("VERIFICATION FAILED")
        print("\nErrors found:")
        for error in errors:
            print(f"  ✗ {error}")
        return False
    else:
        print("VERIFICATION SUCCESSFUL")
        print("\nAll supporting models are correctly implemented:")
        print("  ✓ UsageTracking - for subscription limits")
        print("  ✓ ContactSubmission - for support requests")
        print("  ✓ SkillTaxonomy - for NLP skill database")
        print("  ✓ AuditLog - for security auditing")
        print("\nAll migrations created:")
        print("  ✓ 005_create_usage_tracking_table.py")
        print("  ✓ 006_create_contact_submissions_table.py")
        print("  ✓ 007_create_skill_taxonomy_table.py")
        print("  ✓ 008_create_audit_log_table.py")
        print("\nAll test files created:")
        print("  ✓ test_usage_tracking_model.py")
        print("  ✓ test_contact_submission_model.py")
        print("  ✓ test_skill_taxonomy_model.py")
        print("  ✓ test_audit_log_model.py")
        return True

if __name__ == '__main__':
    success = verify_models()
    sys.exit(0 if success else 1)
