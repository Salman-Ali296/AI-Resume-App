"""Add password reset fields to users table.

This migration adds reset_token_hash and reset_token_expires fields
to support password reset functionality.
"""
from datetime import datetime


def upgrade(conn):
    """Add password reset fields to users table."""
    conn.execute("""
        ALTER TABLE users
        ADD COLUMN reset_token_hash VARCHAR(255),
        ADD COLUMN reset_token_expires TIMESTAMP;
    """)
    
    print(f"[{datetime.now()}] Added password reset fields to users table")


def downgrade(conn):
    """Remove password reset fields from users table."""
    conn.execute("""
        ALTER TABLE users
        DROP COLUMN IF EXISTS reset_token_hash,
        DROP COLUMN IF EXISTS reset_token_expires;
    """)
    
    print(f"[{datetime.now()}] Removed password reset fields from users table")
