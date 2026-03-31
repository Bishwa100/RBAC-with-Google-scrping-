from typing import Optional, List
from fastapi import APIRouter, Depends, status, UploadFile, File, Request, Form
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from datetime import datetime, timezone
import io
import pandas as pd
from PyPDF2 import PdfReader
import httpx
import re
from app.db.session import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.common import success_response
from app.core.deps import get_current_user, RequireScope, get_user_min_level, can_manage_user
from app.models.all import User, UserRole, Role, Scope, UserScope, DataRecord, EditRequest, DocumentExtraction
from app.core.exceptions import APIException
from app.core.security import get_password_hash
from app.api.v1.audit import log_action
from app.core.config import settings

router = APIRouter()

@router.get("/stats/{id}", response_model=dict)
async def get_user_stats(id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(RequireScope("users", "read"))):
    """Get user statistics. Required scope: users:read"""
    target_user = await db.get(User, id)
    if not target_user:
        raise APIException(status.HTTP_404_NOT_FOUND, "not_found", "User not found")
    
    if not can_manage_user(current_user, target_user) and current_user.id != target_user.id:
        raise APIException(status.HTTP_403_FORBIDDEN, "hierarchy_violation", "Cannot view stats for this user")

    # Record stats
    records_res = await db.execute(select(DataRecord).where(DataRecord.submitted_by == id))
    records = records_res.scalars().all()
    
    # Request stats
    requests_res = await db.execute(select(EditRequest).where(EditRequest.requested_by == id))
    requests = requests_res.scalars().all()

    # Activity by month (simple heuristic for chart)
    # In a real app we'd use group_by at SQL level
    activity_data = {}
    for r in records:
        month = r.created_at.strftime("%Y-%m")
        activity_data[month] = activity_data.get(month, 0) + 1

    stats = {
        "total_records": len(records),
        "total_requests": len(requests),
        "pending_requests": len([r for r in requests if r.status == "pending"]),
        "approved_requests": len([r for r in requests if r.status == "approved"]),
        "rejected_requests": len([r for r in requests if r.status == "rejected"]),
        "completed_requests": len([r for r in requests if r.status == "completed"]),
        "activity_over_time": [{"date": k, "count": v} for k, v in sorted(activity_data.items())]
    }
    
    return success_response(data=stats)

