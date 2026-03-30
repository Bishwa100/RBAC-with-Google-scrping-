import pytest
from app.core.config import settings

@pytest.fixture
async def setup_users(client):
    root_login = await client.post("/api/v1/auth/login", json={"email": settings.ROOT_EMAIL, "password": settings.ROOT_PASSWORD})
    root_token = root_login.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {root_token}"}
    
    # scopes
    s1 = await client.post("/api/v1/scopes/", headers=headers, json={"resource": "records", "action": "create"})
    s2 = await client.post("/api/v1/scopes/", headers=headers, json={"resource": "records", "action": "update"})
    s3 = await client.post("/api/v1/scopes/", headers=headers, json={"resource": "edit_requests", "action": "create"})
    s4 = await client.post("/api/v1/scopes/", headers=headers, json={"resource": "edit_requests", "action": "approve"})

    # dept
    d = await client.post("/api/v1/departments/", headers=headers, json={"name": "Ops", "code": "OPS"})
    dept_id = d.json()["data"]["id"]
    
    # roles
    manager = await client.post("/api/v1/roles/", headers=headers, json={"name": "manager", "level": 1, "dept_id": dept_id})
    admin = await client.post("/api/v1/roles/", headers=headers, json={"name": "admin", "level": 2, "dept_id": dept_id})
    worker = await client.post("/api/v1/roles/", headers=headers, json={"name": "worker", "level": 4, "dept_id": dept_id})
    
    # users
    w_res = await client.post("/api/v1/users/", headers=headers, json={"email": "worker@o.com", "password": "pass", "dept_id": dept_id, "role_id": worker.json()["data"]["id"]})
    w_id = w_res.json()["data"]["id"]
    await client.post(f"/api/v1/users/{w_id}/scopes", headers=headers, params={"scope_id": s1.json()["data"]["id"]})
    await client.post(f"/api/v1/users/{w_id}/scopes", headers=headers, params={"scope_id": s2.json()["data"]["id"]})
    await client.post(f"/api/v1/users/{w_id}/scopes", headers=headers, params={"scope_id": s3.json()["data"]["id"]})

    a_res = await client.post("/api/v1/users/", headers=headers, json={"email": "admin@o.com", "password": "pass", "dept_id": dept_id, "role_id": admin.json()["data"]["id"]})
    a_id = a_res.json()["data"]["id"]
    await client.post(f"/api/v1/users/{a_id}/scopes", headers=headers, params={"scope_id": s4.json()["data"]["id"]})

    m_res = await client.post("/api/v1/users/", headers=headers, json={"email": "manager@o.com", "password": "pass", "dept_id": dept_id, "role_id": manager.json()["data"]["id"]})
    m_id = m_res.json()["data"]["id"]
    await client.post(f"/api/v1/users/{m_id}/scopes", headers=headers, params={"scope_id": s4.json()["data"]["id"]})

    return {
        "worker": (await client.post("/api/v1/auth/login", json={"email": "worker@o.com", "password": "pass"})).json()["data"]["access_token"],
        "admin": (await client.post("/api/v1/auth/login", json={"email": "admin@o.com", "password": "pass"})).json()["data"]["access_token"],
        "manager": (await client.post("/api/v1/auth/login", json={"email": "manager@o.com", "password": "pass"})).json()["data"]["access_token"]
    }

@pytest.mark.asyncio
async def test_freeze_workflow(client, setup_users):
    w_token = setup_users["worker"]
    a_token = setup_users["admin"]
    m_token = setup_users["manager"]
    
    # 1. Submit record -> frozen
    rec = await client.post("/api/v1/records/", headers={"Authorization": f"Bearer {w_token}"}, json={"record_type": "log", "payload": {"foo": "bar"}})
    assert rec.status_code == 201
    rec_id = rec.json()["data"]["id"]
    assert rec.json()["data"]["is_frozen"] is True
    
    # 2. Edit blocked
    edit_attempt = await client.patch(f"/api/v1/records/{rec_id}", headers={"Authorization": f"Bearer {w_token}"}, json={"payload": {"foo": "baz"}})
    assert edit_attempt.status_code == 403
    
    # 3. Create edit request
    req = await client.post("/api/v1/edit-requests/", headers={"Authorization": f"Bearer {w_token}"}, json={"record_id": rec_id, "reason": "typo"})
    assert req.status_code == 201
    req_id = req.json()["data"]["id"]
    
    # 4. Admin approves
    a_app = await client.post(f"/api/v1/edit-requests/{req_id}/approve", headers={"Authorization": f"Bearer {a_token}"}, json={"decision": "approved", "comment": "ok"})
    assert a_app.status_code == 200
    assert a_app.json()["data"]["status"] == "pending" # needs 1 more
    
    # 5. Manager approves
    m_app = await client.post(f"/api/v1/edit-requests/{req_id}/approve", headers={"Authorization": f"Bearer {m_token}"}, json={"decision": "approved", "comment": "ok"})
    assert m_app.status_code == 200
    assert m_app.json()["data"]["status"] == "approved"
    
    # 6. Edit succeeds
    edit_success = await client.patch(f"/api/v1/records/{rec_id}", headers={"Authorization": f"Bearer {w_token}"}, json={"payload": {"foo": "baz"}})
    assert edit_success.status_code == 200
    assert edit_success.json()["data"]["payload"]["foo"] == "baz"