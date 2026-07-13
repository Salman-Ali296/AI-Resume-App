# Database Migrations

This directory contains database migration scripts for the Resume Analyzer application.

## Migration Files

### 001_create_users_table.py
Creates the `users` table with the following fields:
- `id`: Primary key (auto-incrementing integer)
- `email`: Unique email address (indexed)
- `password_hash`: Hashed password for authentication
- `oauth_provider`: OAuth provider name (e.g., 'google', 'linkedin')
- `oauth_id`: OAuth provider's user ID
- `subscription_tier`: User's subscription level ('free', 'professional', 'enterprise')
- `created_at`: Timestamp when user was created
- `updated_at`: Timestamp when user was last updated
- `last_login`: Timestamp of last login

**Indexes:**
- `idx_users_email`: Unique index on email field
- `idx_users_oauth`: Composite index on (oauth_provider, oauth_id)

## Applying Migrations

### Option 1: Using Flask-Migrate (Recommended)

```bash
# Initialize migrations (first time only)
flask db init

# Create a new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback migrations
flask db downgrade
```

### Option 2: Using the Direct Migration Script

If Flask-Migrate is not available or you need to apply migrations directly:

```bash
python migrations/apply_migration.py
```

This script will:
1. Connect to the database using the configuration from `config.py`
2. Create the users table if it doesn't exist
3. Create the necessary indexes
4. Report success or any errors

## Migration Best Practices

1. **Always test migrations** in a development environment before applying to production
2. **Backup your database** before running migrations in production
3. **Review migration SQL** to ensure it matches your expectations
4. **Use transactions** to ensure migrations can be rolled back if they fail
5. **Document changes** in migration commit messages

## Database Schema

The current schema includes:

- **users**: User authentication and profile information

Future migrations will add:
- **api_keys**: API key management
- **resumes**: Resume file storage and metadata
- **analyses**: Resume analysis results
- **usage_tracking**: Usage limits and billing
- **contact_submissions**: Support and feedback
- **skill_taxonomy**: Skill categorization and synonyms
- **audit_log**: Security and access logging
