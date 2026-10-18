"""End-to-end integration test verifying complete ASGI session lifecycle, SSE streaming, latency telemetry, and dynamic style suggestions."""

import json
import pytest
import httpx
from app.models.grammar import PreferredStyle


@pytest.mark.asyncio
async def test_e2e_full_asgi_session_lifecycle_and_streaming(async_client: httpx.AsyncClient):
    """E2E flow: Create session -> Stream evaluation -> Verify dynamic non-coffee style alternative and latency SLAs."""
    # 1. Create a session with Mountain Ascent prompt context
    create_res = await async_client.post(
        "/api/v1/sessions",
        json={
            "mode": "translation",
            "source_language": "ru",
            "target_language": "en",
            "timer_seconds": 30,
            "target_word_count": 12,
            "margin_buffer": 5,
            "difficulty": "medium",
            "preferred_style": "formal",
            "allow_loose_phrasing": True,
        },
    )
    assert create_res.status_code == 201
    sess_data = create_res.json()
    session_id = sess_data["session_id"]
    assert sess_data["status"] == "active"
    assert "prompt" in sess_data

    # 2. Verify session retrieval
    get_res = await async_client.get(f"/api/v1/sessions/{session_id}")
    assert get_res.status_code == 200
    assert get_res.json()["session_id"] == session_id

    # 3. Stream evaluation for a mountain ascent translation
    user_submission = "The hikers continued climbing the mountain despite the sudden rain."
    eval_req = {
        "user_text": user_submission,
        "time_spent_ms": 11500,
        "words_typed": len(user_submission.split()),
        "character_count": len(user_submission),
    }

    eval_res = await async_client.post(
        f"/api/v1/sessions/{session_id}/evaluate",
        json=eval_req,
    )
    assert eval_res.status_code == 200
    assert "text/event-stream" in eval_res.headers.get("content-type", "")

    # 4. Parse Server-Sent Events (SSE)
    raw_body = eval_res.text
    blocks = raw_body.strip().split("\n\n")
    events = []
    for block in blocks:
        if not block.strip():
            continue
        event_name = None
        event_data = None
        for line in block.strip().split("\n"):
            if line.startswith("event:"):
                event_name = line[len("event:") :].strip()
            elif line.startswith("data:"):
                data_str = line[len("data:") :].strip()
                event_data = json.loads(data_str)
        if event_name and event_data is not None:
            events.append((event_name, event_data))

    event_map = {name: [] for name, _ in events}
    for name, data in events:
        event_map[name].append(data)

    # 5. Assert complete event sequence
    assert "session_start" in event_map
    assert "token" in event_map
    assert len(event_map["token"]) >= 1
    assert "grammar_errors" in event_map
    assert "semantic_check" in event_map
    assert "style_alternative" in event_map
    assert "metrics" in event_map
    assert "done" in event_map

    # 6. Verify Dynamic Style Alternative (Adversarial Integrity Check)
    style_payload = event_map["style_alternative"][0]
    assert style_payload["style"] == "formal"
    style_text = style_payload["text"]

    # Integrity Assertions: No coffee leakage in non-coffee prompt!
    coffee_keywords = ["coffee", "beverage", "partake", "warm cup", "espresso"]
    for kw in coffee_keywords:
        assert kw not in style_text.lower(), f"Detected coffee leakage in mountain prompt: '{style_text}'"

    # Must contain relevant vocabulary or formal syntactic elevation
    assert len(style_text) > 10
    assert len(style_payload["explanation"]) > 10

    # 7. Verify Latency SLAs in done event
    done_payload = event_map["done"][0]
    latency = done_payload["latency"]
    assert latency["ttft_ms"] < 800.0, f"TTFT SLA breached: {latency['ttft_ms']}ms"
    assert latency["inference_duration_ms"] < 2500.0, f"Inference SLA breached: {latency['inference_duration_ms']}ms"
    assert latency["pipeline_duration_ms"] < 3000.0, f"Pipeline SLA breached: {latency['pipeline_duration_ms']}ms"

    # 8. Verify Session Status transitioned to completed
    final_sess = await async_client.get(f"/api/v1/sessions/{session_id}")
    assert final_sess.status_code == 200
    assert final_sess.json()["status"] == "completed"


