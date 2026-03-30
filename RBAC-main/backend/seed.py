import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.future import select
from app.core.config import settings
from app.models.all import Department, Role, Scope, User, UserRole, UserScope
from app.core.security import get_password_hash

async def seed():
    engine = create_async_engine(settings.DATABASE_URL)
    session_factory = async_sessionmaker(engine)
    
    async with session_factory() as session:
        # Check if already seeded
        res = await session.execute(Department.__table__.select())
        if res.fetchone():
            print("Already seeded.")
            return

        # Scopes
        scopes_data = [
            ("records", "create"), ("records", "read"), ("records", "update"), ("records", "delete"),
            ("users", "create"), ("users", "read"), ("users", "update"), ("users", "delete"),
            ("reports", "export"), ("edit_requests", "create"), ("edit_requests", "approve")
        ]
        db_scopes = {}
        for res_name, action in scopes_data:
            s = Scope(resource=res_name, action=action)
            session.add(s)
            db_scopes[f"{res_name}:{action}"] = s
            
        await session.flush()
        
        # Get Root User (created by bootstrap)
        res = await session.execute(select(User).where(User.email == settings.ROOT_EMAIL))
        root_user = res.scalar_one()
        root_user_id = root_user.id
        
        # Grant all scopes to root
        for s in db_scopes.values():
            session.add(UserScope(user_id=root_user_id, scope_id=s.id, granted_by=root_user_id))
            
        await session.flush()

        # Departments
        depts = [
            Department(name="GOV", code="GOV", created_by=root_user_id),
            Department(name="Training", code="TRN", created_by=root_user_id),
            Department(name="Finance", code="FIN", created_by=root_user_id)
        ]
        session.add_all(depts)
        await session.flush()

        gov, trn, fin = depts

        # Roles
        roles_data = [
            # GOV
            (gov.id, "gov_manager", 1),
            (gov.id, "gov_admin", 2),
            (gov.id, "gov_supervisor", 3),
            (gov.id, "gov_worker", 4),
            (gov.id, "gov_data_importer", 4),
            (gov.id, "gov_employee", 4),
            # TRN
            (trn.id, "training_manager", 1),
            (trn.id, "training_admin", 2),
            (trn.id, "training_trainer", 4),
            (trn.id, "training_trainee", 4),
            # FIN
            (fin.id, "finance_manager", 1),
            (fin.id, "finance_admin", 2),
            (fin.id, "finance_data_entry", 4),
        ]
        
        db_roles = {}
        for d_id, r_name, lvl in roles_data:
            r = Role(name=r_name, level=lvl, dept_id=d_id)
            session.add(r)
            db_roles[r_name] = r
            
        await session.flush()
        
        # Users
        for r_name, r_obj in db_roles.items():
            u = User(
                email=f"{r_name}@test.local",
                hashed_password=get_password_hash("Pass123!"),
                full_name=r_name.replace("_", " ").title(),
                dept_id=r_obj.dept_id,
                created_by=root_user_id
            )
            session.add(u)
            await session.flush()
            session.add(UserRole(user_id=u.id, role_id=r_obj.id, assigned_by=root_user_id))
            
            # Grant some scopes
            if r_obj.level <= 2:
                for s in db_scopes.values():
                    if s.action in ["read", "approve", "update", "create"]:
                        session.add(UserScope(user_id=u.id, scope_id=s.id, granted_by=root_user_id))
            else:
                session.add(UserScope(user_id=u.id, scope_id=db_scopes["records:read"].id, granted_by=root_user_id))
                session.add(UserScope(user_id=u.id, scope_id=db_scopes["records:create"].id, granted_by=root_user_id))
                session.add(UserScope(user_id=u.id, scope_id=db_scopes["records:update"].id, granted_by=root_user_id))
                session.add(UserScope(user_id=u.id, scope_id=db_scopes["edit_requests:create"].id, granted_by=root_user_id))

        await session.flush()

        # Additional Mock Users
        mock_users = [
            ("Alice Smith", "alice.smith@test.local", fin.id, "finance_manager"),
            ("Bob Jones", "bob.jones@test.local", fin.id, "finance_admin"),
            ("Charlie Brown", "charlie.b@test.local", fin.id, "finance_data_entry"),
            ("Diana Prince", "diana.p@test.local", trn.id, "training_manager"),
            ("Evan Wright", "evan.w@test.local", trn.id, "training_trainer"),
            ("Fiona Gallagher", "fiona.g@test.local", trn.id, "training_trainee"),
            ("George Costanza", "george.c@test.local", gov.id, "gov_supervisor"),
            ("Hannah Abbott", "hannah.a@test.local", gov.id, "gov_employee"),
        ]
        
        roles_by_name = {r.name: r for r in db_roles.values()}
        
        for name, email, dept_id, role_name in mock_users:
            u = User(
                email=email,
                hashed_password=get_password_hash("Pass123!"),
                full_name=name,
                dept_id=dept_id,
                created_by=root_user_id
            )
            session.add(u)
            await session.flush()
            
            r_obj = roles_by_name[role_name]
            session.add(UserRole(user_id=u.id, role_id=r_obj.id, assigned_by=root_user_id))
            
            if r_obj.level <= 2:
                for s in db_scopes.values():
                    if s.action in ["read", "approve", "update", "create"]:
                        session.add(UserScope(user_id=u.id, scope_id=s.id, granted_by=root_user_id))
            else:
                session.add(UserScope(user_id=u.id, scope_id=db_scopes["records:read"].id, granted_by=root_user_id))
                session.add(UserScope(user_id=u.id, scope_id=db_scopes["records:create"].id, granted_by=root_user_id))
                session.add(UserScope(user_id=u.id, scope_id=db_scopes["records:update"].id, granted_by=root_user_id))
                session.add(UserScope(user_id=u.id, scope_id=db_scopes["edit_requests:create"].id, granted_by=root_user_id))

        await session.commit()
        print("Seeding complete.")

if __name__ == "__main__":
    asyncio.run(seed())