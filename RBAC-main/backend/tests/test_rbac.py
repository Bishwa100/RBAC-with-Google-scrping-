import pytest
from app.core.config import settings

@pytest.fixture
async def root_token(client):
    res = await client.post("/api/v1/auth/login", json={"email": settings.ROOT_EMAIL, "password": settings.ROOT_PASSWORD})
    return res.json()["data"]["access_token"]

@pytest.mark.asyncio
async def test_scope_enforcement_root(client, root_token):
    # Root can access everything, even without explicit scopes
    res = await client.get("/api/v1/records/", headers={"Authorization": f"Bearer {root_token}"})
    assert res.status_code == 200

@pytest.mark.asyncio
async def test_scope_enforcement_no_token(client):
    res = await client.get("/api/v1/records/")
    assert res.status_code == 401

@pytest.mark.asyncio
async def test_hierarchy_violation_returns_403(client, root_token):
    # Create a level 2 user
    dept_res = await client.post("/api/v1/departments/", headers={"Authorization": f"Bearer {root_token}"}, json={"name": "D1", "code": "D1"})
    dept_id = dept_res.json()["data"]["id"]
    
    role_res = await client.post("/api/v1/roles/", headers={"Authorization": f"Bearer {root_token}"}, json={"name": "admin", "level": 2, "dept_id": dept_id})
    role_id = role_res.json()["data"]["id"]
    
    user_res = await client.post("/api/v1/users/", headers={"Authorization": f"Bearer {root_token}"}, json={"email": "admin@d1.com", "password": "pass", "dept_id": dept_id, "role_id": role_id})
    user_id = user_res.json()["data"]["id"]
    
    login_res = await client.post("/api/v1/auth/login", json={"email": "admin@d1.com", "password": "pass"})
    admin_token = login_res.json()["data"]["access_token"]
    
    # Try to create a department as admin (requires level 0)
    res = await client.post("/api/v1/departments/", headers={"Authorization": f"Bearer {admin_token}"}, json={"name": "D2", "code": "D2"})
    assert res.status_code == 403
    assert res.json()["error"] == "hierarchy_violation"