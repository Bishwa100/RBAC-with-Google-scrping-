"""
TopicLens Sharing Schemas
Pydantic models for content sharing operations
"""
from pydantic import BaseModel, UUID4, Field
from typing import Optional, List
from datetime import datetime


class ShareContentRequest(BaseModel):
    """Request to share content with specific roles"""
    result_id: int = Field(..., description="ID of the TopicLens result to share")
    job_id: str = Field(..., description="ID of the TopicLens job")
    role_ids: List[UUID4] = Field(..., description="List of role IDs to share with")
    notes: Optional[str] = Field(None, description="Optional notes for the shared content")


class ShareContentResponse(BaseModel):
    """Response after sharing content"""
    success: bool
    message: str
    shared_count: int = Field(..., description="Number of roles shared with")
    share_ids: List[str] = Field(..., description="IDs of created share records")


class RevokeShareRequest(BaseModel):
    """Request to revoke shared access"""
    share_id: UUID4 = Field(..., description="ID of the share to revoke")


class SharedContentItem(BaseModel):
    """Individual shared content item with full details"""
    share_id: str
    result_id: int
    job_id: str
    
    # Content details
    topic: str
    source: str
    url: str
    title: Optional[str]
    content: Optional[str]
    metadata: Optional[dict]
    
    # Analysis data
    sentiment: Optional[str]
    keywords: Optional[List[str]]
    summary: Optional[str]
    
    # Sharing metadata
    shared_by_user_id: str
    shared_by_username: str
    shared_with_role_id: str
    shared_with_role_name: str
    notes: Optional[str]
    shared_at: datetime
    
    # Result timestamp
    created_at: datetime
    
    class Config:
        from_attributes = True


class MySharedContentResponse(BaseModel):
    """Response for user's shared content"""
    items: List[SharedContentItem]
    total: int


class AllSharedContentResponse(BaseModel):
    """Response for all shared content (admin view)"""
    items: List[SharedContentItem]
    total: int
