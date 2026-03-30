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
    min_level = get_user_min_level(current_user)
    query = select(DataRecord)
    if min_level > 0:
        query = query.where(DataRecord.dept_id == current_user.dept_id)
        
    result = await db.execute(query)
    records = result.scalars().all()
    return success_response(data=[RecordResponse.model_validate(r).model_dump() for r in records])

@router.get("/{id}", response_model=dict)
async def get_record(id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(RequireScope("records", "read"))):
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