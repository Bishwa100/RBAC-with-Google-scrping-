from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional
from datetime import datetime

class APIEndpointBase(BaseModel):
    path: str
    method: str
    required_resource: Optional[str] = None
    required_action: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    is_public: bool = False
    is_active: bool = True

class APIEndpointCreate(APIEndpointBase):
    pass

class APIEndpointUpdate(BaseModel):
    path: Optional[str] = None
    method: Optional[str] = None
    required_resource: Optional[str] = None
    required_action: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    is_public: Optional[bool] = None
    is_active: Optional[bool] = None

class APIEndpointResponse(APIEndpointBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    required_scope: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)
