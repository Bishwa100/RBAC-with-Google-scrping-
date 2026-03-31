"""
Comprehensive Scope Seeding Script
Seeds all scopes for the RBAC system covering all API endpoints
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.all import Scope
from app.core.config import get_settings

settings = get_settings()

# Comprehensive scope definitions
# Format: (resource, action, description)
SCOPE_DEFINITIONS = [
    # Authentication scopes
    ("auth", "logout", "Logout from the system"),
    ("auth", "bootstrap", "Bootstrap root user (system setup)"),
    
    # User management scopes
    ("users", "read", "View user information and list users"),
    ("users", "create", "Create new users"),
    ("users", "update", "Update user information"),
    ("users", "delete", "Delete users"),
    ("users", "admin", "Advanced user operations (extract, analyze documents)"),
    
    # Role management scopes
    ("roles", "read", "View roles and role information"),
    ("roles", "create", "Create new roles"),
    ("roles", "update", "Update role information and assign scopes to roles"),
    ("roles", "delete", "Delete roles"),
    
    # Scope management scopes
    ("scopes", "read", "View scopes and API endpoint registry"),
    ("scopes", "create", "Create new scopes"),
    ("scopes", "update", "Update scope information"),
    ("scopes", "delete", "Delete scopes"),
    
    # Department management scopes
    ("departments", "read", "View department information"),
    ("departments", "create", "Create new departments"),
    ("departments", "update", "Update department information"),
    ("departments", "delete", "Delete departments"),
    
    # Record management scopes
    ("records", "read", "View data records"),
    ("records", "create", "Submit new data records"),
    ("records", "update", "Update data records"),
    ("records", "delete", "Delete data records"),
    ("records", "admin", "Administrative record operations (freeze/unfreeze)"),
    
    # Edit request scopes
    ("edit_requests", "read", "View edit requests"),
    ("edit_requests", "create", "Create edit requests"),
    ("edit_requests", "approve", "Approve or reject edit requests"),
    
    # Audit log scopes
    ("audit", "read", "View audit logs"),
    ("audit", "export", "Export audit logs"),
    
    # TopicLens scopes
    ("topiclens", "access", "Access TopicLens features (search, analyze, jobs)"),
]


async def seed_scopes():
    """Seed all scope definitions into the database"""
    
    # Create async engine and session
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        print("🌱 Starting scope seeding...")
        
        created_count = 0
        existing_count = 0
        
        for resource, action, description in SCOPE_DEFINITIONS:
            # Check if scope already exists
            result = await session.execute(
                select(Scope).where(
                    Scope.resource == resource,
                    Scope.action == action,
                    Scope.dept_context.is_(None)  # Global scopes only
                )
            )
            existing_scope = result.scalar_one_or_none()
            
            if existing_scope:
                print(f"  ⏭️  Scope already exists: {resource}:{action}")
                existing_count += 1
            else:
                # Create new scope
                new_scope = Scope(
                    resource=resource,
                    action=action,
                    description=description,
                    dept_context=None  # Global scope
                )
                session.add(new_scope)
                print(f"  ✅ Created scope: {resource}:{action}")
                created_count += 1
        
        # Commit all changes
        await session.commit()
        
        print(f"\n📊 Scope Seeding Complete!")
        print(f"  ✅ Created: {created_count} scopes")
        print(f"  ⏭️  Existing: {existing_count} scopes")
        print(f"  📝 Total: {len(SCOPE_DEFINITIONS)} scopes defined")
    
    await engine.dispose()


async def seed_api_endpoints():
    """Seed API endpoint registry"""
    from app.models.rbac_extensions import APIEndpoint
    
    # Create async engine and session
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    # API Endpoint definitions
    # Format: (path, method, resource, action, description, category, is_public)
    ENDPOINT_DEFINITIONS = [
        # Authentication endpoints
        ("/api/v1/auth/login", "POST", None, None, "User login", "auth", True),
        ("/api/v1/auth/refresh", "POST", None, None, "Refresh access token", "auth", True),
        ("/api/v1/auth/logout", "POST", "auth", "logout", "User logout", "auth", False),
        ("/api/v1/auth/register", "POST", "auth", "bootstrap", "Bootstrap root user", "auth", True),
        
        # User management endpoints
        ("/api/v1/users", "GET", "users", "read", "List users", "users", False),
        ("/api/v1/users", "POST", "users", "create", "Create user", "users", False),
        ("/api/v1/users/{id}", "GET", "users", "read", "Get user details", "users", False),
        ("/api/v1/users/{id}", "PATCH", "users", "update", "Update user", "users", False),
        ("/api/v1/users/{id}", "DELETE", "users", "delete", "Delete user", "users", False),
        ("/api/v1/users/stats/{id}", "GET", "users", "read", "Get user statistics", "users", False),
        ("/api/v1/users/extract", "POST", "users", "admin", "Extract user from document", "users", False),
        ("/api/v1/users/analyze", "POST", "users", "admin", "Analyze user document", "users", False),
        
        # Role management endpoints
        ("/api/v1/roles", "GET", "roles", "read", "List roles", "roles", False),
        ("/api/v1/roles", "POST", "roles", "create", "Create role", "roles", False),
        ("/api/v1/roles/{id}", "GET", "roles", "read", "Get role details", "roles", False),
        ("/api/v1/roles/{id}", "PATCH", "roles", "update", "Update role", "roles", False),
        ("/api/v1/roles/{id}", "DELETE", "roles", "delete", "Delete role", "roles", False),
        ("/api/v1/roles/{id}/scopes", "GET", "roles", "read", "Get role scopes", "roles", False),
        ("/api/v1/roles/{id}/scopes", "POST", "roles", "update", "Assign scopes to role", "roles", False),
        ("/api/v1/roles/{id}/scopes/{scope_id}", "DELETE", "roles", "update", "Remove scope from role", "roles", False),
        
        # Scope management endpoints
        ("/api/v1/scopes", "GET", "scopes", "read", "List scopes", "scopes", False),
        ("/api/v1/scopes", "POST", "scopes", "create", "Create scope", "scopes", False),
        ("/api/v1/scopes/{id}", "PATCH", "scopes", "update", "Update scope", "scopes", False),
        ("/api/v1/scopes/{id}", "DELETE", "scopes", "delete", "Delete scope", "scopes", False),
        ("/api/v1/scopes/api-endpoints", "GET", "scopes", "read", "List API endpoint registry", "scopes", False),
        
        # Department management endpoints
        ("/api/v1/departments", "GET", "departments", "read", "List departments", "departments", False),
        ("/api/v1/departments", "POST", "departments", "create", "Create department", "departments", False),
        ("/api/v1/departments/{id}", "GET", "departments", "read", "Get department details", "departments", False),
        ("/api/v1/departments/{id}", "PATCH", "departments", "update", "Update department", "departments", False),
        ("/api/v1/departments/{id}", "DELETE", "departments", "delete", "Delete department", "departments", False),
        
        # Record management endpoints
        ("/api/v1/records", "GET", "records", "read", "List records", "records", False),
        ("/api/v1/records", "POST", "records", "create", "Create record", "records", False),
        ("/api/v1/records/{id}", "GET", "records", "read", "Get record details", "records", False),
        ("/api/v1/records/{id}", "PATCH", "records", "update", "Update record", "records", False),
        ("/api/v1/records/{id}", "DELETE", "records", "delete", "Delete record", "records", False),
        ("/api/v1/records/{id}/freeze", "POST", "records", "admin", "Freeze record", "records", False),
        ("/api/v1/records/{id}/unfreeze", "POST", "records", "admin", "Unfreeze record", "records", False),
        
        # Edit request endpoints
        ("/api/v1/edit-requests", "GET", "edit_requests", "read", "List edit requests", "edit_requests", False),
        ("/api/v1/edit-requests", "POST", "edit_requests", "create", "Create edit request", "edit_requests", False),
        ("/api/v1/edit-requests/{id}", "GET", "edit_requests", "read", "Get edit request details", "edit_requests", False),
        ("/api/v1/edit-requests/{id}/approve", "POST", "edit_requests", "approve", "Approve edit request", "edit_requests", False),
        ("/api/v1/edit-requests/{id}/reject", "POST", "edit_requests", "approve", "Reject edit request", "edit_requests", False),
        
        # Audit log endpoints
        ("/api/v1/audit", "GET", "audit", "read", "List audit logs", "audit", False),
        ("/api/v1/audit/export", "POST", "audit", "export", "Export audit logs", "audit", False),
        
        # TopicLens endpoints
        ("/api/v1/topiclens/search", "POST", "topiclens", "access", "Start topic search", "topiclens", False),
        ("/api/v1/topiclens/jobs", "GET", "topiclens", "access", "List TopicLens jobs", "topiclens", False),
        ("/api/v1/topiclens/jobs/{id}", "GET", "topiclens", "access", "Get job details", "topiclens", False),
        ("/api/v1/topiclens/analyze", "POST", "topiclens", "access", "Analyze content", "topiclens", False),
        ("/api/v1/topiclens/sources", "GET", "topiclens", "access", "List available sources", "topiclens", False),
    ]
    
    async with async_session() as session:
        print("\n🌱 Starting API endpoint registry seeding...")
        
        created_count = 0
        existing_count = 0
        
        for path, method, resource, action, description, category, is_public in ENDPOINT_DEFINITIONS:
            # Check if endpoint already exists
            result = await session.execute(
                select(APIEndpoint).where(
                    APIEndpoint.path == path,
                    APIEndpoint.method == method
                )
            )
            existing_endpoint = result.scalar_one_or_none()
            
            if existing_endpoint:
                print(f"  ⏭️  Endpoint exists: {method} {path}")
                existing_count += 1
            else:
                # Create new endpoint
                new_endpoint = APIEndpoint(
                    path=path,
                    method=method,
                    required_resource=resource,
                    required_action=action,
                    description=description,
                    category=category,
                    is_public=is_public,
                    is_active=True
                )
                session.add(new_endpoint)
                scope_info = f" [{resource}:{action}]" if resource and action else " [public]"
                print(f"  ✅ Created: {method} {path}{scope_info}")
                created_count += 1
        
        # Commit all changes
        await session.commit()
        
        print(f"\n📊 API Endpoint Seeding Complete!")
        print(f"  ✅ Created: {created_count} endpoints")
        print(f"  ⏭️  Existing: {existing_count} endpoints")
        print(f"  📝 Total: {len(ENDPOINT_DEFINITIONS)} endpoints defined")
    
    await engine.dispose()


async def main():
    """Main function to run all seeding"""
    print("=" * 60)
    print("🚀 Comprehensive RBAC Scope Seeding")
    print("=" * 60)
    
    try:
        # Seed scopes
        await seed_scopes()
        
        # Seed API endpoints
        await seed_api_endpoints()
        
        print("\n" + "=" * 60)
        print("✅ All seeding completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
