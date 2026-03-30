from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, Any

class AuditLogResponse(BaseModel):
    id: UUID
    user_id: Optional[UUID] = None
    action: str
    resource: Optional[str] = None
    resource_id: Optional[UUID] = None
    dept_id: Optional[UUID] = None
    details: Optional[Any] = None
    ip_address: Optional[str] = None
    created_at: datetime
    
    # Nested info
    user_email: Optional[str] = None
    dept_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
