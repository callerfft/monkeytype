"""Prompts catalog router."""

from typing import List, Optional
from fastapi import APIRouter, Query, status

from ...models.prompt import Prompt, PromptType, DifficultyLevel
from ...services.prompt_store import prompt_store

router = APIRouter(prefix="/prompts", tags=["Prompts"])


@router.get(
    "",
    response_model=List[Prompt],
    status_code=status.HTTP_200_OK,
    summary="List available curated prompts",
)
async def list_prompts(
    mode: Optional[PromptType] = Query(None, description="Filter by mode"),
    source_language: Optional[str] = Query(None, description="Filter by source language"),
    target_language: Optional[str] = Query(None, description="Filter by target language"),
    difficulty: Optional[DifficultyLevel] = Query(None, description="Filter by difficulty"),
    limit: int = Query(10, ge=1, le=50, description="Max results"),
) -> List[Prompt]:
    """Retrieve filtered list of curated prompts."""
    return prompt_store.filter_prompts(
        mode=mode,
        source_language=source_language,
        target_language=target_language,
        difficulty=difficulty,
        limit=limit,
    )
