"""Evaluation request, result, and SSE streaming models."""

from typing import List, Literal, Optional, Any, Union
from pydantic import BaseModel, Field

from .grammar import GrammarErrorSpan, SemanticValidation, StyleAlternative
from .metrics import SessionMetrics, LatencyBreakdown
from .error import ErrorResponse


class EvaluationRequest(BaseModel):
    """User submission evaluation request payload."""
    user_text: str = Field(..., min_length=0, max_length=1000, description="Raw text typed by user")
    time_spent_ms: int = Field(..., ge=0, description="Active typing duration in milliseconds")
    words_typed: int = Field(..., ge=0, description="Count of words typed")
    character_count: Optional[int] = Field(None, ge=0, description="Count of characters typed")
    keystroke_count: Optional[int] = Field(None, ge=0, description="Count of raw keystrokes")
    check_case_and_period: Optional[bool] = Field(None, description="Flag missing initial capitalization and terminal period")


class EvaluationResult(BaseModel):
    """Complete evaluation report for submission."""
    result_id: str = Field(..., description="Evaluation result UUID")
    session_id: str = Field(..., description="Associated session UUID")
    user_id: Optional[str] = Field(None, description="Firebase UID if authenticated, or null for guest")
    user_text: str = Field(..., description="Evaluated text")
    semantic_validation: SemanticValidation = Field(..., description="Semantic meaning evaluation")
    grammar_errors: List[GrammarErrorSpan] = Field(..., description="List of identified errors")
    style_alternative: StyleAlternative = Field(..., description="Recommended stylistic alternative")
    metrics: SessionMetrics = Field(..., description="Typing metrics")
    latency: LatencyBreakdown = Field(..., description="Evaluation latency breakdown")
    created_at: str = Field(..., description="ISO 8601 creation timestamp")


class SSESessionStartPayload(BaseModel):
    """Payload for 'session_start' SSE event."""
    session_id: str
    status: Literal["active", "starting", "processing"] = "active"


class SSETokenPayload(BaseModel):
    """Payload for 'token' chunk SSE event."""
    text: str
    token: Optional[str] = None
    index: Optional[int] = None


class SSEDonePayload(BaseModel):
    """Payload for 'done' final SSE event."""
    evaluation_id: Optional[str] = None
    result_id: Optional[str] = None
    latency: LatencyBreakdown


class SSEStreamEvent(BaseModel):
    """Structured SSE event schema."""
    event: Literal[
        "session_start",
        "token",
        "grammar_errors",
        "semantic_check",
        "style_alternative",
        "metrics",
        "done",
        "error",
    ]
    data: Union[
        SSESessionStartPayload,
        SSETokenPayload,
        List[GrammarErrorSpan],
        SemanticValidation,
        StyleAlternative,
        SessionMetrics,
        SSEDonePayload,
        EvaluationResult,
        ErrorResponse,
        Any,
    ]
