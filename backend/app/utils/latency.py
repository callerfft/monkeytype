"""Latency timing and statistics utilities."""

import time
import math
from typing import List, Optional
from ..models.metrics import LatencyBreakdown, LatencyPercentiles


class LatencyTimer:
    """High-resolution wall-clock timer for measuring TTFT, inference, and pipeline latency."""

    def __init__(self) -> None:
        self.start_time: float = time.perf_counter()
        self.ttft_time: Optional[float] = None
        self.inference_time: Optional[float] = None
        self.pipeline_time: Optional[float] = None

    def mark_ttft(self) -> float:
        """Mark time of first token received."""
        if self.ttft_time is None:
            self.ttft_time = time.perf_counter()
        return (self.ttft_time - self.start_time) * 1000.0

    def mark_inference_done(self) -> float:
        """Mark completion of model token generation."""
        if self.inference_time is None:
            self.inference_time = time.perf_counter()
        return (self.inference_time - self.start_time) * 1000.0

    def mark_pipeline_done(self) -> LatencyBreakdown:
        """Mark completion of full evaluation response pipeline."""
        self.pipeline_time = time.perf_counter()
        ttft = (self.ttft_time - self.start_time) * 1000.0 if self.ttft_time else 0.0
        inf = (self.inference_time - self.start_time) * 1000.0 if self.inference_time else 0.0
        pipe = (self.pipeline_time - self.start_time) * 1000.0

        return LatencyBreakdown(
            ttft_ms=round(ttft, 2),
            inference_duration_ms=round(inf, 2),
            pipeline_duration_ms=round(pipe, 2),
        )


def calculate_percentiles(values: List[float]) -> LatencyPercentiles:
    """Calculate min, max, avg, and p95 from a sequence of latency numbers."""
    if not values:
        return LatencyPercentiles(min=0.0, max=0.0, avg=0.0, p95=0.0)

    sorted_vals = sorted(values)
    n = len(sorted_vals)
    min_val = round(sorted_vals[0], 2)
    max_val = round(sorted_vals[-1], 2)
    avg_val = round(sum(sorted_vals) / n, 2)

    # 95th percentile index
    p95_index = min(math.ceil(0.95 * n) - 1, n - 1)
    p95_val = round(sorted_vals[max(0, p95_index)], 2)

    return LatencyPercentiles(
        min=min_val,
        max=max_val,
        avg=avg_val,
        p95=p95_val,
    )
