from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, Any, Dict

class RecordBase(BaseModel):
    record_type: str
    payload: Dict[str, Any]

class RecordCreate(RecordBase):
    pass

class RecordUpdate(BaseModel):
    payload: Dict[str, Any]

class RecordResponse(RecordBase):
    id: UUID
    submitted_by: UUID
    dept_id: UUID
    is_frozen: bool
    frozen_at: datetime
    unfrozen_at: Optional[datetime]
    version: int
    created_at: datetime
    updated_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)