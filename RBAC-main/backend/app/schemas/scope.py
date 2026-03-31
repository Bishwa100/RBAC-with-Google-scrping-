from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional

class ScopeBase(BaseModel):
    resource: str
    action: str
    dept_context: Optional[UUID] = None
    description: Optional[str] = None

class ScopeCreate(ScopeBase):
    pass

class ScopeUpdate(BaseModel):
    resource: Optional[str] = None
    action: Optional[str] = None
    dept_context: Optional[UUID] = None
    description: Optional[str] = None

class ScopeResponse(ScopeBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)