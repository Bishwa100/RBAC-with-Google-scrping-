import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Text, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base

def utc_now():
    return datetime.now(timezone.utc)

class Department(Base):
    __tablename__ = "departments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(10), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

class Role(Base):
    __tablename__ = "roles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    level = Column(Integer, nullable=False)
    dept_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), default=utc_now)

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(Text, nullable=False)
    full_name = Column(String(255))
    dept_id = Column(UUID(as_uuid=True), ForeignKey("departments.id", name="fk_user_dept_id", use_alter=True), nullable=True)
    is_active = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), onupdate=utc_now)
    details = Column(JSONB, nullable=True)

    roles = relationship("UserRole", foreign_keys="UserRole.user_id", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    scopes = relationship("UserScope", foreign_keys="UserScope.user_id", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    department = relationship("Department", foreign_keys=[dept_id])
    topiclens_jobs = relationship("TopicLensJob", back_populates="user", cascade="all, delete-orphan")

class UserRole(Base):
    __tablename__ = "user_roles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    assigned_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    assigned_at = Column(DateTime(timezone=True), default=utc_now)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", foreign_keys=[user_id], back_populates="roles")
    role = relationship("Role", lazy="selectin")

class Scope(Base):
    __tablename__ = "scopes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource = Column(String(100), nullable=False)
    action = Column(String(50), nullable=False)
    dept_context = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    description = Column(Text)

class UserScope(Base):
    __tablename__ = "user_scopes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    scope_id = Column(UUID(as_uuid=True), ForeignKey("scopes.id"), nullable=False)
    granted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    granted_at = Column(DateTime(timezone=True), default=utc_now)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", foreign_keys=[user_id], back_populates="scopes")
    scope = relationship("Scope", lazy="selectin")

class DataRecord(Base):
    __tablename__ = "data_records"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submitted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    dept_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    record_type = Column(String(100), nullable=False)
    payload = Column(JSONB, nullable=False)
    is_frozen = Column(Boolean, default=True)
    frozen_at = Column(DateTime(timezone=True), default=utc_now)
    unfrozen_at = Column(DateTime(timezone=True), nullable=True)
    version = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), onupdate=utc_now)

class EditRequest(Base):
    __tablename__ = "edit_requests"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    record_id = Column(UUID(as_uuid=True), ForeignKey("data_records.id"), nullable=False)
    requested_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    approvals_required = Column(Integer, default=2)
    approvals_received = Column(Integer, default=0)
    edit_window_minutes = Column(Integer, default=30)
    edit_window_expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    steps = relationship("ApprovalStep", back_populates="request", cascade="all, delete-orphan", lazy="selectin")

class ApprovalStep(Base):
    __tablename__ = "approval_steps"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(UUID(as_uuid=True), ForeignKey("edit_requests.id"), nullable=False)
    approver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True) # Initially null until claimed
    step_level = Column(Integer, nullable=False)
    required_min_role_level = Column(Integer, nullable=False)
    decision = Column(String(20), nullable=True)
    decided_at = Column(DateTime(timezone=True), nullable=True)
    comment = Column(Text)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    request = relationship("EditRequest", back_populates="steps")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    resource = Column(String(100))
    resource_id = Column(UUID(as_uuid=True), nullable=True)
    dept_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    details = Column(JSONB)
    ip_address = Column(String(45))
    created_at = Column(DateTime(timezone=True), default=utc_now)

    user = relationship("User")
    department = relationship("Department")

class DocumentExtraction(Base):
    __tablename__ = "document_extractions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    content_type = Column(String(100))
    extraction_data = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

# Import TopicLens models
from app.models.topiclens import TopicLensJob, TopicLensResult
