# Database Models

This directory contains SQLAlchemy models for the Resume Analyzer application.

## User Model

**File:** `user.py`

The User model handles authentication and user management for the application.

### Fields

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | Integer | Primary key | Auto-increment |
| `email` | String(255) | User's email address | Unique, Not Null, Indexed |
| `password_hash` | String(255) | Bcrypt hashed password | Not Null |
| `oauth_provider` | String(50) | OAuth provider name | Nullable |
| `oauth_id` | String(255) | OAuth provider user ID | Nullable |
| `subscription_tier` | String(50) | Subscription level | Not Null, Default: 'free' |
| `created_at` | DateTime | Account creation timestamp | Not Null, Auto-set |
| `updated_at` | DateTime | Last update timestamp | Not Null, Auto-update |
| `last_login` | DateTime | Last login timestamp | Nullable |

### Subscription Tiers

- **free**: 5 resume analyses per month
- **professional**: 50 resume analyses per month
- **enterprise**: Unlimited analyses

### OAuth Support

The User model supports OAuth authentication through:
- Google OAuth
- LinkedIn OAuth

When using OAuth, the `oauth_provider` and `oauth_id` fields store the provider name and user ID.

### Indexes

- `idx_users_email`: Unique index on email for fast lookups
- `idx_users_oauth`: Composite index on (oauth_provider, oauth_id) for OAuth authentication

### Methods

#### `to_dict()`
Converts the user object to a dictionary representation, excluding sensitive fields like `password_hash`.

**Returns:** Dictionary with user data

**Example:**
```python
user = User.query.get(1)
user_data = user.to_dict()
# {
#     'id': 1,
#     'email': 'user@example.com',
#     'subscription_tier': 'free',
#     'created_at': '2024-01-15T10:00:00',
#     'updated_at': '2024-01-15T10:00:00',
#     'last_login': None,
#     'oauth_provider': None
# }
```

### Usage Examples

#### Creating a new user with email/password

```python
from models.user import User
from app.extensions import db, bcrypt

# Hash the password
password_hash = bcrypt.generate_password_hash('secure_password').decode('utf-8')

# Create user
user = User(
    email='user@example.com',
    password_hash=password_hash,
    subscription_tier='free'
)

db.session.add(user)
db.session.commit()
```

#### Creating a user with OAuth

```python
user = User(
    email='oauth_user@example.com',
    password_hash='',  # No password for OAuth users
    oauth_provider='google',
    oauth_id='google_123456789',
    subscription_tier='professional'
)

db.session.add(user)
db.session.commit()
```

#### Querying users

```python
# Find by email
user = User.query.filter_by(email='user@example.com').first()

# Find by OAuth credentials
user = User.query.filter_by(
    oauth_provider='google',
    oauth_id='google_123456789'
).first()

# Get all users with a specific subscription tier
free_users = User.query.filter_by(subscription_tier='free').all()
```

#### Updating last login

```python
from datetime import datetime

user = User.query.get(user_id)
user.last_login = datetime.utcnow()
db.session.commit()
```

### Flask-Login Integration

The User model inherits from `UserMixin`, providing the following methods required by Flask-Login:

- `is_authenticated`: Returns True if user is authenticated
- `is_active`: Returns True if user account is active
- `is_anonymous`: Returns False for regular users
- `get_id()`: Returns the user ID as a string

### Security Considerations

1. **Password Hashing**: Always use bcrypt with 12+ rounds (configured in `config.py`)
2. **Password Storage**: Never store plain text passwords
3. **OAuth Tokens**: OAuth tokens should be validated server-side
4. **Session Management**: Sessions expire after 24 hours (configured in `config.py`)
5. **Email Validation**: Validate email format before creating users

### Related Models (To be implemented)

- **APIKey**: API keys for programmatic access
- **Resume**: User's uploaded resumes
- **Analysis**: Resume analysis results
- **UsageTracking**: Monthly usage tracking for subscription limits

## Testing

Tests for the User model are located in `tests/test_user_model.py`.

Run tests with:
```bash
pytest tests/test_user_model.py -v
```

## Database Migration

