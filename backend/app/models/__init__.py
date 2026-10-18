"""Domain models and schemas for LinguaType API."""

from .prompt import Prompt, PromptType, DifficultyLevel
from .grammar import (
    ErrorCategory,
    ErrorSeverity,
    PreferredStyle,
    GrammarErrorSpan,
    SemanticValidation,
    StyleAlternative,
)
from .session import (
    InputMode,
    SessionStatus,
    SessionCreateRequest,
    SessionResponse,
)
from .metrics import (
    SessionMetrics,
    LatencyBreakdown,
    LatencyPercentiles,
)
from .evaluation import (
    EvaluationRequest,
    EvaluationResult,
    SSESessionStartPayload,
    SSETokenPayload,
    SSEDonePayload,
    SSEStreamEvent,
)
from .user import (
    UserProfile,
    UserProfileUpdate,
    GameResultSummary,
    HistoryListResponse,
)
from .health import HealthStatus
from .benchmark import (
    LatencyBenchmarkRequest,
    LatencyBenchmarkResponse,
)
from .error import ErrorResponse

__all__ = [
    "Prompt",
    "PromptType",
    "DifficultyLevel",
    "ErrorCategory",
    "ErrorSeverity",
    "PreferredStyle",
    "GrammarErrorSpan",
    "SemanticValidation",
    "StyleAlternative",
    "InputMode",
    "SessionStatus",
    "SessionCreateRequest",
    "SessionResponse",
    "SessionMetrics",
    "LatencyBreakdown",
    "LatencyPercentiles",
    "EvaluationRequest",
    "EvaluationResult",
    "SSESessionStartPayload",
    "SSETokenPayload",
    "SSEDonePayload",
    "SSEStreamEvent",
    "UserProfile",
    "UserProfileUpdate",
    "GameResultSummary",
    "HistoryListResponse",
    "HealthStatus",
    "LatencyBenchmarkRequest",
    "LatencyBenchmarkResponse",
    "ErrorResponse",
]
