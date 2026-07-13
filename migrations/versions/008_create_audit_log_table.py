"""Create audit_log table

Revision ID: 008
Revises: 007
Create Date: 2024-01-15 14:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade():
    """Create audit_log table with user relationship and indexes for security auditing."""
    op.create_table(
        'audit_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('resource_id', sa.Integer(), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL')
    )
    
    # Create indexes
    op.create_index('idx_audit_user', 'audit_log', ['user_id'], unique=False)
    op.create_index('idx_audit_created', 'audit_log', ['created_at'], unique=False)
    op.create_index('idx_audit_action', 'audit_log', ['action'], unique=False)


def downgrade():
    """Drop audit_log table and indexes."""
    op.drop_index('idx_audit_action', table_name='audit_log')
    op.drop_index('idx_audit_created', table_name='audit_log')
    op.drop_index('idx_audit_user', table_name='audit_log')
    op.drop_table('audit_log')
