"""add topiclens shared content table

Revision ID: 002
Revises: 001
Create Date: 2026-03-31 10:40:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    """Create topiclens_shared_content table"""
    op.create_table(
        'topiclens_shared_content',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('result_id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.String(36), nullable=False),
        sa.Column('shared_by_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('shared_with_role_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('shared_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        
        # Foreign keys
        sa.ForeignKeyConstraint(['result_id'], ['topiclens_results.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_id'], ['topiclens_jobs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['shared_by_user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['shared_with_role_id'], ['roles.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for better query performance
    op.create_index('ix_topiclens_shared_content_result_id', 'topiclens_shared_content', ['result_id'])
    op.create_index('ix_topiclens_shared_content_job_id', 'topiclens_shared_content', ['job_id'])
    op.create_index('ix_topiclens_shared_content_shared_with_role_id', 'topiclens_shared_content', ['shared_with_role_id'])
    op.create_index('ix_topiclens_shared_content_shared_by_user_id', 'topiclens_shared_content', ['shared_by_user_id'])


def downgrade():
    """Drop topiclens_shared_content table"""
    op.drop_index('ix_topiclens_shared_content_shared_by_user_id', table_name='topiclens_shared_content')
    op.drop_index('ix_topiclens_shared_content_shared_with_role_id', table_name='topiclens_shared_content')
    op.drop_index('ix_topiclens_shared_content_job_id', table_name='topiclens_shared_content')
    op.drop_index('ix_topiclens_shared_content_result_id', table_name='topiclens_shared_content')
    op.drop_table('topiclens_shared_content')
