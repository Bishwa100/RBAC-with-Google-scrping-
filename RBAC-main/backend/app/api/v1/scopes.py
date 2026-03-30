from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from app.db.session import get_db
from app.schemas.scope import ScopeCreate, ScopeResponse
from app.schemas.common import success_response
from app.core.deps import get_current_user, RequireRoleLevel
from app.models.all import Scope, User
from app.core.exceptions import APIException

router = APIRouter()

@router.get("/", response_model=dict)
async def list_scopes(db: AsyncSession = Depends(get_db), current_user: User = Depends(RequireRoleLevel(2))):
    result = await db.execute(select(Scope))
    scopes = result.scalars().all()
    return success_response(data=[ScopeResponse.model_validate(s).model_dump() for s in scopes])

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_scope(
    data: ScopeCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(RequireRoleLevel(0))
):
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

@router.delete("/{id}", response_model=dict)
async def delete_scope(
    id: UUID, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(RequireRoleLevel(0))
):
    scope = await db.get(Scope, id)
    if not scope:
        raise APIException(status.HTTP_404_NOT_FOUND, "not_found", "Scope not found")
    
    await db.delete(scope)
    await db.commit()
    return success_response(message="Scope deleted")