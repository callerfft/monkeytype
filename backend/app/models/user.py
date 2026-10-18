"""User profile and historical result models."""

from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr

from .prompt import PromptType
from .grammar import PreferredStyle
from .session import InputMode


class UserProfile(BaseModel):
    """User profile and preference settings."""
    id: str = Field(..., description="Firebase UID")
    email: str = Field(..., description="User email address")
    display_name: Optional[str] = Field(None, description="Optional display name")
    native_language: str = Field("ru", description="Native/source language code")
    target_language: str = Field("en", description="Target learning language code")
    preferred_style: PreferredStyle = Field(PreferredStyle.CONVERSATIONAL, description="Default style register")
    allow_loose_phrasing: bool = Field(True, description="Allow idiomatic variations")
    input_mode: InputMode = Field(InputMode.FREE, description="Default input mode")
    created_at: str = Field(..., description="ISO 8601 timestamp")
    updated_at: str = Field(..., description="ISO 8601 timestamp")


class UserProfileUpdate(BaseModel):
    """Payload to update user settings."""
    native_language: Optional[str] = None
    target_language: Optional[str] = None
    preferred_style: Optional[PreferredStyle] = None
    allow_loose_phrasing: Optional[bool] = None
    input_mode: Optional[InputMode] = None


class GameResultSummary(BaseModel):
    """Summarized historical game result entry."""
    id: str = Field(..., description="Result UUID")
    session_id: str = Field(..., description="Session UUID")
    mode: PromptType = Field(..., description="Game mode")
    source_language: str = Field(..., description="Source language")
    target_language: str = Field(..., description="Target language")
    prompt_content: str = Field(..., description="Prompt phrase/situation")
    user_text: str = Field(..., description="Submission text")
    time_spent_ms: int = Field(..., description="Duration in ms")
    wpm: float = Field(..., description="Typing speed WPM")
    accuracy_score: float = Field(..., description="Accuracy score")
    semantic_valid: bool = Field(..., description="Semantic match result")
    error_count: int = Field(..., description="Number of grammar errors")
    recommended_variant: str = Field(..., description="Style-optimized sentence")
    preferred_style: str = Field(..., description="Style tone applied")
    created_at: str = Field(..., description="ISO 8601 timestamp")


class HistoryListResponse(BaseModel):
    """Paginated user history response."""
    results: List[GameResultSummary] = Field(..., description="Historical results list")
    total: int = Field(..., ge=0, description="Total number of results available")
    offset: int = Field(..., ge=0, description="Current offset")
    limit: int = Field(..., ge=1, description="Page limit")
