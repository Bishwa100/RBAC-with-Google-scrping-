from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from app.db.session import get_db
from app.schemas.scope import ScopeCreate, ScopeResponse, ScopeUpdate
from app.schemas.common import success_response
from app.core.deps import get_current_user, RequireScope
from app.models.all import Scope, User
from app.models.rbac_extensions import APIEndpoint
from app.core.exceptions import APIException

router = APIRouter()

@router.get("/", response_model=dict)
async def list_scopes(db: AsyncSession = Depends(get_db), current_user: User = Depends(RequireScope("scopes", "read"))):
    """List all scopes. Required scope: scopes:read"""
    result = await db.execute(select(Scope))
    scopes = result.scalars().all()
    return success_response(data=[ScopeResponse.model_validate(s).model_dump() for s in scopes])

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_scope(
    data: ScopeCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(RequireScope("scopes", "create"))
):
    """Create a new scope. Required scope: scopes:create"""
    # Check for existing
    result = await db.execute(select(Scope).where(
        Scope.resource == data.resource, 
        Scope.action == data.action, 
        Scope.dept_context == data.dept_context
    ))
    if result.scalar_one_or_none():
        raise APIException(status.HTTP_409_CONFLICT, "conflict", "Scope already exists")

    scope = Scope(**data.model_dump())
    db.add(scope)
    await db.commit()
    await db.refresh(scope)
    return success_response(data=ScopeResponse.model_validate(scope).model_dump())

@router.patch("/{id}", response_model=dict)
async def update_scope(
    id: UUID,
    data: ScopeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RequireScope("scopes", "update"))
):
    """Update scope. Required scope: scopes:update"""
    scope = await db.get(Scope, id)
    if not scope:
        raise APIException(status.HTTP_404_NOT_FOUND, "not_found", "Scope not found")
    
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(scope, k, v)
    
    await db.commit()
    await db.refresh(scope)
    return success_response(data=ScopeResponse.model_validate(scope).model_dump())

@router.delete("/{id}", response_model=dict)
async def delete_scope(
    id: UUID, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(RequireScope("scopes", "delete"))
):
    """Delete scope. Required scope: scopes:delete"""
    scope = await db.get(Scope, id)
    if not scope:
        raise APIException(status.HTTP_404_NOT_FOUND, "not_found", "Scope not found")
    
    await db.delete(scope)
    await db.commit()
    return success_response(message="Scope deleted")

@router.get("/api-endpoints", response_model=dict)
async def list_api_endpoints(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RequireScope("scopes", "read"))
):
    """List all registered API endpoints. Required scope: scopes:read"""
    result = await db.execute(select(APIEndpoint))
    endpoints = result.scalars().all()
    
    from app.schemas.api_endpoint import APIEndpointResponse
    return success_response(data=[APIEndpointResponse.model_validate(e).model_dump() for e in endpoints])