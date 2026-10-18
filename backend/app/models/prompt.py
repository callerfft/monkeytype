"""Prompt models and schemas."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class PromptType(str, Enum):
    """Supported prompt game modes."""
    TRANSLATION = "translation"
    SITUATION_IMAGE = "situation_image"


class DifficultyLevel(str, Enum):
    """Prompt difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Prompt(BaseModel):
    """Prompt entity representation."""
    id: str = Field(..., description="Unique prompt identifier (UUID)")
    type: PromptType = Field(..., description="Prompt type")
    source_language: str = Field(..., description="Language of prompt")
    target_language: str = Field(..., description="Expected language for user submission")
    content: str = Field(..., description="Prompt textual content")
    image_url: Optional[str] = Field(None, description="URL to image for Mode B if available")
    difficulty: DifficultyLevel = Field(..., description="Vocabulary and complexity level")
    target_word_count: int = Field(..., ge=1, description="Target word count")
    margin_buffer: int = Field(..., ge=0, description="Allowed word buffer")
    max_word_count: int = Field(..., ge=1, description="Upper cap: target_word_count + margin_buffer")
