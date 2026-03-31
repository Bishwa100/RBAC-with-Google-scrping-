"""
RBAC Extension Models
Models for comprehensive scope-based access control system
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base

def utc_now():
    return datetime.now(timezone.utc)

class RoleScope(Base):
    """
    Junction table for Role-Scope assignments.
    Allows roles to have associated scopes/permissions that are inherited by users with that role.
    """
    __tablename__ = "role_scopes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    scope_id = Column(UUID(as_uuid=True), ForeignKey("scopes.id", ondelete="CASCADE"), nullable=False)
    assigned_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    assigned_at = Column(DateTime(timezone=True), default=utc_now)
    
    # Relationships
    role = relationship("Role", lazy="selectin")
    scope = relationship("Scope", lazy="selectin")
    assigner = relationship("User", foreign_keys=[assigned_by])

class APIEndpoint(Base):
    """
    Registry of all API endpoints with metadata and required scopes.
    Provides a centralized definition of what scopes are required for each endpoint.
    """
    __tablename__ = "api_endpoints"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Endpoint identification
    path = Column(String(255), nullable=False)  # e.g., "/api/v1/users"
    method = Column(String(10), nullable=False)  # e.g., "GET", "POST", "PATCH", "DELETE"
    
    # Scope requirements
    required_resource = Column(String(100), nullable=True)  # e.g., "users"
    required_action = Column(String(50), nullable=True)     # e.g., "read"
    
    # Metadata
    description = Column(Text)
    category = Column(String(50))  # e.g., "auth", "users", "records"
    is_public = Column(Boolean, default=False)  # Public endpoints don't require auth
    is_active = Column(Boolean, default=True)
    
    # Audit trail
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), onupdate=utc_now)
    
    # Unique constraint on path + method
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )
    
    @property
    def required_scope(self):
        """Returns the required scope in resource:action format"""
        if self.required_resource and self.required_action:
            return f"{self.required_resource}:{self.required_action}"
        return None
