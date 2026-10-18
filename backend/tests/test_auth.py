"""User settings, profile, and historical results auth tests."""

from typing import Dict
import pytest
import httpx


@pytest.mark.asyncio
async def test_user_profile_requires_auth(async_client: httpx.AsyncClient):
    """GET /api/v1/user/profile returns 401 when Authorization header is omitted."""
    res = await async_client.get("/api/v1/user/profile")
    assert res.status_code == 401
    data = res.json()
    assert data["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_get_user_profile_with_auth(
    async_client: httpx.AsyncClient,
    auth_headers: Dict[str, str],
):
    """GET /api/v1/user/profile succeeds with valid Bearer token."""
    res = await async_client.get("/api/v1/user/profile", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "id" in data
    assert "email" in data
    assert data["native_language"] == "ru"
    assert data["target_language"] == "en"
    assert data["preferred_style"] == "conversational"


@pytest.mark.asyncio
async def test_update_user_profile(
    async_client: httpx.AsyncClient,
    auth_headers: Dict[str, str],
):
    """PUT /api/v1/user/profile updates user preferred style and settings."""
    update_payload = {
        "preferred_style": "academic",
        "allow_loose_phrasing": False,
        "input_mode": "scaffolding",
    }
    res = await async_client.put(
        "/api/v1/user/profile",
        json=update_payload,
        headers=auth_headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["preferred_style"] == "academic"
    assert data["allow_loose_phrasing"] is False
    assert data["input_mode"] == "scaffolding"


@pytest.mark.asyncio
async def test_get_results_history(
    async_client: httpx.AsyncClient,
    auth_headers: Dict[str, str],
):
    """GET /api/v1/results returns paginated history list."""
    res = await async_client.get("/api/v1/results?limit=10&offset=0", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "results" in data
    assert "total" in data
    assert data["limit"] == 10
    assert data["offset"] == 0