To create the users table, run:
```bash
python migrations/apply_migration.py
```

Or using Flask-Migrate:
```bash
flask db upgrade
```


## APIKey Model

**File:** `api_key.py`

The APIKey model manages API authentication for programmatic access to the application.

### Fields

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | Integer | Primary key | Auto-increment |
| `user_id` | Integer | Foreign key to users | Not Null, Indexed, CASCADE delete |
| `key_hash` | String(255) | Hashed API key | Not Null, Indexed |
| `name` | String(100) | Descriptive name for the key | Nullable |
| `is_active` | Boolean | Key activation status | Not Null, Default: True |
| `created_at` | DateTime | Key creation timestamp | Not Null, Auto-set |
| `last_used` | DateTime | Last usage timestamp | Nullable |

### Indexes

- `idx_api_keys_user`: Index on user_id for fast user lookups
- `idx_api_keys_hash`: Index on key_hash for authentication

### Methods

#### `to_dict()`
Converts the API key object to a dictionary representation.

**Returns:** Dictionary with API key data (excluding the actual key)

### Usage Examples

#### Creating an API key

```python
from models.api_key import APIKey
from app.extensions import db, bcrypt
import secrets

# Generate a random API key
api_key = secrets.token_urlsafe(32)

# Hash the key before storing
key_hash = bcrypt.generate_password_hash(api_key).decode('utf-8')

# Create API key record
api_key_record = APIKey(
    user_id=user.id,
    key_hash=key_hash,
    name='Production API Key',
    is_active=True
)

db.session.add(api_key_record)
db.session.commit()

# Return the plain key to the user (only shown once)
return api_key
```

#### Validating an API key

```python
from app.extensions import bcrypt

# Get the key from request header
provided_key = request.headers.get('X-API-Key')

# Find all active keys
active_keys = APIKey.query.filter_by(is_active=True).all()

# Check if provided key matches any stored hash
for key_record in active_keys:
    if bcrypt.check_password_hash(key_record.key_hash, provided_key):
        # Update last_used timestamp
        key_record.last_used = datetime.utcnow()
        db.session.commit()
        return key_record.user
        
return None  # Invalid key
```

## Resume Model

**File:** `resume.py`

The Resume model stores uploaded resume files and their parsed data.

### Fields

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | Integer | Primary key | Auto-increment |
| `user_id` | Integer | Foreign key to users | Not Null, Indexed, CASCADE delete |
| `file_name` | String(255) | Original filename | Not Null |
| `file_path` | String(500) | S3 storage path | Not Null |
| `file_size` | Integer | File size in bytes | Not Null |
| `file_format` | String(10) | File format (pdf, docx, txt) | Not Null |
| `parsed_data` | JSONB | Structured resume data | Not Null |
| `is_deleted` | Boolean | Soft delete flag | Not Null, Default: False |
| `uploaded_at` | DateTime | Upload timestamp | Not Null, Auto-set |

### Indexes

- `idx_resumes_user`: Index on user_id for fast user lookups
- `idx_resumes_uploaded`: Index on uploaded_at for chronological queries

### Parsed Data Structure

The `parsed_data` field stores structured resume information in JSONB format:

```json
{
  "contact_info": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "location": "New York, NY"
  },
  "work_experience": [
    {
      "company": "Tech Corp",
      "title": "Software Engineer",
      "start_date": "2020-01",
      "end_date": "2023-12",
      "description": "Developed web applications"
    }
  ],
  "education": [
    {
      "institution": "University of Example",
      "degree": "Bachelor of Science",
      "field": "Computer Science",
      "graduation_date": "2018-05"
    }
  ],
  "certifications": [
    "AWS Certified Developer",
    "Google Cloud Professional"
  ]
}
```

### Methods

#### `to_dict()`
Converts the resume object to a dictionary representation.

**Returns:** Dictionary with resume data including parsed_data

### Usage Examples

#### Creating a resume record

