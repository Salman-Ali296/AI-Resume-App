"""Create analyses table

Revision ID: 004
Revises: 003
Create Date: 2024-01-15 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    """Create analyses table with user and resume relationships, scores, and analysis data."""
    op.create_table(
        'analyses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('resume_id', sa.Integer(), nullable=False),
        sa.Column('job_description', sa.Text(), nullable=False),
        sa.Column('match_score', sa.Float(), nullable=False),
        sa.Column('ats_score', sa.Float(), nullable=False),
        sa.Column('quality_score', sa.Float(), nullable=False),
        sa.Column('extracted_skills', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('match_breakdown', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('recommendations', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['resume_id'], ['resumes.id'], ondelete='CASCADE')
    )
    
    # Create indexes
    op.create_index('idx_analyses_user', 'analyses', ['user_id'], unique=False)
    op.create_index('idx_analyses_resume', 'analyses', ['resume_id'], unique=False)
    op.create_index('idx_analyses_created', 'analyses', ['created_at'], unique=False)
    op.create_index('idx_analyses_match_score', 'analyses', ['match_score'], unique=False)


def downgrade():
    """Drop analyses table and indexes."""
    op.drop_index('idx_analyses_match_score', table_name='analyses')
    op.drop_index('idx_analyses_created', table_name='analyses')
    op.drop_index('idx_analyses_resume', table_name='analyses')
    op.drop_index('idx_analyses_user', table_name='analyses')
    op.drop_table('analyses')
