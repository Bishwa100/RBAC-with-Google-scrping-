from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

class RoleBase(BaseModel):
    name: str
    level: int
    dept_id: Optional[UUID] = None
    description: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    level: Optional[int] = None
    description: Optional[str] = None

class RoleResponse(RoleBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)