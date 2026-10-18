"""Evaluation router: streaming SSE and synchronous endpoints."""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, status
from starlette.responses import StreamingResponse

from ...models.evaluation import EvaluationRequest, EvaluationResult
from ...services.session_store import session_store
from ...services.llm_service import llm_service
from ...core.exceptions import SessionNotFoundError
from ...core.auth import get_optional_current_user

router = APIRouter(prefix="/sessions", tags=["Evaluation"])


@router.post(
    "/{session_id}/evaluate",
    status_code=status.HTTP_200_OK,
    summary="Stream evaluation feedback via Server-Sent Events (SSE)",
)
async def evaluate_stream(
    session_id: str,
    request: EvaluationRequest,
    user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> StreamingResponse:
    """Stream progressive evaluation chunks via SSE conforming to latency SLA."""
    session = session_store.get_session(session_id)
    if not session:
        raise SessionNotFoundError(session_id=session_id)

    user_id = user["uid"] if user else None

    async def event_generator():
        async for chunk in llm_service.stream_evaluation(request, session):
            yield chunk

        # Auto-mark session completed
        session_store.mark_session_completed(session_id)

    headers = {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(event_generator(), headers=headers, media_type="text/event-stream")


@router.post(
    "/{session_id}/evaluate/sync",
    response_model=EvaluationResult,
    status_code=status.HTTP_200_OK,
    summary="Synchronous evaluation fallback",
)
async def evaluate_sync(
    session_id: str,
    request: EvaluationRequest,
    user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
) -> EvaluationResult:
    """Synchronous evaluation fallback returning complete result."""
    session = session_store.get_session(session_id)
    if not session:
        raise SessionNotFoundError(session_id=session_id)

    user_id = user["uid"] if user else None
    result = llm_service.evaluate_sync(request, session, user_id=user_id)
    session_store.save_result(result, session, user_id=user_id)
    return result
