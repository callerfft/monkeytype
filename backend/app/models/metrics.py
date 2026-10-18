"""Typing speed metrics and latency measurement models."""

from typing import Optional
from pydantic import BaseModel, Field


class SessionMetrics(BaseModel):
    """Typing performance and constraint compliance metrics."""
    wpm: float = Field(..., ge=0.0, description="Words Per Minute ((chars / 5) / (minutes))")
    accuracy_score: float = Field(..., ge=0.0, le=100.0, description="Overall accuracy (0-100)")
    time_spent_ms: int = Field(..., ge=0, description="Active typing duration in milliseconds")
    word_count: int = Field(..., ge=0, description="Count of words typed")
    target_word_count: Optional[int] = Field(None, ge=1, description="Target word count constraint")
    target_met: bool = Field(..., description="True if target word count constraint met without overflow")
    word_limit_exceeded: Optional[bool] = Field(None, description="True if word count exceeded max allowed")
    timer_expired: Optional[bool] = Field(None, description="True if user timed out")


class LatencyBreakdown(BaseModel):
    """Execution latency breakdown in milliseconds."""
    ttft_ms: float = Field(..., description="Time To First Token (< 800ms SLA)")
    inference_duration_ms: float = Field(..., description="Total LLM inference duration (< 2500ms SLA)")
    pipeline_duration_ms: float = Field(..., description="Total pipeline latency (< 3000ms SLA)")


class LatencyPercentiles(BaseModel):
    """Statistical summary for latency benchmark."""
    min: float = Field(..., description="Minimum latency in ms")
    max: float = Field(..., description="Maximum latency in ms")
    avg: float = Field(..., description="Average latency in ms")
    p95: float = Field(..., description="95th percentile latency in ms")
