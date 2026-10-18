"""Service health check router."""

from fastapi import APIRouter, status
from ...models.health import HealthStatus
from ...services.llm_service import llm_service
from ...config import settings

router = APIRouter(prefix="/health", tags=["Health & Benchmarking"])


@router.get(
    "",
    response_model=HealthStatus,
    status_code=status.HTTP_200_OK,
    summary="Service health check",
)
async def health_check() -> HealthStatus:
    """Return health status and LLM connectivity."""
    connected = await llm_service.is_connected()
    return HealthStatus(
        status="ok" if connected else "degraded",
        service="linguatype-backend",
        version=settings.VERSION,
        llm_connected=connected,
        llm_provider=f"google-{settings.GEMINI_MODEL}" if settings.LLM_PROVIDER == "gemini" else "mock-llm-service",
    )
