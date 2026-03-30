import pytest
from app.core.config import settings

@pytest.mark.asyncio
async def test_admin_cannot_manage_manager(client):
    root_login = await client.post("/api/v1/auth/login", json={"email": settings.ROOT_EMAIL, "password": settings.ROOT_PASSWORD})
    root_token = root_login.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {root_token}"}
    
    d = await client.post("/api/v1/departments/", headers=headers, json={"name": "HR", "code": "HR"})
    dept_id = d.json()["data"]["id"]
    
    manager = await client.post("/api/v1/roles/", headers=headers, json={"name": "hrmanager", "level": 1, "dept_id": dept_id})
    admin = await client.post("/api/v1/roles/", headers=headers, json={"name": "hradmin", "level": 2, "dept_id": dept_id})
    
    m_res = await client.post("/api/v1/users/", headers=headers, json={"email": "m@hr.com", "password": "pass", "dept_id": dept_id, "role_id": manager.json()["data"]["id"]})
    m_id = m_res.json()["data"]["id"]
    
    a_res = await client.post("/api/v1/users/", headers=headers, json={"email": "a@hr.com", "password": "pass", "dept_id": dept_id, "role_id": admin.json()["data"]["id"]})
    a_id = a_res.json()["data"]["id"]
    
    admin_login = await client.post("/api/v1/auth/login", json={"email": "a@hr.com", "password": "pass"})
    admin_token = admin_login.json()["data"]["access_token"]
    
    # admin tries to delete manager
    delete_res = await client.delete(f"/api/v1/users/{m_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert delete_res.status_code == 403
    assert delete_res.json()["error"] == "hierarchy_violation"