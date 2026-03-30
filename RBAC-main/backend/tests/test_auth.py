import pytest
from app.core.config import settings

@pytest.mark.asyncio
async def test_login_success(client):
    res = await client.post("/api/v1/auth/login", json={"email": settings.ROOT_EMAIL, "password": settings.ROOT_PASSWORD})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]

@pytest.mark.asyncio
async def test_login_invalid(client):
    res = await client.post("/api/v1/auth/login", json={"email": settings.ROOT_EMAIL, "password": "wrong"})
    assert res.status_code == 401
    assert res.json()["success"] is False

@pytest.mark.asyncio
async def test_refresh_token(client):
    res = await client.post("/api/v1/auth/login", json={"email": settings.ROOT_EMAIL, "password": settings.ROOT_PASSWORD})
    refresh = res.json()["data"]["refresh_token"]
    
    res2 = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert res2.status_code == 200
    assert "access_token" in res2.json()["data"]

@pytest.mark.asyncio
async def test_logout(client):
    res = await client.post("/api/v1/auth/login", json={"email": settings.ROOT_EMAIL, "password": settings.ROOT_PASSWORD})
    refresh = res.json()["data"]["refresh_token"]
    
    await client.post("/api/v1/auth/logout", json={"refresh_token": refresh})
    res2 = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert res2.status_code == 401
    assert res2.json()["error"] == "invalid_token"