from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List

class EditRequestCreate(BaseModel):
    record_id: UUID
    reason: str

class ApprovalDecision(BaseModel):
    decision: str # "approved" | "rejected"
    comment: Optional[str] = None

class ApprovalStepResponse(BaseModel):
    id: UUID
    approver_id: Optional[UUID]
    step_level: int
    required_min_role_level: int
    decision: Optional[str]
    decided_at: Optional[datetime]
    comment: Optional[str]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class EditRequestResponse(BaseModel):
    id: UUID
    record_id: UUID
    requested_by: UUID
    reason: str
    status: str
    approvals_required: int
    approvals_received: int
    edit_window_minutes: int
    edit_window_expires_at: Optional[datetime]
    created_at: datetime
    resolved_at: Optional[datetime]
    steps: List[ApprovalStepResponse] = []
    model_config = ConfigDict(from_attributes=True)