"""
TopicLens Database Models
Models for jobs, results, and search history
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import uuid
from datetime import datetime

class TopicLensJob(Base):
    """Model for TopicLens search/analysis jobs"""
    __tablename__ = "topiclens_jobs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Job details
    topic = Column(String(200), nullable=False, index=True)
    sources = Column(JSON, nullable=False)  # List of sources
    deep_analysis = Column(Boolean, default=False)
    
    # Status tracking
    status = Column(String(20), default="pending", index=True)  # pending, running, completed, failed
    progress = Column(Integer, default=0)  # 0-100
    
    # Results
    result = Column(JSON, nullable=True)  # Scraped data and analysis
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="topiclens_jobs")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": str(self.user_id) if self.user_id else None,
            "topic": self.topic,
            "sources": self.sources,
            "deep_analysis": self.deep_analysis,
            "status": self.status,
            "progress": self.progress,
            "result": self.result,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

class TopicLensResult(Base):
    """Model for storing individual scraping results"""
    __tablename__ = "topiclens_results"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String(36), ForeignKey("topiclens_jobs.id"), nullable=False)
    
    # Source information
    source = Column(String(50), nullable=False, index=True)  # github, reddit, etc.
    url = Column(Text, nullable=False)
    title = Column(Text, nullable=True)
    
    # Content
    content = Column(Text, nullable=True)
    result_metadata = Column("metadata", JSON, nullable=True)  # Additional metadata (renamed to avoid SQLAlchemy conflict)
    
    # Analysis
    sentiment = Column(String(20), nullable=True)  # positive, negative, neutral
    keywords = Column(JSON, nullable=True)  # List of keywords
    summary = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    job = relationship("TopicLensJob", backref="results")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "job_id": self.job_id,
            "source": self.source,
            "url": self.url,
            "title": self.title,
            "content": self.content,
            "metadata": self.result_metadata,
            "sentiment": self.sentiment,
            "keywords": self.keywords,
            "summary": self.summary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class TopicLensSharedContent(Base):
    """Model for tracking content shared with specific roles"""
    __tablename__ = "topiclens_shared_content"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    result_id = Column(Integer, ForeignKey("topiclens_results.id"), nullable=False)
    job_id = Column(String(36), ForeignKey("topiclens_jobs.id"), nullable=False)
    
    # Sharing information
    shared_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    shared_with_role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    
    # Optional metadata
    notes = Column(Text, nullable=True)
    
    # Timestamp
    shared_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    result = relationship("TopicLensResult", backref="shared_instances")
    job = relationship("TopicLensJob", backref="shared_instances")
    shared_by = relationship("User", foreign_keys=[shared_by_user_id])
    shared_with_role = relationship("Role", foreign_keys=[shared_with_role_id])
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "result_id": self.result_id,
            "job_id": self.job_id,
            "shared_by_user_id": str(self.shared_by_user_id),
            "shared_with_role_id": str(self.shared_with_role_id),
            "notes": self.notes,
            "shared_at": self.shared_at.isoformat() if self.shared_at else None,
        }
