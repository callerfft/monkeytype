"""Session creation, constraints, and lifecycle tests."""

import uuid
import pytest
import httpx


@pytest.mark.asyncio
async def test_create_mode_a_session_success(async_client: httpx.AsyncClient):
    """Test creating a Mode A translation session with default parameters."""
    payload = {
        "mode": "translation",
        "source_language": "ru",
        "target_language": "en",
        "timer_seconds": 30,
        "target_word_count": 10,
        "margin_buffer": 5,
        "difficulty": "medium",
        "preferred_style": "conversational",
    }
    response = await async_client.post("/api/v1/sessions", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert "session_id" in data
    assert data["status"] == "active"
    assert data["mode"] == "translation"
    assert data["timer_seconds"] == 30
    assert data["prompt"]["type"] == "translation"
    assert data["prompt"]["target_word_count"] == 10
    assert data["prompt"]["max_word_count"] == 15
    assert len(data["prompt"]["content"]) > 0


@pytest.mark.asyncio
async def test_create_mode_b_session_success(async_client: httpx.AsyncClient):
    """Test creating a Mode B situation/image session."""
    payload = {
        "mode": "situation_image",
        "source_language": "en",
        "target_language": "en",
        "timer_seconds": 60,
        "target_word_count": 15,
        "margin_buffer": 5,
        "difficulty": "easy",
    }
    response = await async_client.post("/api/v1/sessions", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert data["mode"] == "situation_image"
    assert data["timer_seconds"] == 60
    assert data["prompt"]["type"] == "situation_image"
    assert data["prompt"]["target_word_count"] == 15
    assert data["prompt"]["max_word_count"] == 20


@pytest.mark.asyncio
async def test_session_timer_variants(async_client: httpx.AsyncClient):
    """Test all allowable timer values: 15s, 30s, 60s, and null (untimed)."""
    for timer_val in [15, 30, 60, None]:
        payload = {
            "mode": "translation",
            "source_language": "ru",
            "target_language": "en",
            "timer_seconds": timer_val,
        }
        res = await async_client.post("/api/v1/sessions", json=payload)
        assert res.status_code == 201
        data = res.json()
        assert data["timer_seconds"] == timer_val


@pytest.mark.asyncio
async def test_session_invalid_timer_rejected(async_client: httpx.AsyncClient):
    """Reject timers outside the 15, 30, 60, null contract specification."""
    payload = {
        "mode": "translation",
        "source_language": "ru",
        "target_language": "en",
        "timer_seconds": 45,  # Invalid
    }
    res = await async_client.post("/api/v1/sessions", json=payload)
    assert res.status_code == 400
    data = res.json()
    assert data["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_get_session_by_id(async_client: httpx.AsyncClient):
    """Fetch created session and verify matching state."""
    create_res = await async_client.post(
        "/api/v1/sessions",
        json={"mode": "translation", "source_language": "ru", "target_language": "en"},
    )
    assert create_res.status_code == 201
    created = create_res.json()
    session_id = created["session_id"]

    get_res = await async_client.get(f"/api/v1/sessions/{session_id}")
    assert get_res.status_code == 200
    fetched = get_res.json()
    assert fetched["session_id"] == session_id
    assert fetched["prompt"]["content"] == created["prompt"]["content"]


@pytest.mark.asyncio
async def test_get_session_not_found(async_client: httpx.AsyncClient):
    """Return 404 with standardized ErrorResponse for non-existent session UUID."""
    random_id = str(uuid.uuid4())
    res = await async_client.get(f"/api/v1/sessions/{random_id}")
    assert res.status_code == 404
    data = res.json()
    assert data["code"] == "SESSION_NOT_FOUND"
    assert "not found" in data["message"].lower()
