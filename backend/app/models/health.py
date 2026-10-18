"""Health check models."""

from typing import Literal
from pydantic import BaseModel, Field


class HealthStatus(BaseModel):
    """Backend service health and provider connectivity status."""
    status: Literal["ok", "degraded", "down"] = Field(..., description="Overall health state")
    service: str = Field("linguatype-backend", description="Service identifier")
    version: str = Field("1.0.0", description="Service release version")
    llm_connected: bool = Field(..., description="LLM provider reachable")
    llm_provider: str = Field("google-gemini-flash", description="Configured LLM engine")
