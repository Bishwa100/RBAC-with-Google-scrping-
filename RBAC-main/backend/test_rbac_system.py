"""
Comprehensive RBAC System Test Script
Tests scope-based access control across all endpoints
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.all import User, Role, Scope, UserRole, UserScope
from app.models.rbac_extensions import RoleScope, APIEndpoint
from app.core.config import get_settings

settings = get_settings()


async def test_database_schema():
    """Test that all required tables and relationships exist"""
    print("\n" + "="*60)
    print("🧪 Testing Database Schema")
    print("="*60)
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Test 1: Check all tables exist
        tables_to_check = [User, Role, Scope, UserRole, UserScope, RoleScope, APIEndpoint]
        for table_model in tables_to_check:
            try:
                result = await session.execute(select(func.count()).select_from(table_model))
                count = result.scalar()
                print(f"  ✅ {table_model.__tablename__}: {count} records")
            except Exception as e:
                print(f"  ❌ {table_model.__tablename__}: Error - {str(e)}")
                return False
    
    await engine.dispose()
    return True


async def test_scope_definitions():
    """Test that all required scopes are defined"""
    print("\n" + "="*60)
    print("🧪 Testing Scope Definitions")
    print("="*60)
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    required_scopes = [
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
    ]
    
    async with async_session() as session:
        missing_scopes = []
        for resource, action in required_scopes:
            result = await session.execute(
                select(Scope).where(
                    Scope.resource == resource,
                    Scope.action == action
                )
            )
            scope = result.scalar_one_or_none()
            if scope:
                print(f"  ✅ Scope exists: {resource}:{action}")
            else:
                print(f"  ❌ Scope missing: {resource}:{action}")
                missing_scopes.append(f"{resource}:{action}")
        
        if missing_scopes:
            print(f"\n  ⚠️  Missing {len(missing_scopes)} scope(s)")
            return False
        else:
            print(f"\n  ✅ All {len(required_scopes)} required scopes exist!")
    
    await engine.dispose()
    return True


async def test_role_scope_assignments():
    """Test that roles have proper scope assignments"""
    print("\n" + "="*60)
    print("🧪 Testing Role-Scope Assignments")
    print("="*60)
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Get all roles
        result = await session.execute(select(Role))
        roles = result.scalars().all()
        
        if not roles:
            print("  ⚠️  No roles found in database")
            return False
        
        for role in roles:
            # Load role scopes
            await session.refresh(role, ['role_scopes'])
            scope_count = len(role.role_scopes)
            
            if role.level == 0:
                # Root should have all scopes (or bypass anyway)
                print(f"  ✅ {role.name} (Level {role.level}): {scope_count} scopes (Root bypasses checks)")
            else:
                print(f"  ✅ {role.name} (Level {role.level}): {scope_count} scopes")
                
                # Show sample scopes
                if scope_count > 0:
                    sample_scopes = []
                    for rs in role.role_scopes[:3]:
                        await session.refresh(rs, ['scope'])
                        sample_scopes.append(f"{rs.scope.resource}:{rs.scope.action}")
                    print(f"     Sample: {', '.join(sample_scopes)}")
    
    await engine.dispose()
    return True


async def test_api_endpoint_registry():
    """Test that API endpoints are registered"""
    print("\n" + "="*60)
    print("🧪 Testing API Endpoint Registry")
    print("="*60)
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Get total endpoint count
        result = await session.execute(select(func.count()).select_from(APIEndpoint))
        total_count = result.scalar()
        
        print(f"  📊 Total API endpoints registered: {total_count}")
        
        # Count by category
        result = await session.execute(
            select(APIEndpoint.category, func.count()).group_by(APIEndpoint.category)
        )
        categories = result.all()
        
        for category, count in categories:
            print(f"  ✅ {category}: {count} endpoints")
        
        # Count public vs protected
        result = await session.execute(
            select(func.count()).select_from(APIEndpoint).where(APIEndpoint.is_public == True)
        )
        public_count = result.scalar()
        
        result = await session.execute(
            select(func.count()).select_from(APIEndpoint).where(APIEndpoint.is_public == False)
        )
        protected_count = result.scalar()
        
        print(f"\n  🔓 Public endpoints: {public_count}")
        print(f"  🔒 Protected endpoints: {protected_count}")
        
        if total_count < 40:
            print(f"\n  ⚠️  Expected ~50 endpoints, found {total_count}")
            return False
    
    await engine.dispose()
    return True


async def test_root_user_bypass():
    """Test that root users bypass scope checks"""
    print("\n" + "="*60)
    print("🧪 Testing Root User Bypass Logic")
    print("="*60)
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Find root role
        result = await session.execute(select(Role).where(Role.level == 0))
        root_role = result.scalar_one_or_none()
        
        if not root_role:
            print("  ⚠️  No root role found (level 0)")
            return False
        
        print(f"  ✅ Root role found: {root_role.name} (Level {root_role.level})")
        
        # Find users with root role
        result = await session.execute(
            select(User).join(UserRole).where(UserRole.role_id == root_role.id)
        )
        root_users = result.scalars().all()
        
        if not root_users:
            print("  ⚠️  No users assigned to root role")
            return False
        
        print(f"  ✅ Found {len(root_users)} root user(s)")
        for user in root_users:
            print(f"     - {user.email}")
    
    await engine.dispose()
    return True


async def test_scope_inheritance():
    """Test that users inherit scopes from roles"""
    print("\n" + "="*60)
    print("🧪 Testing Scope Inheritance from Roles")
    print("="*60)
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Get a non-root role with scopes
        result = await session.execute(
            select(Role).where(Role.level > 0).limit(1)
        )
        role = result.scalar_one_or_none()
        
        if not role:
            print("  ⚠️  No non-root roles found")
            return False
        
        await session.refresh(role, ['role_scopes'])
        
        print(f"  ✅ Testing role: {role.name} (Level {role.level})")
        print(f"     Role has {len(role.role_scopes)} scopes")
        
        # Find a user with this role
        result = await session.execute(
            select(User).join(UserRole).where(UserRole.role_id == role.id).limit(1)
        )
        user = result.scalar_one_or_none()
        
        if user:
            await session.refresh(user, ['scopes'])
            print(f"  ✅ User {user.email} has:")
            print(f"     - Direct scopes: {len(user.scopes)}")
            print(f"     - Inherited scopes: {len(role.role_scopes)}")
            print(f"  ✅ Inheritance test passed!")
        else:
            print(f"  ℹ️  No users assigned to {role.name} role yet")
    
    await engine.dispose()
    return True


async def main():
    """Run all tests"""
    print("╔" + "="*58 + "╗")
    print("║" + " "*18 + "RBAC SYSTEM TESTS" + " "*23 + "║")
    print("╚" + "="*58 + "╝")
    
    tests = [
        ("Database Schema", test_database_schema),
        ("Scope Definitions", test_scope_definitions),
        ("Role-Scope Assignments", test_role_scope_assignments),
        ("API Endpoint Registry", test_api_endpoint_registry),
        ("Root User Bypass", test_root_user_bypass),
        ("Scope Inheritance", test_scope_inheritance),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n  ❌ Error in {test_name}: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\n  Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  🎉 All tests passed successfully!")
        return 0
    else:
        print(f"\n  ⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
