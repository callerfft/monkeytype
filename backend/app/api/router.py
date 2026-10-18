"""Main API router combining v1 routes."""

from fastapi import APIRouter
from .v1 import (
    sessions_router,
    evaluation_router,
    user_router,
    prompts_router,
    health_router,
    benchmark_router,
)

api_router = APIRouter()

# Register all v1 routers
api_router.include_router(sessions_router)
api_router.include_router(evaluation_router)
api_router.include_router(user_router)
api_router.include_router(prompts_router)
api_router.include_router(health_router)
api_router.include_router(benchmark_router)
