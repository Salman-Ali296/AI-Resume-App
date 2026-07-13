"""Create skill_taxonomy table

Revision ID: 007
Revises: 006
Create Date: 2024-01-15 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    """Create skill_taxonomy table with indexes for NLP skill database."""
    op.create_table(
        'skill_taxonomy',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('skill_name', sa.String(length=255), nullable=False),
        sa.Column('canonical_name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('synonyms', postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_skills_name', 'skill_taxonomy', ['skill_name'], unique=False)
    op.create_index('idx_skills_canonical', 'skill_taxonomy', ['canonical_name'], unique=False)
    op.create_index('idx_skills_category', 'skill_taxonomy', ['category'], unique=False)
    op.create_index('idx_skills_industry', 'skill_taxonomy', ['industry'], unique=False)


def downgrade():
    """Drop skill_taxonomy table and indexes."""
    op.drop_index('idx_skills_industry', table_name='skill_taxonomy')
    op.drop_index('idx_skills_category', table_name='skill_taxonomy')
    op.drop_index('idx_skills_canonical', table_name='skill_taxonomy')
    op.drop_index('idx_skills_name', table_name='skill_taxonomy')
    op.drop_table('skill_taxonomy')
