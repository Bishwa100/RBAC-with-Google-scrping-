from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from app.db.session import get_db
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse
from app.schemas.common import success_response
from app.core.deps import get_current_user, RequireScope, get_user_min_level
from app.models.all import Role, User, Scope
from app.models.rbac_extensions import RoleScope
from app.core.exceptions import APIException

router = APIRouter()

@router.get("/", response_model=dict)
async def list_roles(db: AsyncSession = Depends(get_db), current_user: User = Depends(RequireScope("roles", "read"))):
    """List all roles. Required scope: roles:read"""
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
    current_user: User = Depends(RequireScope("roles", "create"))
):
    """Create a new role. Required scope: roles:create"""
    role = Role(**data.model_dump())
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return success_response(data=RoleResponse.model_validate(role).model_dump())

@router.get("/{id}", response_model=dict)
async def get_role(id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(RequireScope("roles", "read"))):
    """Get role by ID. Required scope: roles:read"""
    role = await db.get(Role, id)
    if not role:
        raise APIException(status.HTTP_404_NOT_FOUND, "not_found", "Role not found")
    return success_response(data=RoleResponse.model_validate(role).model_dump())

@router.patch("/{id}", response_model=dict)
async def update_role(
    id: UUID, 
    data: RoleUpdate, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(RequireScope("roles", "update"))
):
    """Update role. Required scope: roles:update"""
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
    current_user: User = Depends(RequireScope("roles", "delete"))
):
    """Delete role. Required scope: roles:delete"""
    role = await db.get(Role, id)
    if not role:
        raise APIException(status.HTTP_404_NOT_FOUND, "not_found", "Role not found")
    
    await db.delete(role)
    await db.commit()
    return success_response(message="Role deleted")

@router.get("/{id}/scopes", response_model=dict)
async def list_role_scopes(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RequireScope("roles", "read"))
):
    """List scopes assigned to a role. Required scope: roles:read"""
    role = await db.get(Role, id)
    if not role:
        raise APIException(status.HTTP_404_NOT_FOUND, "not_found", "Role not found")
    
    result = await db.execute(
        select(RoleScope).join(Scope).where(RoleScope.role_id == id)
    )
    role_scopes = result.scalars().all()
    
    from app.schemas.scope import ScopeResponse
    scopes = [rs.scope for rs in role_scopes]
    return success_response(data=[ScopeResponse.model_validate(s).model_dump() for s in scopes])

@router.post("/{id}/scopes", response_model=dict)
async def assign_scope_to_role(
    id: UUID,
    scope_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RequireScope("roles", "update"))
):
    """Assign scope to a role. Required scope: roles:update"""
    role = await db.get(Role, id)
    scope = await db.get(Scope, scope_id)
    
    if not role or not scope:
        raise APIException(status.HTTP_404_NOT_FOUND, "not_found", "Role or Scope not found")
    
    # Check if already assigned
    result = await db.execute(
        select(RoleScope).where(RoleScope.role_id == id, RoleScope.scope_id == scope_id)
    )
    if result.scalar_one_or_none():
        raise APIException(status.HTTP_409_CONFLICT, "conflict", "Scope already assigned to role")
    
    role_scope = RoleScope(role_id=id, scope_id=scope_id)
    db.add(role_scope)
    await db.commit()
    return success_response(message="Scope assigned to role")

@router.delete("/{id}/scopes/{scope_id}", response_model=dict)
async def remove_scope_from_role(
    id: UUID,
    scope_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RequireScope("roles", "update"))
):
    """Remove scope from role. Required scope: roles:update"""
    result = await db.execute(
        select(RoleScope).where(RoleScope.role_id == id, RoleScope.scope_id == scope_id)
    )
    role_scope = result.scalar_one_or_none()
    
    if not role_scope:
        raise APIException(status.HTTP_404_NOT_FOUND, "not_found", "Scope assignment not found")
    
    await db.delete(role_scope)
    await db.commit()
    return success_response(message="Scope removed from role")