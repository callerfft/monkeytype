"""User profile and results history router."""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, status

from ...models.user import (
    UserProfile,
    UserProfileUpdate,
    HistoryListResponse,
)
from ...core.auth import get_current_user
from ...services.session_store import session_store

router = APIRouter(tags=["User & Settings"])


@router.get(
    "/user/profile",
    response_model=UserProfile,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile and settings",
)
async def get_profile(
    user: Dict[str, Any] = Depends(get_current_user),
) -> UserProfile:
    """Retrieve profile and preferences for authenticated user."""
    profile = session_store.get_user_profile(
        user_id=user["uid"],
        email=user.get("email", "user@linguatype.app"),
    )
    return profile


@router.put(
    "/user/profile",
    response_model=UserProfile,
    status_code=status.HTTP_200_OK,
    summary="Update user settings and preferences",
)
async def update_profile(
    update: UserProfileUpdate,
    user: Dict[str, Any] = Depends(get_current_user),
) -> UserProfile:
    """Update preferred style, languages, and input settings."""
    profile = session_store.update_user_profile(
        user_id=user["uid"],
        update=update,
    )
    return profile


@router.get(
    "/results",
    response_model=HistoryListResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve user session history and game results",
)
async def get_history(
    limit: int = Query(20, ge=1, le=100, description="Page limit"),
    offset: int = Query(0, ge=0, description="Page offset"),
    mode: Optional[str] = Query(None, description="Filter by game mode: translation | situation_image"),
    user: Dict[str, Any] = Depends(get_current_user),
) -> HistoryListResponse:
    """Fetch paginated game results history."""
    items, total = session_store.get_results(
        user_id=user["uid"],
        limit=limit,
        offset=offset,
        mode=mode,
    )
    return HistoryListResponse(
        results=items,
        total=total,
        offset=offset,
        limit=limit,
    )