@router.get("/", response_model=dict)
async def list_users(db: AsyncSession = Depends(get_db), current_user: User = Depends(RequireScope("users", "read"))):
    """List all users. Required scope: users:read"""
    min_level = get_user_min_level(current_user)
    query = select(User).options(
        selectinload(User.roles).selectinload(UserRole.role),
        selectinload(User.department)
    )
    
    if min_level > 0:
        query = query.where(User.dept_id == current_user.dept_id)
        
    result = await db.execute(query)
    users = result.scalars().all()
    
    # Filter and Transform users to include nested roles and department
    await db.refresh(current_user, ['scopes'])
    user_scopes = [s.scope for s in current_user.scopes]
    
    transformed_users = []
    for u in users:
        # Filtering logic
        if min_level == 0 or get_user_min_level(u) > min_level or u.id == current_user.id:
            # Transformation logic
            u_roles = []
            for ur in u.roles:
                u_roles.append({
                    "id": ur.role.id,
                    "name": ur.role.name,
                    "level": ur.role.level,
                    "dept_id": ur.role.dept_id,
                    "description": ur.role.description,
                    "created_at": ur.role.created_at,
                    "scopes": user_scopes if u.id == current_user.id else []
                })
                
            transformed_users.append({
                "id": u.id,
                "email": u.email,
                "full_name": u.full_name,
                "department_id": u.dept_id,
                "department": u.department,
                "is_active": u.is_active,
                "roles": u_roles,
                "created_at": u.created_at
            })
             
    return success_response(data=[UserResponse.model_validate(u).model_dump(mode='json') for u in transformed_users])

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    full_name: Optional[str] = Form(None),
    dept_id: Optional[UUID] = Form(None),
    role_id: Optional[UUID] = Form(None),
    details_json: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(RequireScope("users", "create"))
):
    """Create a new user. Required scope: users:create"""
    manager_level = get_user_min_level(current_user)
    
    # Parse details
    details = None
    if details_json:
        try:
            details = json.loads(details_json)
        except:
            pass

    # Validation
    if manager_level > 0 and dept_id and dept_id != current_user.dept_id:
        raise APIException(status.HTTP_403_FORBIDDEN, "hierarchy_violation", "Cannot create user outside your department")
        
    target_role = await db.get(Role, role_id) if role_id else None
    if target_role and manager_level >= target_role.level and manager_level != 0:
        raise APIException(status.HTTP_403_FORBIDDEN, "hierarchy_violation", "Cannot assign role level equal or higher than yours")

    # Check email exists
    res = await db.execute(select(User).where(User.email == email))
    if res.scalar_one_or_none():
         raise APIException(status.HTTP_409_CONFLICT, "conflict", "Email already registered")

    new_user = User(
        email=email,
        hashed_password=get_password_hash(password),
        full_name=full_name,
        dept_id=dept_id,
        created_by=current_user.id,
        details=details
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    if target_role:
        db.add(UserRole(user_id=new_user.id, role_id=target_role.id, assigned_by=current_user.id))
        await db.commit()

    if file:
        await log_action(
            db, 
            action="USER_DOCUMENT_UPLOAD", 
            user_id=current_user.id, 
            resource="users", 
            resource_id=new_user.id,
            dept_id=current_user.dept_id,
            details={"filename": file.filename},
            request=request
        )

    await log_action(
        db, 
        action="USER_CREATE", 
        user_id=current_user.id, 
        resource="users", 
        resource_id=new_user.id,
        dept_id=current_user.dept_id,
        details={"email": email},
        request=request
    )

    # Fetch needed relations for response
    await db.refresh(new_user, ['roles', 'department'])
    # Transform for response logic similar to list
    u_roles = []
    for ur in new_user.roles:
        u_roles.append({
            "id": ur.role.id,
            "name": ur.role.name,
            "level": ur.role.level,
            "dept_id": ur.role.dept_id,
            "description": ur.role.description,
            "created_at": ur.role.created_at,
            "scopes": []
        })
    
    user_dict = {
        "id": new_user.id,
        "email": new_user.email,
        "full_name": new_user.full_name,
        "department_id": new_user.dept_id,
        "department": new_user.department,
        "is_active": new_user.is_active,
        "roles": u_roles,
        "created_at": new_user.created_at,
        "details": new_user.details
    }

    return success_response(data=UserResponse.model_validate(user_dict).model_dump(mode='json'))

@router.post("/extract", response_model=dict)
async def extract_user_info(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RequireScope("users", "admin"))
):
    """Extract user information from document. Required scope: users:admin"""
    # Forward the file to doc_extractor service
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            files = {'file': (file.filename, await file.read(), file.content_type)}
            response = await client.post(f"{settings.DOC_EXTRACTOR_URL}/extract", files=files)
            
            if response.status_code != 200:
                raise APIException(status.HTTP_500_INTERNAL_SERVER_ERROR, "extraction_failed", f"Doc extractor returned {response.status_code}")
            
            result = response.json()
            extraction_data = result.get("data", {})
            
            # Store in database
            doc_ext = DocumentExtraction(
                filename=file.filename,
                content_type=file.content_type,
                extraction_data=extraction_data
            )
            db.add(doc_ext)
            await db.commit()
            
            return success_response(data=extraction_data)
    except Exception as e:
        raise APIException(status.HTTP_500_INTERNAL_SERVER_ERROR, "extraction_error", str(e))

