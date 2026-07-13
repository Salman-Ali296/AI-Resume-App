# Task 2.3 Implementation Summary: Resume Model

## Overview
Successfully implemented the Resume model for file storage with user relationship, file metadata, and parsed data storage in JSONB format.

## Files Created/Modified

### 1. models/resume.py (NEW)
Created the Resume model with the following features:
- **Table Name**: `resumes`
- **Primary Key**: `id` (Integer, auto-increment)
- **Foreign Key**: `user_id` references `users.id` with CASCADE delete
- **File Metadata Fields**:
  - `file_name` (String 255) - Original filename
  - `file_path` (String 500) - S3 storage path
  - `file_size` (Integer) - File size in bytes
  - `file_format` (String 10) - File format (pdf, docx, txt)
- **Parsed Data**: `parsed_data` (JSONB) - Structured resume data
- **Soft Delete**: `is_deleted` (Boolean, default False)
- **Timestamp**: `uploaded_at` (DateTime, auto-set)
- **Relationship**: Many-to-one with User model
- **Indexes**: 
  - `idx_resumes_user` on `user_id`
  - `idx_resumes_uploaded` on `uploaded_at`
- **Methods**:
  - `__repr__()` - String representation
  - `to_dict()` - Dictionary serialization

### 2. models/__init__.py (MODIFIED)
Updated to export the Resume model:
```python
from models.resume import Resume
__all__ = ['User', 'APIKey', 'Resume']
```

### 3. migrations/versions/003_create_resumes_table.py (NEW)
Created Alembic migration with:
- Table creation with all fields
- Foreign key constraint to users table
- JSONB column for parsed_data (PostgreSQL-specific)
- Indexes for user_id and uploaded_at
- Upgrade and downgrade functions

### 4. migrations/apply_migration.py (MODIFIED)
Added `apply_resumes_table_migration()` function:
- Creates resumes table with IF NOT EXISTS
- Creates indexes with IF NOT EXISTS
- Includes proper error handling
- Updated main execution to call the new migration

### 5. tests/test_resume_model.py (NEW)
Comprehensive test suite with 7 test cases:
- `test_resume_creation` - Basic model instantiation
- `test_resume_repr` - String representation
- `test_resume_to_dict` - Dictionary serialization
- `test_resume_soft_delete` - Soft delete flag functionality
- `test_resume_jsonb_data` - Complex JSONB data storage
- `test_resume_file_formats` - Multiple file format support
- Tests cover all requirements (6.1, 6.2, 13.1)

### 6. verify_resume_model.py (NEW)
Verification script that checks:
- Model imports correctly
- All required attributes present
- All required methods present
- Model structure validity
- User relationship defined
- Table name configuration
- Index configuration

## Requirements Satisfied

### Requirement 6.1: Resume Storage
✓ Database stores resume file, extracted data, and analysis results
✓ JSONB field for flexible parsed data structure
✓ File metadata (name, path, size, format) stored

### Requirement 6.2: User Association
✓ Each resume associated with user via foreign key
✓ CASCADE delete ensures data cleanup
✓ Indexed for efficient queries

### Requirement 13.1: Multi-Format Support
✓ file_format field supports pdf, docx, txt
✓ Model structure supports all file types

## Database Schema

```sql
CREATE TABLE resumes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    file_format VARCHAR(10) NOT NULL,
    parsed_data JSONB NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    uploaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_resumes_user ON resumes(user_id);
CREATE INDEX idx_resumes_uploaded ON resumes(uploaded_at);
```

## JSONB Data Structure Example

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

## Model Features

### Soft Deletes
The `is_deleted` flag enables soft deletes for compliance with data retention requirements (Requirement 6.8, 15.5):
- Resumes marked as deleted remain in database
- Can be permanently removed after retention period
- Queries can filter out deleted resumes

### JSONB Benefits
Using PostgreSQL JSONB provides:
- Flexible schema for varying resume structures
- Efficient storage and indexing
- Query capabilities on JSON fields
- No need for separate tables for resume sections

### Relationships
- **User → Resumes**: One-to-many (user.resumes)
- **Resume → User**: Many-to-one (resume.user)
- Cascade delete ensures cleanup when user is deleted

## Integration Points

### With User Model
The Resume model integrates with the existing User model:
```python
# User model has backref
user.resumes  # Access all resumes for a user

# Resume model has relationship
resume.user  # Access the user who owns the resume
```

### With Future Models
The Resume model will integrate with:
- **Analysis Model**: One resume can have many analyses
- **File Storage Service**: file_path points to S3 location
- **Parser Service**: Populates parsed_data field

## Testing Strategy

### Unit Tests (test_resume_model.py)
- Model instantiation and attributes
- String representation
- Dictionary serialization
- Soft delete functionality
- JSONB data handling
- Multiple file format support

### Integration Tests (Future)
- Database CRUD operations
- User relationship queries
- Soft delete filtering
- JSONB querying

## Migration Instructions

### Using Docker (Recommended)
```bash
# Start services
docker-compose up -d postgres

# Run migrations
docker-compose exec web python migrations/apply_migration.py
```

### Manual Setup
```bash
# Ensure PostgreSQL is running
# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
python migrations/apply_migration.py
```

## Verification

To verify the implementation:
```bash
# Run verification script
python verify_resume_model.py

# Run tests (requires database)
pytest tests/test_resume_model.py -v
```

## Next Steps

1. **Task 2.4**: Create Analysis model for storing results
2. **Task 5**: Implement resume parser to populate parsed_data
3. **Task 17**: Implement resume storage service with S3 integration

## Notes

- Model follows the same pattern as User and APIKey models
- Uses SQLAlchemy ORM with Flask-SQLAlchemy
- Compatible with PostgreSQL 15+
- JSONB requires PostgreSQL (not compatible with SQLite)
- All timestamps use UTC
- File paths should use S3 URI format: `s3://bucket/path/to/file`

## Compliance

- **Security**: Foreign key with CASCADE delete
- **Privacy**: Soft delete for data retention compliance
- **Performance**: Indexes on user_id and uploaded_at
- **Scalability**: JSONB for flexible schema evolution
