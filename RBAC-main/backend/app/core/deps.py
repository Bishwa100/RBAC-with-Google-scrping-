from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.core.config import settings
from app.db.session import get_db
from app.models.all import User, Role, UserRole, UserScope, Scope
from app.models.rbac_extensions import RoleScope
from app.core.exceptions import APIException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    credentials_exception = APIException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        error="invalid_credentials",
        detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(
        select(User).options(
            selectinload(User.roles).selectinload(UserRole.role).selectinload(Role.role_scopes).selectinload(RoleScope.scope),
            selectinload(User.scopes).selectinload(UserScope.scope)
        )
        .where(User.id == UUID(user_id))
    )
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise credentials_exception
    return user

class RequireScope:
    def __init__(self, resource: str, action: str):
        self.resource = resource
        self.action = action

    async def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        # Check if root (level 0 bypasses all scope checks)
        is_root = any(ur.role.level == 0 for ur in current_user.roles)
        if is_root:
            return current_user

        has_scope = False
        
        # Check direct user scopes
        for us in current_user.scopes:
            if us.revoked_at is None:
                if us.scope.resource == self.resource and us.scope.action == self.action:
                    has_scope = True
                    break
        
        # If not found in direct scopes, check role-inherited scopes
        if not has_scope:
            for ur in current_user.roles:
                # Check if role assignment is still valid (not expired)
                if ur.expires_at is None or ur.expires_at > ur.assigned_at:
                    for rs in ur.role.role_scopes:
                        if rs.scope.resource == self.resource and rs.scope.action == self.action:
                            has_scope = True
                            break
                if has_scope:
                    break
        
        if not has_scope:
            raise APIException(
                status_code=status.HTTP_403_FORBIDDEN,
                error="insufficient_scope",
                detail=f"Missing required scope: {self.resource}:{self.action}"
            )
        return current_user

class RequireRoleLevel:
    def __init__(self, max_level: int):
        self.max_level = max_level

    async def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        min_level = min([ur.role.level for ur in current_user.roles], default=999)
        if min_level > self.max_level:
             raise APIException(
                status_code=status.HTTP_403_FORBIDDEN,
                error="hierarchy_violation",
                detail=f"Requires role level <= {self.max_level}"
            )
        return current_user

def get_user_min_level(user: User) -> int:
    return min([ur.role.level for ur in user.roles], default=999)

def can_manage_user(manager: User, target_user: User) -> bool:
    manager_level = get_user_min_level(manager)
    if manager_level == 0:
        return True
    target_level = get_user_min_level(target_user)
    if manager_level >= target_level:
        return False
    if manager.dept_id != target_user.dept_id:
        return False
    return True

class RequireRootUser:
    """Dependency to ensure only root/admin users can access"""
    
    async def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        is_root = any(
            ur.role.name.lower() in ['root', 'admin', 'superadmin'] 
            or ur.role.level == 0
            for ur in current_user.roles
        )
        
        if not is_root:
            raise APIException(
                status_code=status.HTTP_403_FORBIDDEN,
                error="root_required",
                detail="This operation requires root or admin privileges"
            )
        return current_user

def is_root_user(user: User) -> bool:
    """Helper function to check if user is root/admin"""
    return any(
        ur.role.name.lower() in ['root', 'admin', 'superadmin'] 
        or ur.role.level == 0
        for ur in user.roles
    )
