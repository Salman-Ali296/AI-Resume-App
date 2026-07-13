"""Create resumes table

Revision ID: 003
Revises: 002
Create Date: 2024-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    """Create resumes table with user relationship, file metadata, and parsed data."""
    op.create_table(
        'resumes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('file_format', sa.String(length=10), nullable=False),
        sa.Column('parsed_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    
    # Create indexes
    op.create_index('idx_resumes_user', 'resumes', ['user_id'], unique=False)
    op.create_index('idx_resumes_uploaded', 'resumes', ['uploaded_at'], unique=False)


def downgrade():
    """Drop resumes table and indexes."""
    op.drop_index('idx_resumes_uploaded', table_name='resumes')
    op.drop_index('idx_resumes_user', table_name='resumes')
    op.drop_table('resumes')
