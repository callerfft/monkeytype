"""Edge case tests for streaming and synchronous evaluation."""

import json
import pytest
import httpx
from app.models.grammar import PreferredStyle


@pytest.mark.asyncio
async def test_evaluate_empty_submission_timeout(async_client: httpx.AsyncClient):
    """Test evaluation when user runs out of time without typing text."""
    sess_res = await async_client.post(
        "/api/v1/sessions",
        json={
            "mode": "translation",
            "source_language": "ru",
            "target_language": "en",
            "timer_seconds": 15,
            "target_word_count": 10,
            "margin_buffer": 5,
        },
    )
    assert sess_res.status_code == 201
    session_id = sess_res.json()["session_id"]

    eval_payload = {
        "user_text": "",
        "time_spent_ms": 15100,
        "words_typed": 0,
        "character_count": 0,
    }

    res = await async_client.post(
        f"/api/v1/sessions/{session_id}/evaluate/sync",
        json=eval_payload,
    )
    assert res.status_code == 200
    data = res.json()

    assert data["user_text"] == ""
    assert data["metrics"]["word_count"] == 0
    assert data["metrics"]["wpm"] == 0.0
    assert data["metrics"]["accuracy_score"] == 0.0
    assert data["metrics"]["target_met"] is False
    assert data["metrics"]["timer_expired"] is True
    assert data["semantic_validation"]["is_valid"] is False


@pytest.mark.asyncio
async def test_evaluate_word_limit_exceeded(async_client: httpx.AsyncClient):
    """Test that submitting more words than target + buffer flags word_limit_exceeded."""
    sess_res = await async_client.post(
        "/api/v1/sessions",
        json={
            "mode": "translation",
            "source_language": "ru",
            "target_language": "en",
            "target_word_count": 5,
            "margin_buffer": 2,  # max allowed is 7 words
        },
    )
    assert sess_res.status_code == 201
    session_id = sess_res.json()["session_id"]

    long_text = "one two three four five six seven eight nine ten"
    res = await async_client.post(
        f"/api/v1/sessions/{session_id}/evaluate/sync",
        json={
            "user_text": long_text,
            "time_spent_ms": 5000,
            "words_typed": 10,
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["metrics"]["word_count"] == 10
    assert data["metrics"]["word_limit_exceeded"] is True
    assert data["metrics"]["target_met"] is False


@pytest.mark.asyncio
async def test_all_stylistic_registers(async_client: httpx.AsyncClient):
    """Verify that each preferred style register generates corresponding alternative."""
    styles = [
        PreferredStyle.CONVERSATIONAL,
        PreferredStyle.FORMAL,
        PreferredStyle.CONCISE,
        PreferredStyle.ACADEMIC,
        PreferredStyle.BUSINESS,
    ]

    for style in styles:
        sess_res = await async_client.post(
            "/api/v1/sessions",
            json={
                "mode": "translation",
                "source_language": "ru",
                "target_language": "en",
                "preferred_style": style.value,
            },
        )
        assert sess_res.status_code == 201
        session_id = sess_res.json()["session_id"]

        eval_res = await async_client.post(
            f"/api/v1/sessions/{session_id}/evaluate/sync",
            json={
                "user_text": "I drink coffee in morning.",
                "time_spent_ms": 6000,
                "words_typed": 5,
            },
        )
        assert eval_res.status_code == 200
        alt = eval_res.json()["style_alternative"]
        assert alt["style"] == style.value
        assert len(alt["text"]) > 0
        assert len(alt["explanation"]) > 0
