"""LinguaType FastAPI backend application entrypoint."""

import sys
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

if sys.platform == "win32":
    try:
        from asyncio.proactor_events import BaseProactorEventLoop

        class _DummySocket:
            def fileno(self): return -1
            def setblocking(self, _flag): pass
            def send(self, data): return len(data)
            def close(self): pass

        BaseProactorEventLoop._make_self_pipe = lambda self: (
            setattr(self, "_ssock", _DummySocket()),
            setattr(self, "_csock", _DummySocket()),
            setattr(self, "_internal_fds", getattr(self, "_internal_fds", 0) + 1),
        )
        BaseProactorEventLoop._loop_self_reading = lambda self, f=None: None
        BaseProactorEventLoop._close_self_pipe = lambda self: (
            setattr(self, "_ssock", None),
            setattr(self, "_csock", None),
            setattr(self, "_internal_fds", getattr(self, "_internal_fds", 1) - 1),
        )
    except Exception:
        pass

from .config import settings
from .core.security import setup_cors
from .core.exceptions import (
    AppException,
    app_exception_handler,
    validation_exception_handler,
    http_exception_handler,
)
from .api.router import api_router


def create_app() -> FastAPI:
    """Factory creating configured FastAPI instance matching api_v1.json contract."""
    app = FastAPI(
        title="LinguaType API",
        version=settings.VERSION,
        description="API for LinguaType: low-latency, gamified translation and sentence construction trainer with streaming LLM evaluation (<3s SLA).",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Setup Cross-Origin Resource Sharing
    setup_cors(app)

    # Register standardized exception handlers
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)

    # Include API routes under /api/v1
    app.include_router(api_router, prefix=settings.API_V1_STR)

    @app.get("/", tags=["Health & Benchmarking"])
    async def root():
        """Root endpoint returning service identity."""
        return {
            "name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "status": "online",
            "docs": "/docs",
        }

    return app


app = create_app()