@router.post("/analyze", response_model=dict)
async def analyze_user_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RequireScope("users", "admin"))
):
    """Analyze user file and extract information. Required scope: users:admin"""
    contents = await file.read()
    filename = file.filename.lower()
    text = ""

    if filename.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(io.BytesIO(contents))
        # Take first row as candidate if exists
        if not df.empty:
            row = df.iloc[0].to_dict()
            text = " ".join([str(v) for v in row.values()])
    elif filename.endswith('.csv'):
        df = pd.read_csv(io.BytesIO(contents))
        if not df.empty:
            row = df.iloc[0].to_dict()
            text = " ".join([str(v) for v in row.values()])
    elif filename.endswith('.pdf'):
        reader = PdfReader(io.BytesIO(contents))
        for page in reader.pages:
            text += page.extract_text() or ""
    elif filename.endswith(('.png', '.jpg', '.jpeg')):
        # Mock OCR logic for now since Tesseract requires system binary
        text = "Name: MOCKED_OPERATIVE Email: mocked@node.local Phone: +1234567890"
    
    # Simple heuristic extraction
    extracted_data = {
        "full_name": "",
        "email": "",
        "phone": ""
    }

    # Extract email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    if email_match:
        extracted_data["email"] = email_match.group(0)

    # Extract phone (very basic)
    phone_match = re.search(r'\+?\d{10,15}', text)
    if phone_match:
        extracted_data["phone"] = phone_match.group(0)

    # Extract name (heuristic: first line or common label)
    name_patterns = [
        r'Name:\s*([^\n\r]+)',
        r'Full Name:\s*([^\n\r]+)',
        r'Designation:\s*([^\n\r]+)'
    ]
    for pattern in name_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            extracted_data["full_name"] = match.group(1).strip()
            break
    
    if not extracted_data["full_name"] and text:
        # Fallback: take first 2-3 words of first line
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if lines:
            extracted_data["full_name"] = " ".join(lines[0].split()[:3])

    return success_response(data=extracted_data)

@router.post("/upload", response_model=dict)
async def upload_users(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RequireScope("users", "create"))
):
    """Bulk upload users from file. Required scope: users:create"""
    contents = await file.read()
    filename = file.filename.lower()
    users_to_create = []

    if filename.endswith('.xlsx') or filename.endswith('.xls'):
        df = pd.read_excel(io.BytesIO(contents))
        users_to_create = df.to_dict('records')
    elif filename.endswith('.csv'):
        df = pd.read_csv(io.BytesIO(contents))
        users_to_create = df.to_dict('records')
    elif filename.endswith('.pdf'):
        # Basic PDF text extraction logic (heuristic)
        reader = PdfReader(io.BytesIO(contents))
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return success_response(message="PDF analyzed. Manual review required for identity verification documents.")
    elif filename.endswith(('.png', '.jpg', '.jpeg')):
        return success_response(message="Identity document uploaded. OCR analysis pending.")
    else:
        raise APIException(status.HTTP_400_BAD_REQUEST, "bad_request", "Unsupported file format")

    created_count = 0
    for u_data in users_to_create:
        email = u_data.get('email')
        full_name = u_data.get('full_name')
        if not email or not full_name: continue
        
        # Check exists
        res = await db.execute(select(User).where(User.email == email))
        if res.scalar_one_or_none(): continue

        new_user = User(
            email=email,
            hashed_password=get_password_hash("Pass123!"), # Default password for bulk
            full_name=full_name,
            dept_id=current_user.dept_id,
            created_by=current_user.id
        )
        db.add(new_user)
        created_count += 1

    await db.commit()
    
    await log_action(
        db, 
        action="USER_BULK_UPLOAD", 
        user_id=current_user.id, 
        resource="users",
        dept_id=current_user.dept_id,
        details={"filename": filename, "count": created_count},
        request=request
    )

    return success_response(message=f"Bulk process complete. Created {created_count} users.")

