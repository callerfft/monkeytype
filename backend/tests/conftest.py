"""Test configuration and fixtures."""

import os
import sys
from pathlib import Path
from typing import AsyncGenerator, Dict

import pytest
import pytest_asyncio
import httpx
from httpx import ASGITransport

# Ensure backend root is in python path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

if sys.platform == "win32":
    # Windows Python 3.14 ProactorEventLoop self-pipe uses socket.socketpair() which fails
    # with WinError 10013 in sandboxed/restricted network environments.
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

from app.main import app
from app.config import settings


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Async HTTP client targeting the in-process FastAPI ASGI application."""
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.fixture
def auth_headers() -> Dict[str, str]:
    """Mock Bearer token headers for authenticated endpoints."""
    return {"Authorization": "Bearer mock-test-token-456"}


@pytest.fixture
def contract_path() -> Path:
    """Path to OpenAPI 3.1.0 contract file."""
    # Check root workspace contracts/api_v1.json
    root_contract = backend_dir.parent / "contracts" / "api_v1.json"
    if root_contract.exists():
        return root_contract
    # Fallback to survey contract
    survey_contract = backend_dir.parent / ".agents" / "teamwork" / "spec_miner_survey_1" / "api_v1.json"
    return survey_contract
