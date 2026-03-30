from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.schemas.auth import Login, Token, RefreshToken, UserCreateRoot
from app.schemas.common import success_response, error_response
from app.core.security import verify_password, create_access_token, create_refresh_token, get_password_hash
from app.models.all import User, Role, UserRole
from app.core.exceptions import APIException
from jose import jwt, JWTError
from app.core.config import settings

router = APIRouter()

# In-memory blacklist for POC
token_blacklist = set()

@router.post("/login", response_model=dict)
async def login(data: Login, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(data.password, user.hashed_password) or not user.is_active:
        raise APIException(status_code=status.HTTP_401_UNAUTHORIZED, error="invalid_credentials", detail="Invalid email or password")
    
    # fetch roles and scopes
    await db.refresh(user, ['roles', 'scopes', 'department'])
    
    # Map roles and include user scopes for each role to satisfy frontend logic
    roles_data = []
    user_scopes = [s.scope for s in user.scopes]
    for ur in user.roles:
        roles_data.append({
            "id": ur.role.id,
            "name": ur.role.name,
            "level": ur.role.level,
            "dept_id": ur.role.dept_id,
            "description": ur.role.description,
            "scopes": user_scopes
        })
        
    user_dict = {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "department_id": user.dept_id,
        "department": user.department,
        "roles": roles_data
    }
    
    from app.schemas.auth import UserAuthResponse
    user_data = UserAuthResponse.model_validate(user_dict)
    
    access_token = create_access_token(user.id, [r.role.name for r in user.roles], user.dept_id)
    refresh_token = create_refresh_token(user.id)
    
    return success_response(data={
        "access_token": access_token, 
        "refresh_token": refresh_token, 
        "token_type": "bearer",
        "user": user_data.model_dump(mode='json')
    })

@router.post("/refresh", response_model=dict)
async def refresh(data: RefreshToken, db: AsyncSession = Depends(get_db)):
    if data.refresh_token in token_blacklist:
        raise APIException(status_code=status.HTTP_401_UNAUTHORIZED, error="invalid_token", detail="Refresh token blacklisted")
    try:
        payload = jwt.decode(data.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise ValueError()
    except Exception:
        raise APIException(status_code=status.HTTP_401_UNAUTHORIZED, error="invalid_token", detail="Invalid refresh token")
        
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
         raise APIException(status_code=status.HTTP_401_UNAUTHORIZED, error="invalid_user", detail="User inactive or deleted")
         
    await db.refresh(user, ['roles'])
    roles_result = await db.execute(select(Role).join(UserRole).where(UserRole.user_id == user.id))
    role_names = [r.name for r in roles_result.scalars().all()]
    
    access_token = create_access_token(user.id, role_names, user.dept_id)
    return success_response(data={"access_token": access_token})

@router.post("/logout", response_model=dict)
async def logout(data: RefreshToken):
    token_blacklist.add(data.refresh_token)
    return success_response(message="Logged out successfully")

@router.post("/register", response_model=dict)
async def register_root(data: UserCreateRoot, db: AsyncSession = Depends(get_db)):
    # Check if a user already exists (bootstrap)
    result = await db.execute(select(User).limit(1))
    if result.scalar_one_or_none() is not None:
         from app.core.deps import get_current_user, get_user_min_level
         # If users exist, this must be called by root. We'll enforce this differently or manually here
         raise APIException(status_code=status.HTTP_403_FORBIDDEN, error="forbidden", detail="System already bootstrapped. Use /users to create users.")
         
    root_role = Role(name="root", level=0, description="Root Superuser")
    db.add(root_role)
    await db.commit()
    
    root_user = User(
        email=data.email,
        hashed_password=get_password_hash(data.password),
        full_name=data.full_name,
        is_active=True
    )
    db.add(root_user)
    await db.commit()
    
    db.add(UserRole(user_id=root_user.id, role_id=root_role.id, assigned_by=root_user.id))
    await db.commit()
    
    return success_response(data={"id": str(root_user.id)})