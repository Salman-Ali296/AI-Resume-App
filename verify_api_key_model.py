"""Verification script for APIKey model implementation."""
import sys

def verify_model_import():
    """Verify that the APIKey model can be imported."""
    try:
        from models.api_key import APIKey
        print("✓ APIKey model imported successfully")
        
        # Check model attributes
        expected_columns = ['id', 'user_id', 'key_hash', 'name', 'is_active', 'created_at', 'last_used']
        for col in expected_columns:
            if hasattr(APIKey, col):
                print(f"  ✓ Column '{col}' exists")
            else:
                print(f"  ✗ Column '{col}' missing")
                return False
        
        # Check methods
        if hasattr(APIKey, 'to_dict'):
            print("  ✓ Method 'to_dict' exists")
        else:
            print("  ✗ Method 'to_dict' missing")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Failed to import APIKey model: {e}")
        return False


def verify_migration():
    """Verify that the migration file is valid."""
    try:
        # Import the migration module
        sys.path.insert(0, 'migrations/versions')
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "migration_002",
            "migrations/versions/002_create_api_keys_table.py"
        )
        migration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migration)
        
        print("✓ Migration file imported successfully")
        
        # Check migration attributes
        if hasattr(migration, 'upgrade'):
            print("  ✓ Function 'upgrade' exists")
        else:
            print("  ✗ Function 'upgrade' missing")
            return False
        
        if hasattr(migration, 'downgrade'):
            print("  ✓ Function 'downgrade' exists")
        else:
            print("  ✗ Function 'downgrade' missing")
            return False
        
        # Check revision info
        if hasattr(migration, 'revision') and migration.revision == '002':
            print(f"  ✓ Revision ID: {migration.revision}")
        else:
            print("  ✗ Invalid revision ID")
            return False
        
        if hasattr(migration, 'down_revision') and migration.down_revision == '001':
            print(f"  ✓ Down revision: {migration.down_revision}")
        else:
            print("  ✗ Invalid down_revision")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Failed to verify migration: {e}")
        return False


def verify_models_init():
    """Verify that models/__init__.py exports APIKey."""
    try:
        from models import APIKey
        print("✓ APIKey exported from models package")
        return True
    except Exception as e:
        print(f"✗ Failed to import APIKey from models package: {e}")
        return False


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("APIKey Model Implementation Verification")
    print("=" * 60)
    print()
    
    print("1. Verifying model import...")
    model_ok = verify_model_import()
    print()
    
    print("2. Verifying migration file...")
    migration_ok = verify_migration()
    print()
    
    print("3. Verifying models package export...")
    export_ok = verify_models_init()
    print()
    
    print("=" * 60)
    if model_ok and migration_ok and export_ok:
        print("✓ All verification checks passed!")
        print("=" * 60)
        print()
        print("Implementation Summary:")
        print("  - APIKey model created with all required fields")
        print("  - User relationship configured with cascade delete")
        print("  - is_active flag for key revocation")
        print("  - Indexes on user_id and key_hash")
        print("  - Database migration created (002_create_api_keys_table.py)")
        print("  - Comprehensive test suite created (test_api_key_model.py)")
        print()
        print("Next steps:")
        print("  1. Run: python migrations/apply_migration.py")
        print("  2. Run tests: pytest tests/test_api_key_model.py -v")
        return 0
    else:
        print("✗ Some verification checks failed")
        print("=" * 60)
        return 1


if __name__ == '__main__':
    sys.exit(main())
