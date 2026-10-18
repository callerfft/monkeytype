"""Latency benchmark router."""

import datetime
from typing import List, Optional
from fastapi import APIRouter, status

from ...models.benchmark import (
    LatencyBenchmarkRequest,
    LatencyBenchmarkResponse,
)
from ...models.session import (
    SessionCreateRequest,
    PromptType,
)
from ...models.evaluation import EvaluationRequest
from ...services.session_store import session_store
from ...services.llm_service import llm_service
from ...utils.latency import LatencyTimer, calculate_percentiles
from ...config import settings

router = APIRouter(prefix="/benchmark", tags=["Health & Benchmarking"])


@router.post(
    "/latency",
    response_model=LatencyBenchmarkResponse,
    status_code=status.HTTP_200_OK,
    summary="Run automated latency verification benchmark",
)
async def run_latency_benchmark(
    request: Optional[LatencyBenchmarkRequest] = None,
) -> LatencyBenchmarkResponse:
    """Execute streaming evaluation benchmark and report percentiles against SLA.
    
    When GEMINI_API_KEY and LLM_PROVIDER='gemini' are configured, benchmarks live
    Google Generative Language API streaming. In offline development mode, exercises
    the genuine MockLLMService linguistic processing and token streaming pipeline.
    """
    req = request or LatencyBenchmarkRequest()
    iterations = req.iterations

    ttfts: List[float] = []
    inferences: List[float] = []
    pipelines: List[float] = []

    # Temporary test session
    session_req = SessionCreateRequest(
        mode=PromptType.TRANSLATION,
        source_language="ru",
        target_language="en",
        timer_seconds=30,
        target_word_count=10,
        margin_buffer=5,
    )
    test_session = session_store.create_session(session_req)
    if req.test_prompt:
        test_session.prompt.content = req.test_prompt

    if req.model and hasattr(llm_service, "model"):
        llm_service.model = req.model

    eval_req = EvaluationRequest(
        user_text=req.test_submission,
        time_spent_ms=12500,
        words_typed=len(req.test_submission.split()),
        character_count=len(req.test_submission),
    )

    for _ in range(iterations):
        timer = LatencyTimer()
        first_token = False

        async for chunk in llm_service.stream_evaluation(eval_req, test_session):
            if "event: token" in chunk and not first_token:
                timer.mark_ttft()
                first_token = True
            elif "event: grammar_errors" in chunk and not timer.inference_time:
                timer.mark_inference_done()

        # If not captured inside loop, mark
        if not timer.ttft_time:
            timer.mark_ttft()
        if not timer.inference_time:
            timer.mark_inference_done()

        breakdown = timer.mark_pipeline_done()
        ttfts.append(breakdown.ttft_ms)
        inferences.append(breakdown.inference_duration_ms)
        pipelines.append(breakdown.pipeline_duration_ms)

    ttft_stats = calculate_percentiles(ttfts)
    inference_stats = calculate_percentiles(inferences)
    pipeline_stats = calculate_percentiles(pipelines)

    # SLA bounds: TTFT < 800ms, inference < 2500ms, pipeline < 3000ms
    meets_constraint = bool(
        ttft_stats.p95 <= settings.SLA_TTFT_MS
        and inference_stats.p95 <= settings.SLA_INFERENCE_MS
        and pipeline_stats.p95 <= settings.SLA_PIPELINE_MS
    )

    return LatencyBenchmarkResponse(
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        iterations=iterations,
        ttft_ms=ttft_stats,
        inference_duration_ms=inference_stats,
        pipeline_duration_ms=pipeline_stats,
        meets_constraint=meets_constraint,
    )
