"""Automated latency verification benchmark asserting SLA compliance."""

import pytest
import httpx


@pytest.mark.asyncio
async def test_health_check_endpoint(async_client: httpx.AsyncClient):
    """GET /api/v1/health returns ok status and connected LLM provider."""
    res = await async_client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["service"] == "linguatype-backend"
    assert data["llm_connected"] is True


@pytest.mark.asyncio
async def test_latency_benchmark_meets_sla(async_client: httpx.AsyncClient):
    """POST /api/v1/benchmark/latency asserts TTFT < 800ms, inference < 2.5s, pipeline < 3.0s."""
    benchmark_req = {
        "iterations": 3,
        "model": "gemini-2.0-flash",
        "test_prompt": "Опишите ваш утренний распорядок дня.",
        "test_submission": "Every morning I wake up at seven o'clock and drink a hot cup of coffee before starting my work.",
    }

    res = await async_client.post("/api/v1/benchmark/latency", json=benchmark_req)
    assert res.status_code == 200
    data = res.json()

    assert data["iterations"] == 3
    assert data["meets_constraint"] is True

    ttft = data["ttft_ms"]
    inference = data["inference_duration_ms"]
    pipeline = data["pipeline_duration_ms"]

    # Strict SLA Assertions
    assert ttft["p95"] < 800.0, f"P95 TTFT SLA breached: {ttft['p95']}ms (SLA: < 800ms)"
    assert inference["p95"] < 2500.0, f"P95 Inference SLA breached: {inference['p95']}ms (SLA: < 2500ms)"
    assert pipeline["p95"] < 3000.0, f"P95 Pipeline SLA breached: {pipeline['p95']}ms (SLA: < 3000ms)"
    assert ttft["min"] > 0
    assert inference["min"] > 0
    assert pipeline["min"] > 0
