"""Script to apply database migrations directly."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from config import get_config

def apply_users_table_migration():
    """Apply the users table migration."""
    config = get_config()
    engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
    
    # SQL for creating users table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        oauth_provider VARCHAR(50),
        oauth_id VARCHAR(255),
        subscription_tier VARCHAR(50) NOT NULL DEFAULT 'free',
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
        last_login TIMESTAMP
    );
    """
    
    # SQL for creating indexes
    create_email_index_sql = """
    CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
    """
    
    create_oauth_index_sql = """
    CREATE INDEX IF NOT EXISTS idx_users_oauth ON users(oauth_provider, oauth_id);
    """
    
    try:
        with engine.connect() as conn:
            # Execute migrations
            conn.execute(text(create_table_sql))
            conn.execute(text(create_email_index_sql))
            conn.execute(text(create_oauth_index_sql))
            conn.commit()
            
            print("✓ Users table created successfully")
            print("✓ Email index created successfully")
            print("✓ OAuth index created successfully")
            
    except Exception as e:
        print(f"Error applying users migration: {e}")
        sys.exit(1)
    finally:
        engine.dispose()


def apply_api_keys_table_migration():
    """Apply the api_keys table migration."""
    config = get_config()
    engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
    
    # SQL for creating api_keys table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS api_keys (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        key_hash VARCHAR(255) NOT NULL,
        name VARCHAR(100),
        is_active BOOLEAN NOT NULL DEFAULT TRUE,
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        last_used TIMESTAMP
    );
    """
    
    # SQL for creating indexes
    create_user_index_sql = """
    CREATE INDEX IF NOT EXISTS idx_api_keys_user ON api_keys(user_id);
    """
    
    create_hash_index_sql = """
    CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON api_keys(key_hash);
    """
    
    try:
        with engine.connect() as conn:
            # Execute migrations
            conn.execute(text(create_table_sql))
            conn.execute(text(create_user_index_sql))
            conn.execute(text(create_hash_index_sql))
            conn.commit()
            
            print("✓ API keys table created successfully")
            print("✓ User index created successfully")
            print("✓ Hash index created successfully")
            
    except Exception as e:
        print(f"Error applying api_keys migration: {e}")
        sys.exit(1)
    finally:
        engine.dispose()


def apply_resumes_table_migration():
    """Apply the resumes table migration."""
    config = get_config()
    engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
    
    # SQL for creating resumes table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS resumes (
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
    """
    
    # SQL for creating indexes
    create_user_index_sql = """
    CREATE INDEX IF NOT EXISTS idx_resumes_user ON resumes(user_id);
    """
    
    create_uploaded_index_sql = """
    CREATE INDEX IF NOT EXISTS idx_resumes_uploaded ON resumes(uploaded_at);
    """
    
    try:
        with engine.connect() as conn:
            # Execute migrations
            conn.execute(text(create_table_sql))
            conn.execute(text(create_user_index_sql))
            conn.execute(text(create_uploaded_index_sql))
            conn.commit()
            
            print("✓ Resumes table created successfully")
            print("✓ User index created successfully")
            print("✓ Uploaded timestamp index created successfully")
            
    except Exception as e:
        print(f"Error applying resumes migration: {e}")
        sys.exit(1)
    finally:
        engine.dispose()


if __name__ == '__main__':
    print("Applying database migrations...\n")
    apply_users_table_migration()
    apply_api_keys_table_migration()
    apply_resumes_table_migration()
    print("\nAll migrations completed!")
