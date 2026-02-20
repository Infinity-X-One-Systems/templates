"""Tests for authentication endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_register_and_login():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register
        reg = await client.post("/auth/register", json={"email": "test@example.com", "password": "Secret123!", "name": "Test"})
        assert reg.status_code == 201
        assert reg.json()["email"] == "test@example.com"

        # Login
        login = await client.post("/auth/login", json={"email": "test@example.com", "password": "Secret123!"})
        assert login.status_code == 200
        tokens = login.json()
        assert "access_token" in tokens

        # Me
        me = await client.get("/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
        assert me.status_code == 200
        assert me.json()["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_login_invalid_credentials():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/auth/login", json={"email": "nobody@example.com", "password": "wrong"})
    assert resp.status_code == 401
