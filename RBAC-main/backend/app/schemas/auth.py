from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID

from app.schemas.department import DepartmentResponse

class Login(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: Optional['UserAuthResponse'] = None

class ScopeResponse(BaseModel):
    id: UUID
    resource: str
    action: str
    description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class RoleResponse(BaseModel):
    id: UUID
    name: str
    level: int
    description: Optional[str] = None
    scopes: List[ScopeResponse] = []
    model_config = ConfigDict(from_attributes=True)

class UserAuthResponse(BaseModel):
    id: UUID
    email: str
    full_name: Optional[str] = None
    is_active: bool
    department_id: Optional[UUID] = None
    department: Optional[DepartmentResponse] = None
    roles: List[RoleResponse] = []
    model_config = ConfigDict(from_attributes=True)

class RefreshToken(BaseModel):
    refresh_token: str

class UserCreateRoot(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None