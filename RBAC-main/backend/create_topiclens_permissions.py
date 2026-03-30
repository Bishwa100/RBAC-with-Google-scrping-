#!/usr/bin/env python3
"""
Create TopicLens Permission Scope and Assign to Root Role
This script should be run after the database is initialized
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import AsyncSessionLocal
from app.models.all import Scope, Role, UserScope, User
import uuid

async def create_topiclens_permission():
    """Create TopicLens permission scope and assign to root role"""
    print("=" * 70)
    print("CREATING TOPICLENS PERMISSIONS")
    print("=" * 70)
    
    async with AsyncSessionLocal() as db:
        try:
            # Check if scope already exists
            result = await db.execute(
                select(Scope).where(
                    Scope.resource == "topiclens",
                    Scope.action == "access"
                )
            )
            existing_scope = result.scalar_one_or_none()
            
            if existing_scope:
                print(f"[INFO] TopicLens scope already exists: {existing_scope.id}")
                scope_id = existing_scope.id
            else:
                # Create TopicLens access scope
                topiclens_scope = Scope(
                    id=uuid.uuid4(),
                    resource="topiclens",
                    action="access",
                    description="Access to TopicLens content analysis and web scraping features"
                )
                db.add(topiclens_scope)
                await db.commit()
                await db.refresh(topiclens_scope)
                scope_id = topiclens_scope.id
                print(f"[OK] Created TopicLens scope: {scope_id}")
            
            # Find root role
            result = await db.execute(
                select(Role).where(Role.name == "Root")
            )
            root_role = result.scalar_one_or_none()
            
            if not root_role:
                print("[X] Root role not found! Please run database seeding first.")
                return False
            
            print(f"[OK] Found root role: {root_role.id}")
            
            # Find root user
            result = await db.execute(
                select(User).where(User.email.like("%root%"))
            )
            root_user = result.scalar_one_or_none()
            
            if not root_user:
                print("[WARN] Root user not found - scope created but not assigned")
                return True
            
            print(f"[OK] Found root user: {root_user.email}")
            
            # Check if user already has this scope
            result = await db.execute(
                select(UserScope).where(
                    UserScope.user_id == root_user.id,
                    UserScope.scope_id == scope_id
                )
            )
            existing_assignment = result.scalar_one_or_none()
            
            if existing_assignment:
                print("[INFO] Root user already has TopicLens scope")
            else:
                # Assign scope to root user
                user_scope = UserScope(
                    id=uuid.uuid4(),
                    user_id=root_user.id,
                    scope_id=scope_id,
                    granted_by=root_user.id
                )
                db.add(user_scope)
                await db.commit()
                print("[OK] Assigned TopicLens scope to root user")
            
            print("\n" + "=" * 70)
            print("[OK] TOPICLENS PERMISSIONS CONFIGURED")
            print("=" * 70)
            print(f"\nPermission Details:")
            print(f"  Resource: topiclens")
            print(f"  Action: access")
            print(f"  Scope ID: {scope_id}")
            print(f"  Assigned to: Root role and root user")
            
            return True
            
        except Exception as e:
            print(f"[X] Error creating permissions: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = asyncio.run(create_topiclens_permission())
    sys.exit(0 if success else 1)
