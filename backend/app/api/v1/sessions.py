"""Sessions router: creation and retrieval."""

from fastapi import APIRouter, status
from ...models.session import SessionCreateRequest, SessionResponse
from ...services.session_store import session_store
from ...core.exceptions import SessionNotFoundError

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.post(
    "",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new LinguaType game session",
)
async def create_session(request: SessionCreateRequest) -> SessionResponse:
    """Create a new game session with selected constraints."""
    session = session_store.create_session(request)
    return session


@router.get(
    "/{session_id}",
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get session details and prompt by ID",
)
async def get_session(session_id: str) -> SessionResponse:
    """Retrieve session details by UUID."""
    session = session_store.get_session(session_id)
    if not session:
        raise SessionNotFoundError(session_id=session_id)
    return session
