"""Create api_keys table

Revision ID: 002
Revises: 001
Create Date: 2024-01-15 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    """Create api_keys table with user relationship and indexes."""
    op.create_table(
        'api_keys',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('key_hash', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    
    # Create indexes
    op.create_index('idx_api_keys_user', 'api_keys', ['user_id'], unique=False)
    op.create_index('idx_api_keys_hash', 'api_keys', ['key_hash'], unique=False)


def downgrade():
    """Drop api_keys table and indexes."""
    op.drop_index('idx_api_keys_hash', table_name='api_keys')
    op.drop_index('idx_api_keys_user', table_name='api_keys')
    op.drop_table('api_keys')
