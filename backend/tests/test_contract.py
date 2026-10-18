"""Contract verification tests against contracts/api_v1.json."""

import json
from pathlib import Path
import pytest

from app.models import (
    SessionCreateRequest,
    Prompt,
    SessionResponse,
    EvaluationRequest,
    GrammarErrorSpan,
    SemanticValidation,
    StyleAlternative,
    SessionMetrics,
    LatencyBreakdown,
    EvaluationResult,
    SSESessionStartPayload,
    SSETokenPayload,
    SSEDonePayload,
    SSEStreamEvent,
    UserProfile,
    UserProfileUpdate,
    GameResultSummary,
    HistoryListResponse,
    HealthStatus,
    LatencyBenchmarkRequest,
    LatencyPercentiles,
    LatencyBenchmarkResponse,
    ErrorResponse,
)


def test_contract_file_exists(contract_path: Path):
    """Verify that contracts/api_v1.json exists and is valid JSON."""
    assert contract_path.exists(), f"Contract file not found at {contract_path}"
    with open(contract_path, "r", encoding="utf-8") as f:
        spec = json.load(f)

    assert spec.get("openapi") == "3.1.0"
    assert "paths" in spec
    assert "components" in spec
    assert "schemas" in spec["components"]


def test_all_contract_schemas_have_pydantic_counterparts(contract_path: Path):
    """Ensure all 23 contract schemas are mapped to Pydantic models."""
    with open(contract_path, "r", encoding="utf-8") as f:
        spec = json.load(f)

    contract_schemas = spec["components"]["schemas"]
    assert len(contract_schemas) == 23

    model_mapping = {
        "SessionCreateRequest": SessionCreateRequest,
        "Prompt": Prompt,
        "SessionResponse": SessionResponse,
        "EvaluationRequest": EvaluationRequest,
        "GrammarErrorSpan": GrammarErrorSpan,
        "SemanticValidation": SemanticValidation,
        "StyleAlternative": StyleAlternative,
        "SessionMetrics": SessionMetrics,
        "LatencyBreakdown": LatencyBreakdown,
        "EvaluationResult": EvaluationResult,
        "SSESessionStartPayload": SSESessionStartPayload,
        "SSETokenPayload": SSETokenPayload,
        "SSEDonePayload": SSEDonePayload,
        "SSEStreamEvent": SSEStreamEvent,
        "UserProfile": UserProfile,
        "UserProfileUpdate": UserProfileUpdate,
        "GameResultSummary": GameResultSummary,
        "HistoryListResponse": HistoryListResponse,
        "HealthStatus": HealthStatus,
        "LatencyBenchmarkRequest": LatencyBenchmarkRequest,
        "LatencyPercentiles": LatencyPercentiles,
        "LatencyBenchmarkResponse": LatencyBenchmarkResponse,
        "ErrorResponse": ErrorResponse,
    }

    for schema_name, pydantic_cls in model_mapping.items():
        assert schema_name in contract_schemas, f"Missing schema '{schema_name}' in contract"
        assert pydantic_cls is not None, f"Missing Pydantic class for '{schema_name}'"


def test_session_create_request_validation():
    """Verify SessionCreateRequest contract rules: timer constraints and defaults."""
    # Valid timer 15, 30, 60, or None
    req1 = SessionCreateRequest(mode="translation", timer_seconds=15)
    assert req1.timer_seconds == 15

    req2 = SessionCreateRequest(mode="situation_image", timer_seconds=None)
    assert req2.timer_seconds is None

    # Invalid timer must raise ValueError
    with pytest.raises(ValueError):
        SessionCreateRequest(mode="translation", timer_seconds=45)

    # Word limits: 3 <= target <= 50
    with pytest.raises(ValueError):
        SessionCreateRequest(mode="translation", target_word_count=2)


def test_grammar_error_span_contract():
    """Verify GrammarErrorSpan 0-based character offsets and severity constraints."""
    span = GrammarErrorSpan(
        start=0,
        end=4,
        original_text="They",
        message="Agreement issue",
        suggestion="They are",
        category="agreement",
        severity="error",
    )
    assert span.start == 0
    assert span.end == 4
    assert span.severity.value == "error"

    with pytest.raises(ValueError):
        GrammarErrorSpan(
            start=-1,
            end=4,
            original_text="a",
            message="b",
            suggestion="c",
            category="spelling",
            severity="error",
        )
