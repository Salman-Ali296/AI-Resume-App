"""Create contact_submissions table

Revision ID: 006
Revises: 005
Create Date: 2024-01-15 14:15:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    """Create contact_submissions table with user relationship and indexes."""
    op.create_table(
        'contact_submissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('subject', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL')
    )
    
    # Create indexes
    op.create_index('idx_contact_user', 'contact_submissions', ['user_id'], unique=False)
    op.create_index('idx_contact_created', 'contact_submissions', ['created_at'], unique=False)


def downgrade():
    """Drop contact_submissions table and indexes."""
    op.drop_index('idx_contact_created', table_name='contact_submissions')
    op.drop_index('idx_contact_user', table_name='contact_submissions')
    op.drop_table('contact_submissions')
