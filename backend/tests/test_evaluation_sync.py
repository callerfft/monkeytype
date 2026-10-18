"""Synchronous evaluation endpoint tests."""

import pytest
import httpx


@pytest.mark.asyncio
async def test_evaluate_sync_success(async_client: httpx.AsyncClient):
    """Test synchronous fallback evaluation returning complete EvaluationResult JSON."""
    sess_res = await async_client.post(
        "/api/v1/sessions",
        json={
            "mode": "translation",
            "source_language": "ru",
            "target_language": "en",
            "timer_seconds": 30,
            "target_word_count": 10,
            "margin_buffer": 5,
            "difficulty": "easy",
            "preferred_style": "conversational",
        },
    )
    assert sess_res.status_code == 201
    session_id = sess_res.json()["session_id"]

    eval_payload = {
        "user_text": "I drink hot coffee early every morning before going to work.",
        "time_spent_ms": 11200,
        "words_typed": 11,
        "character_count": 60,
    }

    res = await async_client.post(
        f"/api/v1/sessions/{session_id}/evaluate/sync",
        json=eval_payload,
    )
    assert res.status_code == 200
    result = res.json()

    assert "result_id" in result
    assert result["session_id"] == session_id
    assert result["user_text"] == eval_payload["user_text"]
    assert "semantic_validation" in result
    assert result["semantic_validation"]["score"] >= 60.0
    assert result["semantic_validation"]["is_valid"] is True
    assert "grammar_errors" in result
    assert "style_alternative" in result
    assert result["style_alternative"]["style"] == "conversational"
    assert "metrics" in result
    assert result["metrics"]["wpm"] > 0
    assert result["metrics"]["target_met"] is True
    assert "latency" in result
    assert result["latency"]["ttft_ms"] < 800.0
    assert result["latency"]["inference_duration_ms"] < 2500.0
    assert result["latency"]["pipeline_duration_ms"] < 3000.0


@pytest.mark.asyncio
async def test_evaluate_sync_not_found(async_client: httpx.AsyncClient):
    """Sync evaluation returns 404 for missing session."""
    random_id = "11111111-2222-3333-4444-555555555555"
    res = await async_client.post(
        f"/api/v1/sessions/{random_id}/evaluate/sync",
        json={"user_text": "Hello world", "time_spent_ms": 1000, "words_typed": 2},
    )
    assert res.status_code == 404
    assert res.json()["code"] == "SESSION_NOT_FOUND"
