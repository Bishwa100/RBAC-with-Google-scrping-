from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text
from app.models.all import User, Role
from app.core.security import get_password_hash
from app.core.config import settings
from app.db.base import Base
import logging

logger = logging.getLogger(__name__)

async def init_db(db: AsyncSession):
    # Ensure tables are created
    logger.info("Ensuring tables exist.")
    async with db.bind.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Check if 'details' column exists in 'users' table and add it if not
    # This is a manual migration as Alembic is not being used to manage these changes.
    await db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS details JSONB"))
    await db.commit()
    
    result = await db.execute(select(User).limit(1))
    first_user = result.scalar_one_or_none()
    
    if not first_user:
        logger.info("No users found. Bootstrapping root user.")
        # Create root role
        root_role = Role(name="root", level=0, description="Root Superuser")
        db.add(root_role)
        await db.commit()
        await db.refresh(root_role)
        
        # Create root user
        root_user = User(
            email=settings.ROOT_EMAIL,
            hashed_password=get_password_hash(settings.ROOT_PASSWORD),
            full_name="Root Admin",
            is_active=True
        )
        db.add(root_user)
        await db.commit()
        await db.refresh(root_user)
        
        # Assign role
        from app.models.all import UserRole
        ur = UserRole(user_id=root_user.id, role_id=root_role.id, assigned_by=root_user.id)
        db.add(ur)
        await db.commit()
        logger.info("Root user created successfully.")