```python
from models.resume import Resume
from app.extensions import db

# After parsing the resume file
resume = Resume(
    user_id=user.id,
    file_name='john_doe_resume.pdf',
    file_path='s3://resume-analyzer-bucket/user123/resume456/john_doe_resume.pdf',
    file_size=204800,  # 200 KB
    file_format='pdf',
    parsed_data={
        'contact_info': {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '+1234567890'
        },
        'work_experience': [],
        'education': []
    },
    is_deleted=False
)

db.session.add(resume)
db.session.commit()
```

#### Querying resumes

```python
# Get all resumes for a user (excluding deleted)
resumes = Resume.query.filter_by(
    user_id=user.id,
    is_deleted=False
).order_by(Resume.uploaded_at.desc()).all()

# Get a specific resume
resume = Resume.query.get(resume_id)

# Query by file format
pdf_resumes = Resume.query.filter_by(
    user_id=user.id,
    file_format='pdf',
    is_deleted=False
).all()

# Query JSONB data (PostgreSQL specific)
from sqlalchemy import cast
from sqlalchemy.dialects.postgresql import JSONB

# Find resumes with specific email
resumes = Resume.query.filter(
    Resume.parsed_data['contact_info']['email'].astext == 'john@example.com'
).all()
```

#### Soft deleting a resume

```python
resume = Resume.query.get(resume_id)
resume.is_deleted = True
db.session.commit()

# Later, permanently delete
from datetime import datetime, timedelta

# Delete resumes marked as deleted more than 30 days ago
cutoff_date = datetime.utcnow() - timedelta(days=30)
old_deleted_resumes = Resume.query.filter(
    Resume.is_deleted == True,
    Resume.uploaded_at < cutoff_date
).all()

for resume in old_deleted_resumes:
    # Delete from S3 first
    # delete_from_s3(resume.file_path)
    
    # Then delete from database
    db.session.delete(resume)

db.session.commit()
```

#### Accessing user relationship

```python
# Get the user who owns a resume
resume = Resume.query.get(resume_id)
owner = resume.user

# Get all resumes for a user
user = User.query.get(user_id)
user_resumes = user.resumes.filter_by(is_deleted=False).all()
```

### File Format Support

The Resume model supports the following file formats:
- **PDF** (.pdf): Most common format
- **DOCX** (.docx): Microsoft Word documents
- **TXT** (.txt): Plain text resumes

### Soft Delete Feature

The `is_deleted` flag enables soft deletes for compliance:
- Resumes are marked as deleted but remain in the database
- Can be restored if needed
- Permanently deleted after retention period (e.g., 30 days)
- Queries should filter out deleted resumes by default

### JSONB Benefits

Using PostgreSQL JSONB provides:
- **Flexible Schema**: Resume structures can vary
- **Efficient Storage**: Binary JSON format
- **Indexing**: Can create indexes on JSON fields
- **Querying**: SQL queries on nested JSON data
- **No Schema Changes**: Add new fields without migrations

### Security Considerations

1. **File Validation**: Validate file format and size before upload
2. **Malware Scanning**: Scan files before processing
3. **Access Control**: Users can only access their own resumes
4. **Encryption**: Files encrypted at rest in S3 (AES-256)
5. **Soft Deletes**: Comply with data retention policies

### Related Models

- **User**: Owner of the resume (many-to-one)
- **Analysis**: Analysis results for this resume (one-to-many, to be implemented)

## Model Relationships

```
User (1) ----< (N) Resume
User (1) ----< (N) APIKey
Resume (1) ----< (N) Analysis (to be implemented)
```

## Testing

Tests for all models are located in the `tests/` directory:
- `tests/test_user_model.py`
- `tests/test_api_key_model.py`
- `tests/test_resume_model.py`

Run all model tests:
```bash
pytest tests/test_*_model.py -v
```

## Database Migrations

All migrations are in `migrations/versions/`:
- `001_create_users_table.py`
- `002_create_api_keys_table.py`
- `003_create_resumes_table.py`

Apply all migrations:
```bash
python migrations/apply_migration.py
```

## Notes

- All models use UTC timestamps
- PostgreSQL 15+ required for JSONB support
- Foreign keys use CASCADE delete for data cleanup
- Indexes optimize common query patterns
- All models include `to_dict()` for JSON serialization