@router.get("/me", response_model=dict)
async def get_me(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    await db.refresh(current_user, ['roles', 'scopes', 'department'])
    
    u_roles = []
    user_scopes = [s.scope for s in current_user.scopes]
    for ur in current_user.roles:
        u_roles.append({
            "id": ur.role.id,
            "name": ur.role.name,
            "level": ur.role.level,
            "dept_id": ur.role.dept_id,
            "description": ur.role.description,
            "created_at": ur.role.created_at,
            "scopes": user_scopes
        })
        
    user_dict = {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "department_id": current_user.dept_id,
        "department": current_user.department,
        "is_active": current_user.is_active,
        "roles": u_roles,
        "created_at": current_user.created_at
    }
    return success_response(data=UserResponse.model_validate(user_dict).model_dump(mode='json'))

@router.get("/{id}", response_model=dict)
async def get_user(id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(RequireScope("users", "read"))):
    """Get user by ID. Required scope: users:read"""
    target_user = await db.get(User, id)
    if not target_user:
        raise APIException(status.HTTP_404_NOT_FOUND, "not_found", "User not found")
    
    await db.refresh(target_user, ['roles', 'department'])
    if not can_manage_user(current_user, target_user) and current_user.id != target_user.id:
        raise APIException(status.HTTP_403_FORBIDDEN, "hierarchy_violation", "Cannot view this user")
        
    u_roles = []
    for ur in target_user.roles:
        u_roles.append({
            "id": ur.role.id,
            "name": ur.role.name,
            "level": ur.role.level,
            "dept_id": ur.role.dept_id,
            "description": ur.role.description,
            "created_at": ur.role.created_at,
            "scopes": []
        })
        
    user_dict = {
        "id": target_user.id,
        "email": target_user.email,
        "full_name": target_user.full_name,
        "department_id": target_user.dept_id,
        "department": target_user.department,
        "is_active": target_user.is_active,
        "roles": u_roles,
        "created_at": target_user.created_at
    }
        
    return success_response(data=UserResponse.model_validate(user_dict).model_dump(mode='json'))

@router.patch("/{id}", response_model=dict)
async def update_user(
    id: UUID, 
    data: UserUpdate, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(RequireScope("users", "update"))
):
    """Update user. Required scope: users:update"""
    target_user = await db.get(User, id)
    if not target_user:
        raise APIException(status.HTTP_404_NOT_FOUND, "not_found", "User not found")
        
    await db.refresh(target_user, ['roles'])
    if not can_manage_user(current_user, target_user):
        raise APIException(status.HTTP_403_FORBIDDEN, "hierarchy_violation", "Cannot manage this user")

    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(target_user, k, v)
        
    await db.commit()
    await db.refresh(target_user, ['roles', 'department'])
    
    u_roles = []
    for ur in target_user.roles:
        u_roles.append({
            "id": ur.role.id,
            "name": ur.role.name,
            "level": ur.role.level,
            "dept_id": ur.role.dept_id,
            "description": ur.role.description,
            "created_at": ur.role.created_at,
            "scopes": []
        })
        
    user_dict = {
        "id": target_user.id,
        "email": target_user.email,
        "full_name": target_user.full_name,
        "department_id": target_user.dept_id,
        "department": target_user.department,
        "is_active": target_user.is_active,
        "roles": u_roles,
        "created_at": target_user.created_at
    }
    return success_response(data=UserResponse.model_validate(user_dict).model_dump(mode='json'))

@router.delete("/{id}", response_model=dict)
async def delete_user(
    id: UUID, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(RequireScope("users", "delete"))
):
    """Delete/deactivate user. Required scope: users:delete"""
    target_user = await db.get(User, id)
    if not target_user:
        raise APIException(status.HTTP_404_NOT_FOUND, "not_found", "User not found")
        
    await db.refresh(target_user, ['roles'])
    if not can_manage_user(current_user, target_user):
         raise APIException(status.HTTP_403_FORBIDDEN, "hierarchy_violation", "Cannot manage this user")

    target_user.is_active = False
    await db.commit()
    return success_response(message="User deactivated")

@router.post("/{id}/roles", response_model=dict)
async def assign_role(
    id: UUID, 
    role_id: UUID,
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    target_user = await db.get(User, id)
    target_role = await db.get(Role, role_id)
    if not target_user or not target_role:
        raise APIException(status.HTTP_404_NOT_FOUND, "not_found", "User or Role not found")
        
    await db.refresh(target_user, ['roles'])
    if not can_manage_user(current_user, target_user):
         raise APIException(status.HTTP_403_FORBIDDEN, "hierarchy_violation", "Cannot manage this user")
         
    manager_level = get_user_min_level(current_user)
    if manager_level >= target_role.level and manager_level != 0:
        raise APIException(status.HTTP_403_FORBIDDEN, "hierarchy_violation", "Cannot assign role equal or higher than yours")

    res = await db.execute(select(UserRole).where(UserRole.user_id == id, UserRole.role_id == role_id))
    if res.scalar_one_or_none():
         raise APIException(status.HTTP_409_CONFLICT, "conflict", "Role already assigned")

    db.add(UserRole(user_id=id, role_id=role_id, assigned_by=current_user.id))
    await db.commit()
    return success_response(message="Role assigned")

@router.delete("/{id}/roles/{role_id}", response_model=dict)
async def remove_role(
    id: UUID, 
    role_id: UUID,
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    target_user = await db.get(User, id)
    if not target_user:
        raise APIException(status.HTTP_404_NOT_FOUND, "not_found", "User not found")
        
    await db.refresh(target_user, ['roles'])
    if not can_manage_user(current_user, target_user):
         raise APIException(status.HTTP_403_FORBIDDEN, "hierarchy_violation", "Cannot manage this user")

    res = await db.execute(select(UserRole).where(UserRole.user_id == id, UserRole.role_id == role_id))
    ur = res.scalar_one_or_none()
    if not ur:
        raise APIException(status.HTTP_404_NOT_FOUND, "not_found", "User does not have this role")

    await db.delete(ur)
    await db.commit()
    return success_response(message="Role removed")

@router.get("/{id}/scopes", response_model=dict)
async def list_user_scopes(
    id: UUID, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    res = await db.execute(select(UserScope).join(Scope).where(UserScope.user_id == id, UserScope.revoked_at == None))
    scopes = [ur.scope for ur in res.scalars().all()]
    from app.schemas.scope import ScopeResponse
    return success_response(data=[ScopeResponse.model_validate(s).model_dump() for s in scopes])

@router.post("/{id}/scopes", response_model=dict)
async def grant_scope(
    id: UUID, 
    scope_id: UUID,
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    target_user = await db.get(User, id)
    scope = await db.get(Scope, scope_id)
    if not target_user or not scope:
        raise APIException(status.HTTP_404_NOT_FOUND, "not_found", "User or Scope not found")

    await db.refresh(target_user, ['roles'])
    if not can_manage_user(current_user, target_user):
         raise APIException(status.HTTP_403_FORBIDDEN, "hierarchy_violation", "Cannot manage this user")

    # Check if assigner has this scope
    if get_user_min_level(current_user) != 0:
        has_scope = False
        await db.refresh(current_user, ['scopes'])
        for us in current_user.scopes:
            if us.revoked_at is None and us.scope_id == scope_id:
                has_scope = True
                break
        if not has_scope:
            raise APIException(status.HTTP_403_FORBIDDEN, "hierarchy_violation", "Cannot grant a scope you do not possess")

    db.add(UserScope(user_id=id, scope_id=scope_id, granted_by=current_user.id))
    await db.commit()
    return success_response(message="Scope granted")

@router.delete("/{id}/scopes/{scope_id}", response_model=dict)
async def revoke_scope(
    id: UUID, 
    scope_id: UUID,
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    target_user = await db.get(User, id)
    if not target_user:
        raise APIException(status.HTTP_404_NOT_FOUND, "not_found", "User not found")

    await db.refresh(target_user, ['roles'])
    if not can_manage_user(current_user, target_user):
         raise APIException(status.HTTP_403_FORBIDDEN, "hierarchy_violation", "Cannot manage this user")

    res = await db.execute(select(UserScope).where(UserScope.user_id == id, UserScope.scope_id == scope_id, UserScope.revoked_at == None))
    us = res.scalar_one_or_none()
    if not us:
         raise APIException(status.HTTP_404_NOT_FOUND, "not_found", "Active scope grant not found")
         
    us.revoked_at = datetime.now(timezone.utc)
    await db.commit()
    return success_response(message="Scope revoked")