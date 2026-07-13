"""Create usage_tracking table

Revision ID: 005
Revises: 004
Create Date: 2024-01-15 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    """Create usage_tracking table with user relationship and indexes."""
    op.create_table(
        'usage_tracking',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('month', sa.Date(), nullable=False),
        sa.Column('analysis_count', sa.Integer(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'month', name='uq_user_month')
    )
    
    # Create index
    op.create_index('idx_usage_user_month', 'usage_tracking', ['user_id', 'month'], unique=False)


def downgrade():
    """Drop usage_tracking table and indexes."""
    op.drop_index('idx_usage_user_month', table_name='usage_tracking')
    op.drop_table('usage_tracking')
