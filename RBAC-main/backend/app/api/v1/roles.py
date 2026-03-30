from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from app.db.session import get_db
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse
from app.schemas.common import success_response
from app.core.deps import get_current_user, RequireRoleLevel, get_user_min_level
from app.models.all import Role, User
from app.core.exceptions import APIException

router = APIRouter()

@router.get("/", response_model=dict)
async def list_roles(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    min_level = get_user_min_level(current_user)
    query = select(Role)
    if min_level > 0:
        query = query.where(Role.dept_id == current_user.dept_id)
        
    result = await db.execute(query)
    roles = result.scalars().all()
    return success_response(data=[RoleResponse.model_validate(r).model_dump() for r in roles])

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_role(
    data: RoleCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(RequireRoleLevel(0))
):
    role = Role(**data.model_dump())
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return success_response(data=RoleResponse.model_validate(role).model_dump())

@router.patch("/{id}", response_model=dict)
async def update_role(
    id: UUID, 
    data: RoleUpdate, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(RequireRoleLevel(0))
):
    role = await db.get(Role, id)
    if not role:
        raise APIException(status.HTTP_404_NOT_FOUND, "not_found", "Role not found")
    
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(role, k, v)
    
    await db.commit()
    await db.refresh(role)
    return success_response(data=RoleResponse.model_validate(role).model_dump())

@router.delete("/{id}", response_model=dict)
async def delete_role(
    id: UUID, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(RequireRoleLevel(0))
):
    role = await db.get(Role, id)
    if not role:
        raise APIException(status.HTTP_404_NOT_FOUND, "not_found", "Role not found")
    
    await db.delete(role)
    await db.commit()
    return success_response(message="Role deleted")