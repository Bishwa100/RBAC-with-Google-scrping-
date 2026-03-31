from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from app.db.session import get_db
from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentResponse
from app.schemas.common import success_response
from app.core.deps import get_current_user, RequireScope
from app.models.all import Department, User
from app.core.exceptions import APIException

router = APIRouter()

@router.get("/", response_model=dict)
async def list_departments(db: AsyncSession = Depends(get_db), current_user: User = Depends(RequireScope("departments", "read"))):
    """List all departments. Required scope: departments:read"""
    result = await db.execute(select(Department).where(Department.is_active == True))
    depts = result.scalars().all()
    return success_response(data=[DepartmentResponse.model_validate(d).model_dump() for d in depts])

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_department(
    data: DepartmentCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(RequireScope("departments", "create"))
):
    """Create a new department. Required scope: departments:create"""
    result = await db.execute(select(Department).where(Department.code == data.code))
    if result.scalar_one_or_none():
         raise APIException(status.HTTP_409_CONFLICT, "conflict", "Department code already exists")
    
    dept = Department(**data.model_dump(), created_by=current_user.id)
    db.add(dept)
    await db.commit()
    await db.refresh(dept)
    return success_response(data=DepartmentResponse.model_validate(dept).model_dump())

@router.get("/{id}", response_model=dict)
async def get_department(id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(RequireScope("departments", "read"))):
    """Get department by ID. Required scope: departments:read"""
    dept = await db.get(Department, id)
    if not dept or not dept.is_active:
        raise APIException(status.HTTP_404_NOT_FOUND, "not_found", "Department not found")
    return success_response(data=DepartmentResponse.model_validate(dept).model_dump())

@router.patch("/{id}", response_model=dict)
async def update_department(
    id: UUID, 
    data: DepartmentUpdate, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(RequireScope("departments", "update"))
):
    """Update department. Required scope: departments:update"""
    dept = await db.get(Department, id)
    if not dept:
        raise APIException(status.HTTP_404_NOT_FOUND, "not_found", "Department not found")
    
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(dept, k, v)
    
    await db.commit()
    await db.refresh(dept)
    return success_response(data=DepartmentResponse.model_validate(dept).model_dump())

@router.delete("/{id}", response_model=dict)
async def delete_department(
    id: UUID, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(RequireScope("departments", "delete"))
):
    """Delete/deactivate department. Required scope: departments:delete"""
    dept = await db.get(Department, id)
    if not dept:
        raise APIException(status.HTTP_404_NOT_FOUND, "not_found", "Department not found")
    
    dept.is_active = False
    await db.commit()
    return success_response(message="Department soft deleted")