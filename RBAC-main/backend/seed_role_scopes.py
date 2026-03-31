"""
Role-Scope Assignment Script
Assigns default scopes to existing roles based on role levels
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.all import Role, Scope
from app.models.rbac_extensions import RoleScope
from app.core.config import get_settings

settings = get_settings()

# Default role-scope assignments
# Format: role_name -> list of (resource, action) tuples
ROLE_SCOPE_ASSIGNMENTS = {
    # Root role (Level 0) - bypasses checks programmatically, but assign for completeness
    "Root": [
        # All scopes - but root will bypass checks anyway
        ("auth", "logout"),
        ("auth", "bootstrap"),
        ("users", "read"),
        ("users", "create"),
        ("users", "update"),
        ("users", "delete"),
        ("users", "admin"),
        ("roles", "read"),
        ("roles", "create"),
        ("roles", "update"),
        ("roles", "delete"),
        ("scopes", "read"),
        ("scopes", "create"),
        ("scopes", "update"),
        ("scopes", "delete"),
        ("departments", "read"),
        ("departments", "create"),
        ("departments", "update"),
        ("departments", "delete"),
        ("records", "read"),
        ("records", "create"),
        ("records", "update"),
        ("records", "delete"),
        ("records", "admin"),
        ("edit_requests", "read"),
        ("edit_requests", "create"),
        ("edit_requests", "approve"),
        ("audit", "read"),
        ("audit", "export"),
        ("topiclens", "access"),
    ],
    
    # Manager role (Level 1) - can manage users, approve requests, view audit
    "Manager": [
        ("auth", "logout"),
        ("users", "read"),
        ("users", "create"),
        ("users", "update"),
        ("roles", "read"),
        ("departments", "read"),
        ("records", "read"),
        ("records", "create"),
        ("records", "update"),
        ("edit_requests", "read"),
        ("edit_requests", "create"),
        ("edit_requests", "approve"),
        ("audit", "read"),
    ],
    
    # Admin role (Level 2) - can create users, approve requests
    "Admin": [
        ("auth", "logout"),
        ("users", "read"),
        ("users", "create"),
        ("roles", "read"),
        ("departments", "read"),
        ("records", "read"),
        ("records", "create"),
        ("records", "update"),
        ("edit_requests", "read"),
        ("edit_requests", "create"),
        ("edit_requests", "approve"),
    ],
    
    # Worker role (Level 3+) - basic operations only
    "Worker": [
        ("auth", "logout"),
        ("users", "read"),  # Own profile only (enforced in endpoint logic)
        ("records", "read"),
        ("records", "create"),
        ("edit_requests", "read"),
        ("edit_requests", "create"),
    ],
}


async def assign_role_scopes():
    """Assign default scopes to roles"""
    
    # Create async engine and session
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        print("🌱 Starting role-scope assignments...")
        
        total_assigned = 0
        total_existing = 0
        total_errors = 0
        
        for role_name, scope_list in ROLE_SCOPE_ASSIGNMENTS.items():
            print(f"\n📋 Processing role: {role_name}")
            
            # Find the role
            result = await session.execute(
                select(Role).where(Role.name == role_name)
            )
            role = result.scalar_one_or_none()
            
            if not role:
                print(f"  ⚠️  Role not found: {role_name}")
                total_errors += 1
                continue
            
            for resource, action in scope_list:
                # Find the scope
                result = await session.execute(
                    select(Scope).where(
                        Scope.resource == resource,
                        Scope.action == action,
                        Scope.dept_context.is_(None)
                    )
                )
                scope = result.scalar_one_or_none()
                
                if not scope:
                    print(f"  ⚠️  Scope not found: {resource}:{action}")
                    total_errors += 1
                    continue
                
                # Check if assignment already exists
                result = await session.execute(
                    select(RoleScope).where(
                        RoleScope.role_id == role.id,
                        RoleScope.scope_id == scope.id
                    )
                )
                existing_assignment = result.scalar_one_or_none()
                
                if existing_assignment:
                    print(f"  ⏭️  Already assigned: {resource}:{action}")
                    total_existing += 1
                else:
                    # Create new role-scope assignment
                    new_assignment = RoleScope(
                        role_id=role.id,
                        scope_id=scope.id,
                        assigned_by=None  # System assignment
                    )
                    session.add(new_assignment)
                    print(f"  ✅ Assigned: {resource}:{action}")
                    total_assigned += 1
        
        # Commit all changes
        await session.commit()
        
        print(f"\n📊 Role-Scope Assignment Complete!")
        print(f"  ✅ Assigned: {total_assigned} scope assignments")
        print(f"  ⏭️  Existing: {total_existing} assignments")
        print(f"  ⚠️  Errors: {total_errors} (missing roles/scopes)")
    
    await engine.dispose()


async def main():
    """Main function"""
    print("=" * 60)
    print("🚀 Role-Scope Default Assignments")
    print("=" * 60)
    
    try:
        await assign_role_scopes()
        
        print("\n" + "=" * 60)
        print("✅ Assignment completed successfully!")
        print("=" * 60)
        print("\n💡 Note: Root role will bypass scope checks programmatically,")
        print("   but scopes are assigned for completeness and documentation.")
        
    except Exception as e:
        print(f"\n❌ Error during assignment: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
