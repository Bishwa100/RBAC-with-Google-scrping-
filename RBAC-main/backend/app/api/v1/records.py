from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from datetime import datetime, timezone
from app.db.session import get_db
from app.schemas.record import RecordCreate, RecordUpdate, RecordResponse
from app.schemas.common import success_response
from app.core.deps import get_current_user, get_user_min_level, RequireScope
from app.models.all import DataRecord, User, EditRequest
from app.core.exceptions import APIException
from app.services.edit_request_service import check_edit_permission

router = APIRouter()

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def submit_record(
    data: RecordCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(RequireScope("records", "create"))
):
    """
    Create a new record.
    
    **Required scope:** records:create
    """
    if current_user.dept_id is None and get_user_min_level(current_user) != 0:
        raise APIException(status.HTTP_400_BAD_REQUEST, "bad_request", "User has no department")
        
    record = DataRecord(
        submitted_by=current_user.id,
        dept_id=current_user.dept_id,
        record_type=data.record_type,
        payload=data.payload,
        is_frozen=True,
        frozen_at=datetime.now(timezone.utc)
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return success_response(data=RecordResponse.model_validate(record).model_dump())

@router.get("/", response_model=dict)
async def list_records(db: AsyncSession = Depends(get_db), current_user: User = Depends(RequireScope("records", "read"))):
    """
    List all records (filtered by department if not root).
    
    **Required scope:** records:read
    """
    min_level = get_user_min_level(current_user)
    query = select(DataRecord)
    if min_level > 0:
        query = query.where(DataRecord.dept_id == current_user.dept_id)
        
    result = await db.execute(query)
    records = result.scalars().all()
    return success_response(data=[RecordResponse.model_validate(r).model_dump() for r in records])

@router.get("/{id}", response_model=dict)
async def get_record(id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(RequireScope("records", "read"))):
    """
    Get a specific record by ID.
    
    **Required scope:** records:read
    """
    record = await db.get(DataRecord, id)
    if not record:
        raise APIException(status.HTTP_404_NOT_FOUND, "not_found", "Record not found")
        
    min_level = get_user_min_level(current_user)
    if min_level > 0 and record.dept_id != current_user.dept_id:
         raise APIException(status.HTTP_403_FORBIDDEN, "hierarchy_violation", "Cannot access record outside your department")
         
    return success_response(data=RecordResponse.model_validate(record).model_dump())

@router.patch("/{id}", response_model=dict)
async def edit_record(
    id: UUID, 
    data: RecordUpdate, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(RequireScope("records", "update"))
):
    """
    Update a record (requires active edit window).
    
    **Required scope:** records:update
    """
    record = await db.get(DataRecord, id)
    if not record:
        raise APIException(status.HTTP_404_NOT_FOUND, "not_found", "Record not found")
        
    can_edit = await check_edit_permission(id, current_user, db)
    if not can_edit:
        raise APIException(status.HTTP_403_FORBIDDEN, "forbidden", "No active edit window for this record")
        
    record.payload = data.payload
    record.version += 1
    record.is_frozen = True # Re-freeze after edit
    record.frozen_at = datetime.now(timezone.utc)
    record.updated_at = datetime.now(timezone.utc)
    
    # Mark the request as completed so it can't be used again
    res = await db.execute(
        select(EditRequest).where(
            EditRequest.record_id == id,
            EditRequest.status == "approved"
        )
    )
    req = res.scalar_one_or_none()
    if req:
        req.status = "completed"
    
    await db.commit()
    await db.refresh(record)
    return success_response(data=RecordResponse.model_validate(record).model_dump())

@router.delete("/{id}", response_model=dict)
async def delete_record(
    id: UUID, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(RequireScope("records", "delete"))
):
    """
    Delete a record by ID.
    
    **Required scope:** records:delete
    """
    record = await db.get(DataRecord, id)
    if not record:
        raise APIException(status.HTTP_404_NOT_FOUND, "not_found", "Record not found")
    
    min_level = get_user_min_level(current_user)
    if min_level > 0 and record.dept_id != current_user.dept_id:
        raise APIException(status.HTTP_403_FORBIDDEN, "hierarchy_violation", "Cannot delete record outside your department")
    
    await db.delete(record)
    await db.commit()
    return success_response(data={"message": "Record deleted successfully"})

@router.post("/{id}/freeze", response_model=dict)
async def freeze_record(
    id: UUID, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(RequireScope("records", "admin"))
):
    """
    Freeze a record to prevent modifications.
    
    **Required scope:** records:admin
    """
    record = await db.get(DataRecord, id)
    if not record:
        raise APIException(status.HTTP_404_NOT_FOUND, "not_found", "Record not found")
    
    min_level = get_user_min_level(current_user)
    if min_level > 0 and record.dept_id != current_user.dept_id:
        raise APIException(status.HTTP_403_FORBIDDEN, "hierarchy_violation", "Cannot freeze record outside your department")
    
    if record.is_frozen:
        raise APIException(status.HTTP_400_BAD_REQUEST, "bad_request", "Record is already frozen")
    
    record.is_frozen = True
    record.frozen_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(record)
    return success_response(data=RecordResponse.model_validate(record).model_dump())

@router.post("/{id}/unfreeze", response_model=dict)
async def unfreeze_record(
    id: UUID, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(RequireScope("records", "admin"))
):
    """
    Unfreeze a record to allow modifications.
    
    **Required scope:** records:admin
    """
    record = await db.get(DataRecord, id)
    if not record:
        raise APIException(status.HTTP_404_NOT_FOUND, "not_found", "Record not found")
    
    min_level = get_user_min_level(current_user)
    if min_level > 0 and record.dept_id != current_user.dept_id:
        raise APIException(status.HTTP_403_FORBIDDEN, "hierarchy_violation", "Cannot unfreeze record outside your department")
    
    if not record.is_frozen:
        raise APIException(status.HTTP_400_BAD_REQUEST, "bad_request", "Record is not frozen")
    
    record.is_frozen = False
    record.frozen_at = None
    await db.commit()
    await db.refresh(record)
    return success_response(data=RecordResponse.model_validate(record).model_dump())