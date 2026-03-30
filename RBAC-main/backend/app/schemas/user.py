from pydantic import BaseModel, ConfigDict, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from app.schemas.role import RoleResponse
from app.schemas.department import DepartmentResponse

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    dept_id: Optional[UUID] = None
    role_id: Optional[UUID] = None
    details: Optional[dict] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    details: Optional[dict] = None

class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: Optional[str]
    department_id: Optional[UUID] = None
    department: Optional[DepartmentResponse] = None
    is_active: bool
    roles: List[RoleResponse] = []
    created_at: datetime
    details: Optional[dict] = None
    model_config = ConfigDict(from_attributes=True)