from fastapi import APIRouter, Depends, status, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from typing import List, Optional
import csv
import io
from app.db.session import get_db
from app.schemas.audit import AuditLogResponse
from app.schemas.common import success_response
from app.core.deps import get_current_user, RequireScope, get_user_min_level
from app.models.all import AuditLog, User, Department

router = APIRouter()

@router.get("/", response_model=dict)
async def list_audit_logs(
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(RequireScope("audit", "read"))
):
    """
    List audit logs (filtered by department if not root).
    
    **Required scope:** audit:read
    """
    min_level = get_user_min_level(current_user)
    
    query = select(AuditLog).options(
        selectinload(AuditLog.user),
        selectinload(AuditLog.department)
    ).order_by(AuditLog.created_at.desc())
    
    if min_level > 0:
        # Dept managers see their dept logs or global logs if relevant to their dept?
        # For simplicity, let's say they see logs where dept_id matches theirs.
        query = query.where(AuditLog.dept_id == current_user.dept_id)
        
    result = await db.execute(query.limit(100))
    logs = result.scalars().all()
    
    transformed_logs = []
    for log in logs:
        l_dict = AuditLogResponse.model_validate(log).model_dump(mode='json')
        l_dict['user_email'] = log.user.email if log.user else "SYSTEM"
        l_dict['dept_name'] = log.department.name if log.department else "GLOBAL"
        transformed_logs.append(l_dict)
        
    return success_response(data=transformed_logs)

@router.post("/export", response_model=dict)
async def export_audit_logs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RequireScope("audit", "export")),
    format: str = "csv"
):
    """
    Export audit logs to CSV or JSON format.
    
    **Required scope:** audit:export
    """
    min_level = get_user_min_level(current_user)
    
    query = select(AuditLog).options(
        selectinload(AuditLog.user),
        selectinload(AuditLog.department)
    ).order_by(AuditLog.created_at.desc())
    
    if min_level > 0:
        query = query.where(AuditLog.dept_id == current_user.dept_id)
    
    result = await db.execute(query.limit(1000))
    logs = result.scalars().all()
    
    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow([
            'ID', 'Timestamp', 'User Email', 'Action', 'Resource', 
            'Resource ID', 'Department', 'IP Address', 'Details'
        ])
        
        for log in logs:
            writer.writerow([
                str(log.id),
                log.created_at.isoformat(),
                log.user.email if log.user else "SYSTEM",
                log.action,
                log.resource or "",
                str(log.resource_id) if log.resource_id else "",
                log.department.name if log.department else "GLOBAL",
                log.ip_address or "",
                str(log.details) if log.details else ""
            ])
        
        csv_content = output.getvalue()
        output.close()
        
        return success_response(data={
            "format": "csv",
            "content": csv_content,
            "count": len(logs)
        })
    else:
        transformed_logs = []
        for log in logs:
            l_dict = AuditLogResponse.model_validate(log).model_dump(mode='json')
            l_dict['user_email'] = log.user.email if log.user else "SYSTEM"
            l_dict['dept_name'] = log.department.name if log.department else "GLOBAL"
            transformed_logs.append(l_dict)
        
        return success_response(data={
            "format": "json",
            "logs": transformed_logs,
            "count": len(logs)
        })

async def log_action(
    db: AsyncSession,
    action: str,
    user_id: Optional[UUID] = None,
    resource: Optional[str] = None,
    resource_id: Optional[UUID] = None,
    dept_id: Optional[UUID] = None,
    details: Optional[dict] = None,
    request: Optional[Request] = None
):
    ip = request.client.host if request else None
    new_log = AuditLog(
        user_id=user_id,
        action=action,
        resource=resource,
        resource_id=resource_id,
        dept_id=dept_id,
        details=details,
        ip_address=ip
    )
    db.add(new_log)
    await db.commit()
