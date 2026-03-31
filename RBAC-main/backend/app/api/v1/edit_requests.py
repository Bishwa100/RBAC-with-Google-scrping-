from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from app.db.session import get_db
from app.schemas.edit_request import EditRequestCreate, ApprovalDecision, EditRequestResponse
from app.schemas.common import success_response
from app.core.deps import get_current_user, get_user_min_level, RequireScope
from app.models.all import EditRequest, User, DataRecord
from app.core.exceptions import APIException
from app.services.edit_request_service import create_edit_request, process_approval

router = APIRouter()

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_request(
    data: EditRequestCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(RequireScope("edit_requests", "create"))
):
    """
    Create a new edit request for a record.
    
    **Required scope:** edit_requests:create
    """
    req = await create_edit_request(data.record_id, current_user, data.reason, db)
    return success_response(data=EditRequestResponse.model_validate(req).model_dump())

@router.get("/", response_model=dict)
async def list_requests(db: AsyncSession = Depends(get_db), current_user: User = Depends(RequireScope("edit_requests", "read"))):
    """
    List edit requests (filtered by department/user based on role).
    
    **Required scope:** edit_requests:read
    """
    min_level = get_user_min_level(current_user)
    
    query = select(EditRequest).options(selectinload(EditRequest.steps))
    
    if min_level > 0:
        if min_level <= 2:
            # admin / manager sees dept
            query = query.join(DataRecord).where(DataRecord.dept_id == current_user.dept_id)
        else:
            # worker sees own
            query = query.where(EditRequest.requested_by == current_user.id)
            
    result = await db.execute(query)
    reqs = result.scalars().all()
    return success_response(data=[EditRequestResponse.model_validate(r).model_dump() for r in reqs])

@router.get("/{id}", response_model=dict)
async def get_request(id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(RequireScope("edit_requests", "read"))):
    """
    Get a specific edit request by ID.
    
    **Required scope:** edit_requests:read
    """
    req = await db.get(EditRequest, id, options=[selectinload(EditRequest.steps)])
    if not req:
        raise APIException(status.HTTP_404_NOT_FOUND, "not_found", "Request not found")
        
    return success_response(data=EditRequestResponse.model_validate(req).model_dump())

@router.post("/{id}/approve", response_model=dict)
async def approve_request(
    id: UUID, 
    data: ApprovalDecision, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(RequireScope("edit_requests", "approve"))
):
    """
    Approve or reject an edit request.
    
    **Required scope:** edit_requests:approve
    """
    if data.decision not in ["approved", "rejected"]:
        raise APIException(status.HTTP_400_BAD_REQUEST, "bad_request", "Decision must be 'approved' or 'rejected'")
    req = await process_approval(id, current_user, data.decision, data.comment or "", db)
    return success_response(data=EditRequestResponse.model_validate(req).model_dump())

@router.post("/{id}/reject", response_model=dict)
async def reject_request(
    id: UUID, 
    data: ApprovalDecision, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(RequireScope("edit_requests", "approve"))
):
    """
    Reject an edit request.
    
    **Required scope:** edit_requests:approve
    """
    req = await process_approval(id, current_user, "rejected", data.comment or "", db)
    return success_response(data=EditRequestResponse.model_validate(req).model_dump())