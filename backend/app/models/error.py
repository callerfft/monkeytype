"""Standardized API error models."""

from typing import Any, Optional
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standardized machine-readable error payload."""
    code: str = Field(..., description="Standardized error code (e.g. VALIDATION_ERROR, SESSION_NOT_FOUND)")
    message: str = Field(..., description="Human-readable description of error")
    details: Optional[Any] = Field(None, description="Optional extra debug information or field errors")
