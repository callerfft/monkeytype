"""Latency benchmark request and response models."""

from pydantic import BaseModel, Field
from .metrics import LatencyPercentiles


class LatencyBenchmarkRequest(BaseModel):
    """Payload to trigger an automated latency benchmark execution."""
    iterations: int = Field(3, ge=1, le=10, description="Number of sequential benchmark runs")
    model: str = Field("gemini-2.0-flash", description="Target model name")
    test_prompt: str = Field(
        "Опишите ваш утренний распорядок дня.",
        description="Prompt to evaluate against",
    )
    test_submission: str = Field(
        "Every morning I wake up at seven o'clock and drink a hot cup of coffee before starting my work.",
        description="Synthetic user text submission",
    )


class LatencyBenchmarkResponse(BaseModel):
    """Latency benchmark aggregated percentiles and constraint check."""
    timestamp: str = Field(..., description="ISO 8601 benchmark execution timestamp")
    iterations: int = Field(..., description="Completed test iterations")
    ttft_ms: LatencyPercentiles = Field(..., description="Time to first token statistics")
    inference_duration_ms: LatencyPercentiles = Field(..., description="LLM inference duration statistics")
    pipeline_duration_ms: LatencyPercentiles = Field(..., description="Total pipeline latency statistics")
    meets_constraint: bool = Field(
        ...,
        description="True if p95 inference_duration_ms < 2500ms and pipeline_duration_ms < 3000ms",
    )
