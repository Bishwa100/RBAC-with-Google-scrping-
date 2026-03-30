from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from datetime import datetime, timezone
from app.models.all import DataRecord, EditRequest, ApprovalStep, User
from app.core.exceptions import APIException
from app.core.deps import get_user_min_level
from fastapi import status

async def create_edit_request(record_id: UUID, requester: User, reason: str, db: AsyncSession) -> EditRequest:
    record = await db.get(DataRecord, record_id)
    if not record:
        raise APIException(status.HTTP_404_NOT_FOUND, "not_found", "Record not found")
        
    if record.submitted_by != requester.id:
        raise APIException(status.HTTP_403_FORBIDDEN, "forbidden", "Only the submitter can request an edit")
        
    if not record.is_frozen:
        raise APIException(status.HTTP_400_BAD_REQUEST, "bad_request", "Record is not frozen")
        
    # Check if active request exists
    res = await db.execute(select(EditRequest).where(EditRequest.record_id == record_id, EditRequest.status == "pending"))
    if res.scalar_one_or_none():
         raise APIException(status.HTTP_409_CONFLICT, "conflict", "A pending edit request already exists for this record")

    requester_level = get_user_min_level(requester)
    
    req = EditRequest(
        record_id=record_id,
        requested_by=requester.id,
        reason=reason,
        status="pending",
        approvals_required=2,
        edit_window_minutes=30
    )
    db.add(req)
    await db.flush()

    # Create 2 approval steps
    level_1 = max(0, requester_level - 1)
    level_2 = max(0, requester_level - 2)
    
    step1 = ApprovalStep(
        request_id=req.id,
        step_level=1,
        required_min_role_level=level_1
    )
    step2 = ApprovalStep(
        request_id=req.id,
        step_level=2,
        required_min_role_level=level_2
    )
    db.add_all([step1, step2])
    await db.commit()
    await db.refresh(req)
    return req

async def process_approval(request_id: UUID, approver: User, decision: str, comment: str, db: AsyncSession):
    req = await db.get(EditRequest, request_id, options=[selectinload(EditRequest.steps)])
    if not req:
        raise APIException(status.HTTP_404_NOT_FOUND, "not_found", "Edit request not found")
        
    if req.status != "pending":
         raise APIException(status.HTTP_400_BAD_REQUEST, "bad_request", f"Request is already {req.status}")
         
    record = await db.get(DataRecord, req.record_id)
    # Root bypasses dept check
    approver_level = get_user_min_level(approver)
    if approver_level > 0 and record.dept_id != approver.dept_id:
         raise APIException(status.HTTP_403_FORBIDDEN, "hierarchy_violation", "Approver must be from the same department")

    # Check if already voted
    for step in req.steps:
        if step.approver_id == approver.id:
            raise APIException(status.HTTP_409_CONFLICT, "conflict", "You have already voted on this request")

    # Find eligible step
    target_step = None
    for step in sorted(req.steps, key=lambda s: s.step_level):
        if step.approver_id is None and approver_level <= step.required_min_role_level:
            target_step = step
            break
            
    if not target_step:
         raise APIException(status.HTTP_403_FORBIDDEN, "hierarchy_violation", "You are not eligible to approve any pending steps for this request")
         
    target_step.decision = decision
    target_step.decided_at = datetime.now(timezone.utc)
    target_step.approver_id = approver.id
    target_step.comment = comment

    if decision == "rejected":
        req.status = "rejected"
        req.resolved_at = datetime.now(timezone.utc)
    elif decision == "approved":
        req.approvals_received += 1
        if req.approvals_received >= req.approvals_required:
            req.status = "approved"
            req.resolved_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(req)
    return req

async def check_edit_permission(record_id: UUID, user: User, db: AsyncSession) -> bool:
    record = await db.get(DataRecord, record_id)
    if not record or record.submitted_by != user.id:
        return False
        
    res = await db.execute(
        select(EditRequest)
        .where(
            EditRequest.record_id == record_id,
            EditRequest.status == "approved"
        )
    )
    valid_req = res.scalar_one_or_none()
    return valid_req is not None