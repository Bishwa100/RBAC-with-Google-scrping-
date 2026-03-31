"""Add RoleScope and APIEndpoint models for comprehensive RBAC

Revision ID: add_role_scope_api_endpoint
Revises: 
Create Date: 2026-03-31 08:58:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = 'add_role_scope_api_endpoint'
down_revision = None  # Update this if there's a previous migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create role_scopes table
    op.create_table(
        'role_scopes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('role_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('roles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('scope_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('scopes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('assigned_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('assigned_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    # Create indexes for role_scopes
    op.create_index('ix_role_scopes_role_id', 'role_scopes', ['role_id'])
    op.create_index('ix_role_scopes_scope_id', 'role_scopes', ['scope_id'])
    
    # Create api_endpoints table
    op.create_table(
        'api_endpoints',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('path', sa.String(255), nullable=False),
        sa.Column('method', sa.String(10), nullable=False),
        sa.Column('required_resource', sa.String(100), nullable=True),
        sa.Column('required_action', sa.String(50), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('is_public', sa.Boolean, default=False, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
    )
    
    # Create unique constraint on path + method
    op.create_unique_constraint('uq_api_endpoints_path_method', 'api_endpoints', ['path', 'method'])
    
    # Create indexes for api_endpoints
    op.create_index('ix_api_endpoints_category', 'api_endpoints', ['category'])
    op.create_index('ix_api_endpoints_resource_action', 'api_endpoints', ['required_resource', 'required_action'])


def downgrade() -> None:
    # Drop api_endpoints table
    op.drop_index('ix_api_endpoints_resource_action', table_name='api_endpoints')
    op.drop_index('ix_api_endpoints_category', table_name='api_endpoints')
    op.drop_constraint('uq_api_endpoints_path_method', 'api_endpoints', type_='unique')
    op.drop_table('api_endpoints')
    
    # Drop role_scopes table
    op.drop_index('ix_role_scopes_scope_id', table_name='role_scopes')
    op.drop_index('ix_role_scopes_role_id', table_name='role_scopes')
    op.drop_table('role_scopes')
