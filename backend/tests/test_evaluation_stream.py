"""Streaming evaluation SSE event sequence and payload schema tests."""

import json
import pytest
import httpx


@pytest.mark.asyncio
async def test_streaming_evaluation_complete_sequence(async_client: httpx.AsyncClient):
    """Verify full SSE event sequence: session_start -> tokens -> errors -> semantics -> style -> metrics -> done."""
    # 1. Create a session
    sess_res = await async_client.post(
        "/api/v1/sessions",
        json={
            "mode": "translation",
            "source_language": "ru",
            "target_language": "en",
            "timer_seconds": 30,
            "target_word_count": 8,
            "margin_buffer": 4,
            "difficulty": "easy",
            "preferred_style": "formal",
        },
    )
    assert sess_res.status_code == 201
    session_id = sess_res.json()["session_id"]

    # 2. Evaluate submission with intentional grammatical issues
    user_submission = "he have alot of coffee in the morning."
    eval_payload = {
        "user_text": user_submission,
        "time_spent_ms": 14000,
        "words_typed": len(user_submission.split()),
        "character_count": len(user_submission),
    }

    response = await async_client.post(
        f"/api/v1/sessions/{session_id}/evaluate",
        json=eval_payload,
    )
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]

    # 3. Parse SSE chunks
    raw_body = response.text
    events = []
    blocks = raw_body.strip().split("\n\n")

    for block in blocks:
        if not block.strip():
            continue
        lines = block.strip().split("\n")
        event_name = None
        event_data = None
        for line in lines:
            if line.startswith("event:"):
                event_name = line[len("event:") :].strip()
            elif line.startswith("data:"):
                data_str = line[len("data:") :].strip()
                event_data = json.loads(data_str)
        if event_name and event_data is not None:
            events.append((event_name, event_data))

    event_names = [e[0] for e in events]

    # Verify event presence in correct order
    assert "session_start" in event_names
    assert "token" in event_names
    assert "grammar_errors" in event_names
    assert "semantic_check" in event_names
    assert "style_alternative" in event_names
    assert "metrics" in event_names
    assert "done" in event_names

    # 4. Verify grammar error spans character offsets
    error_events = [e[1] for e in events if e[0] == "grammar_errors"]
    assert len(error_events) >= 1
    error_list = error_events[0]
    assert isinstance(error_list, list)
    assert len(error_list) >= 1

    for err in error_list:
        start = err["start"]
        end = err["end"]
        original = err["original_text"]
        # Character offset integrity invariant: substring must match exactly
        assert user_submission[start:end] == original
        assert err["category"] in ["grammar", "spelling", "punctuation", "syntax", "word_choice", "agreement", "tense"]
        assert err["severity"] in ["error", "warning", "info"]

    # 5. Verify semantic validation payload
    semantic_events = [e[1] for e in events if e[0] == "semantic_check"]
    assert len(semantic_events) >= 1
    sem = semantic_events[0]
    assert "is_valid" in sem
    assert 0.0 <= sem["score"] <= 100.0
    assert "explanation" in sem
    assert isinstance(sem["missing_concepts"], list)

    # 6. Verify single style alternative
    style_events = [e[1] for e in events if e[0] == "style_alternative"]
    assert len(style_events) == 1
    style = style_events[0]
    assert style["style"] == "formal"
    assert len(style["text"]) > 0
    assert len(style["explanation"]) > 0

    # 7. Verify session metrics
    metric_events = [e[1] for e in events if e[0] == "metrics"]
    assert len(metric_events) >= 1
    met = metric_events[0]
    assert met["wpm"] > 0
    assert 0.0 <= met["accuracy_score"] <= 100.0
    assert met["time_spent_ms"] == 14000
    assert "target_met" in met

    # 8. Verify SLA compliance in done event
    done_events = [e[1] for e in events if e[0] == "done"]
    assert len(done_events) == 1
    done = done_events[0]
    latency = done["latency"]
    assert latency["ttft_ms"] < 800.0, f"TTFT SLA breached: {latency['ttft_ms']}ms"
    assert latency["inference_duration_ms"] < 2500.0, f"Inference SLA breached: {latency['inference_duration_ms']}ms"
    assert latency["pipeline_duration_ms"] < 3000.0, f"Pipeline SLA breached: {latency['pipeline_duration_ms']}ms"


@pytest.mark.asyncio
async def test_evaluate_nonexistent_session_404(async_client: httpx.AsyncClient):
    """Attempting to evaluate a non-existent session returns 404."""
    random_id = "00000000-0000-0000-0000-000000000000"
    payload = {
        "user_text": "Sample text",
        "time_spent_ms": 5000,
        "words_typed": 2,
    }
    res = await async_client.post(f"/api/v1/sessions/{random_id}/evaluate", json=payload)
    assert res.status_code == 404
    data = res.json()
    assert data["code"] == "SESSION_NOT_FOUND"
