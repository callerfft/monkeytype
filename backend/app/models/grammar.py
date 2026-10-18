"""Grammar, semantic check, and styling models."""

from enum import Enum
from typing import List
from pydantic import BaseModel, Field


class ErrorCategory(str, Enum):
    """Grammar error categories."""
    GRAMMAR = "grammar"
    SPELLING = "spelling"
    PUNCTUATION = "punctuation"
    SYNTAX = "syntax"
    WORD_CHOICE = "word_choice"
    AGREEMENT = "agreement"
    TENSE = "tense"


class ErrorSeverity(str, Enum):
    """Severity of linguistic error."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class PreferredStyle(str, Enum):
    """Stylistic tone registers."""
    CONVERSATIONAL = "conversational"
    FORMAL = "formal"
    CONCISE = "concise"
    ACADEMIC = "academic"
    BUSINESS = "business"


class GrammarErrorSpan(BaseModel):
    """Identified grammatical/spelling error span in user submission."""
    start: int = Field(..., ge=0, description="0-based start character offset inclusive")
    end: int = Field(..., ge=0, description="0-based end character offset exclusive")
    original_text: str = Field(..., description="Exact substring containing error")
    message: str = Field(..., description="Human-readable explanation of error")
    suggestion: str = Field(..., description="Recommended replacement text")
    category: ErrorCategory = Field(..., description="Linguistic category")
    severity: ErrorSeverity = Field(..., description="Severity level")


class SemanticValidation(BaseModel):
    """Validation of semantic meaning and concept coverage."""
    is_valid: bool = Field(..., description="True if semantic intent matches")
    score: float = Field(..., ge=0.0, le=100.0, description="Semantic preservation score (0-100)")
    explanation: str = Field(..., description="Reasoning for verdict")
    missing_concepts: List[str] = Field(default_factory=list, description="Key concepts omitted")


class StyleAlternative(BaseModel):
    """Exactly ONE alternative rewrite matching user's requested style."""
    style: PreferredStyle = Field(..., description="Style register applied")
    text: str = Field(..., description="Alternative sentence")
    explanation: str = Field(..., description="Rationale for stylistic transformation")
