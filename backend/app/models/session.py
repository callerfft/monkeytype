"""Session creation and response models."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator

from .prompt import Prompt, PromptType, DifficultyLevel
from .grammar import PreferredStyle


class InputMode(str, Enum):
    """Input modes."""
    FREE = "free"
    SCAFFOLDING = "scaffolding"


class SessionStatus(str, Enum):
    """Session operational status."""
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class SessionCreateRequest(BaseModel):
    """Payload to initialize a new game session."""
    mode: PromptType = Field(..., description="Mode A (translation) or Mode B (situation_image)")
    timer_seconds: Optional[int] = Field(30, description="Time limit in seconds (15, 30, 60, or null for untimed)")
    target_word_count: int = Field(10, ge=3, le=50, description="Target word count")
    margin_buffer: int = Field(5, ge=0, le=15, description="Allowed margin buffer")
    source_language: str = Field("ru", pattern=r"^[a-z]{2}(-[A-Z]{2})?$", description="Source language ISO code")
    target_language: str = Field("en", pattern=r"^[a-z]{2}(-[A-Z]{2})?$", description="Target language ISO code")
    difficulty: DifficultyLevel = Field(DifficultyLevel.MEDIUM, description="Vocabulary difficulty")
    input_mode: InputMode = Field(InputMode.FREE, description="Input mode: free or scaffolding")
    preferred_style: PreferredStyle = Field(PreferredStyle.CONVERSATIONAL, description="Preferred tone for alternative")
    allow_loose_phrasing: bool = Field(True, description="Allow loose / idiomatic phrasing in semantic check")
    check_case_and_period: bool = Field(False, description="Flag missing initial capitalization and terminal period")

    @field_validator("timer_seconds")
    @classmethod
    def validate_timer(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v not in (15, 30, 60):
            raise ValueError("timer_seconds must be one of 15, 30, 60, or null")
        return v


class SessionResponse(BaseModel):
    """Session entity response."""
    session_id: str = Field(..., description="Unique session UUID")
    status: SessionStatus = Field(..., description="Session state")
    mode: PromptType = Field(..., description="Game mode")
    prompt: Prompt = Field(..., description="Selected prompt for session")
    timer_seconds: Optional[int] = Field(None, description="Active timer limit")
    input_mode: InputMode = Field(..., description="Selected input mode")
    preferred_style: PreferredStyle = Field(..., description="Preferred stylistic register")
    allow_loose_phrasing: bool = Field(..., description="Loose phrasing setting")
    check_case_and_period: bool = Field(False, description="Flag missing initial capitalization and terminal period")
    created_at: str = Field(..., description="ISO 8601 creation timestamp")
    expires_at: str = Field(..., description="ISO 8601 expiration timestamp")