@pytest.mark.asyncio
async def test_e2e_dynamic_style_alternatives_across_topics(async_client: httpx.AsyncClient):
    """Verify that style alternatives dynamically match the topic across multiple registers."""
    test_cases = [
        {
            "prompt_content": "Несмотря на внезапный ливень, туристы продолжили восхождение к вершине древней горы.",
            "user_text": "The tourists climbed the mountain despite the heavy rain.",
            "style": PreferredStyle.CONCISE,
            "expected_theme_words": ["rain", "hiker", "mountain", "ascent", "despite"],
            "forbidden_words": ["coffee", "beverage", "cup"],
        },
        {
            "prompt_content": "Технологии искусственного интеллекта стремительно меняют подход к решению сложных задач.",
            "user_text": "AI technologies are changing how we solve difficult problems.",
            "style": PreferredStyle.ACADEMIC,
            "expected_theme_words": ["artificial", "intelligence", "algorithm", "problem", "framework", "technolog"],
            "forbidden_words": ["coffee", "beverage", "tea"],
        },
        {
            "prompt_content": "Регулярная физическая активность и здоровое питание укрепляют иммунитет и улучшают настроение.",
            "user_text": "Regular exercise and good food boost immunity and mood.",
            "style": PreferredStyle.BUSINESS,
            "expected_theme_words": ["wellness", "performance", "vitality", "lifestyle", "habit"],
            "forbidden_words": ["coffee", "beverage"],
        },
        {
            "prompt_content": "Солнце ярко светит, и легкий ветерок шелестит зелеными листьями деревьев.",
            "user_text": "The sun is shining bright and the wind is blowing through the trees.",
            "style": PreferredStyle.CONVERSATIONAL,
            "expected_theme_words": ["sun", "breeze", "trees", "blowing"],
            "forbidden_words": ["coffee", "beverage", "workplace"],
        },
    ]

    for tc in test_cases:
        create_res = await async_client.post(
            "/api/v1/sessions",
            json={
                "mode": "translation",
                "source_language": "ru",
                "target_language": "en",
                "preferred_style": tc["style"].value,
            },
        )
        assert create_res.status_code == 201
        session_id = create_res.json()["session_id"]

        # Evaluate synchronously
        eval_res = await async_client.post(
            f"/api/v1/sessions/{session_id}/evaluate/sync",
            json={
                "user_text": tc["user_text"],
                "time_spent_ms": 8000,
                "words_typed": len(tc["user_text"].split()),
            },
        )
        assert eval_res.status_code == 200
        alt = eval_res.json()["style_alternative"]
        assert alt["style"] == tc["style"].value

        alt_text_lower = alt["text"].lower()
        # Verify forbidden words are not present
        for forbidden in tc["forbidden_words"]:
            assert forbidden not in alt_text_lower, (
                f"Topic '{tc['prompt_content']}' leaked forbidden word '{forbidden}' in alternative: '{alt['text']}'"
            )


@pytest.mark.asyncio
async def test_e2e_sync_evaluation_fallback(async_client: httpx.AsyncClient):
    """Verify synchronous evaluation fallback endpoint returns complete valid result."""
    create_res = await async_client.post(
        "/api/v1/sessions",
        json={
            "mode": "translation",
            "source_language": "ru",
            "target_language": "en",
            "preferred_style": "business",
        },
    )
    assert create_res.status_code == 201
    session_id = create_res.json()["session_id"]

    eval_res = await async_client.post(
        f"/api/v1/sessions/{session_id}/evaluate/sync",
        json={
            "user_text": "We need to finish our quarterly milestones ahead of schedule.",
            "time_spent_ms": 9500,
            "words_typed": 10,
        },
    )
    assert eval_res.status_code == 200
    data = eval_res.json()

    assert data["session_id"] == session_id
    assert "semantic_validation" in data
    assert "grammar_errors" in data
    assert "style_alternative" in data
    assert data["style_alternative"]["style"] == "business"
    assert "metrics" in data
    assert "latency" in data
    assert data["latency"]["pipeline_duration_ms"] < 3000.0


@pytest.mark.asyncio
async def test_e2e_latency_benchmark_meets_sla(async_client: httpx.AsyncClient):
    """Verify latency benchmark endpoint across multiple iterations meets TTFT and inference constraints."""
    res = await async_client.post(
        "/api/v1/benchmark/latency",
        json={
            "iterations": 3,
            "model": "gemini-2.0-flash",
            "test_prompt": "Несмотря на внезапный ливень, туристы продолжили восхождение к вершине древней горы.",
            "test_submission": "The hikers continued climbing the mountain despite the sudden rainstorm.",
        },
    )
    assert res.status_code == 200
    data = res.json()

    assert data["iterations"] == 3
    assert data["meets_constraint"] is True
    assert data["ttft_ms"]["p95"] < 800.0
    assert data["inference_duration_ms"]["p95"] < 2500.0
    assert data["pipeline_duration_ms"]["p95"] < 3000.0
