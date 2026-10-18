# Handoff Report: Explorer 2 — Backend, Environment & Infrastructure Survey

## 1. Observation

### 1.1 Python Environment & Tooling
- **Python Version**: CPython 3.14.3 (Windows x64).
  - Executable: `C:\Users\Yohanson\AppData\Local\Programs\Python\Python314\python.exe`
  - Command: `python --version` -> `Python 3.14.3`
- **Package Managers**:
  - `uv`: version 0.10.7 at `C:\Users\Yohanson\.local\bin\uv.exe`
  - `pip`: version 26.1 at `C:\Users\Yohanson\AppData\Local\Programs\Python\Python314\Scripts\pip.exe`
- **Test Runner**:
  - `pytest`: version 9.0.3 at `C:\Users\Yohanson\AppData\Local\Programs\Python\Python314\Scripts\pytest.exe`
  - `pytest-asyncio`: version 1.4.0 installed in site-packages.
- **Installed Key Dependencies (verified via `python -c "import ..."` & `pip list`)**:
  - `fastapi`: 0.136.3
  - `uvicorn`: 0.48.0
  - `pydantic`: 2.13.3
  - `pydantic-settings`: 2.13.1
  - `pydantic_core`: 2.46.3
  - `starlette`: 1.2.1
  - `httpx`: 0.28.1
  - `PyJWT`: 2.12.1
  - `cryptography`: 46.0.5
  - `python-jose`: 3.5.0
  - `python-dotenv`: 1.2.2
  - `python-multipart`: 0.0.27
  - `anyio`: 3.7.1
  - `aiohttp`: 3.13.3
  - `aiofiles`: 25.1.0
  - `websockets`: 14.2

### 1.2 Network Environment & Package Resolution
- Running `uv pip install --system --dry-run sse-starlette` produced verbatim error:
  ```
  error: Request failed after 3 retries
    Caused by: Failed to fetch: `https://pypi.org/simple/sse-starlette/`
    Caused by: error sending request for url (https://pypi.org/simple/sse-starlette/)
    Caused by: client error (Connect)
    Caused by: dns error
    Caused by: Этот хост неизвестен. (os error 11001)
  ```
- Uninstalled target packages: `google-genai` / `google-generativeai`, `sse-starlette`, `firebase-admin` are not currently in the Python 3.14 environment, and DNS resolution to `pypi.org` fails (isolated/offline sandbox environment).

### 1.3 Repository & Existing Backend Structure
- Directory `c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\backend` exists.
- Current contents: Monkeytype's legacy Node.js/Express backend (`@monkeytype/backend` v1.14.3, `package.json`, `tsconfig.json`, `src/app.ts`, `src/server.ts`, `__tests__/`).
- Root `package.json` contains scripts `lint-be`, `build-be`, `test-be`, and `pnpm-workspace.yaml` contains `- backend`.
- There are currently 0 Python files (`*.py`) in `c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype`.

### 1.4 API Contract Alignment
- `spec_miner_survey_1` produced `c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\spec_miner_survey_1\api_v1.json` (OpenAPI 3.1.0):
  - `POST /api/v1/sessions`: Create game session (Mode A translation / Mode B situation_image, timer: 15s/30s/60s/null, word limits).
  - `GET /api/v1/sessions/{session_id}`: Retrieve session state and prompt.
  - `POST /api/v1/sessions/{session_id}/evaluate`: Streaming evaluation via SSE (`text/event-stream`). Emits events: `session_start`, `token`, `grammar_errors`, `semantic_check`, `style_alternative`, `metrics`, `done`, `error`.
  - `POST /api/v1/sessions/{session_id}/evaluate/sync`: Synchronous fallback returning `EvaluationResult`.
  - `GET /api/v1/user/profile`, `PUT /api/v1/user/profile`: User preferences and style settings.
  - `GET /api/v1/results`: Historical game results.
  - `GET /api/v1/prompts`: Curated prompt catalog.
  - `GET /api/v1/health`: Health status.
  - `POST /api/v1/benchmark/latency`: Latency benchmark endpoint validating SLA targets.
  - Security scheme: `FirebaseAuth` (HTTP Bearer JWT).

### 1.5 Firebase & App Hosting Configuration
- Existing `frontend/firebase.json` is configured for classic static hosting (`dist`).
- Firebase App Hosting documentation (`firebase_app_hosting_basics/references/configuration.md`) specifies `apphosting.yaml` format with `runConfig` (`cpu`, `memoryMiB`, `minInstances`, `maxInstances`, `concurrency`) and `env` secret management.

---

## 2. Logic Chain

1. **Self-Contained Dependency Strategy**:
   - Because PyPI is unreachable due to DNS error 11001 (Observation 1.2), the backend implementation must strictly rely on libraries already installed (Observation 1.1) or Python standard library.
   - For SSE streaming: `sse-starlette` is not installed, but `starlette.responses.StreamingResponse` is pre-installed (`starlette 1.2.1` / `fastapi 0.136.3`). A native SSE generator yielding `f"event: {event}\ndata: {json.dumps(payload)}\n\n"` with `media_type="text/event-stream"` is 100% compliant with standard SSE and requires zero additional dependencies.
   - For Gemini Flash: Instead of the uninstalled `google-genai` SDK, the backend will use `httpx.AsyncClient` (installed: `httpx 0.28.1`) to stream from Google's REST API (`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:streamGenerateContent?alt=sse&key=...`). Furthermore, an asynchronous `MockGeminiService` must be included for offline execution and automated test isolation.
   - For Firebase Auth: Instead of `firebase-admin`, token verification is natively performed using `PyJWT 2.12.1` and `cryptography 46.0.5` against Google Identity JWKS (`https://www.googleapis.com/service_accounts/v1/jwk/securetoken@system.gserviceaccount.com`), with an in-memory key cache and a development mock mode (`AUTH_MODE=mock|firebase`).

2. **Latency Budget & Benchmarking Methodology**:
   - Original requirements mandate TTFT & inference < 2.5s, end-to-end pipeline < 3.0s.
   - Using `pytest-asyncio` and `httpx.AsyncClient(transport=ASGITransport(app=app))`, tests can execute in-process requests without opening external network sockets.
   - High-resolution timing (`time.perf_counter()`) records:
     - `TTFT`: time to receipt of first `data:` or `token` SSE chunk (< 800ms target, < 2.5s ceiling).
     - `Inference Latency`: duration until receipt of `event: done` chunk (< 2.5s).
     - `Pipeline Latency`: total duration of request processing (< 3.0s).
   - In `tests/test_latency_benchmark.py`, synthetic test scenarios will assert these SLA bounds deterministically.

3. **Backend Coexistence & Directory Architecture**:
   - The user request explicitly demands `backend/` (Python/FastAPI) and automated tests with `pytest` (Observation 1.3).
   - Placing Python source in `backend/app/` and tests in `backend/tests/` prevents clashing with existing TypeScript files in `backend/src/` and `backend/__tests__/`.
   - Adding `backend/pyproject.toml` and `backend/requirements.txt` establishes the Python package identity.
   - `backend/package.json` can be configured with `"test:py": "pytest tests"` to preserve integration with Turborepo (`turbo run test`).

4. **App Hosting Performance Tuning**:
   - Standard Cloud Run instances can incur cold starts of 2–4s, which would breach the < 3.0s latency SLA.
   - Setting `minInstances: 1` in `apphosting.yaml` keeps a minimum of 1 warm container running, ensuring instant request processing.

---

## 3. Caveats

1. **Offline Sandbox Limitation**: External PyPI downloads and live Google Gemini API calls are not reachable in the current sandbox environment without configured API keys and open internet routing. The system architecture must emphasize mock/local execution paths in all automated test suites.
2. **Dual-Backend Monorepo Coexistence**: The existing `@monkeytype/backend` Node.js package in `backend/` was inherited from upstream Monkeytype. If the project team chooses to retire the Node.js backend entirely, `backend/src/` can be archived or cleaned up; otherwise, `backend/app/` cleanly isolates all Python code.
3. **Firebase Token Verification Offline**: Without network access, fetching Google's public JWKS certificates is impossible. The auth service must support `AUTH_MODE=mock` for testing and local development, falling back to Google JWKS only in production environments.

---

## 4. Conclusion & Recommendations

### 4.1 Recommended Backend File Layout
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application initialization & middleware
│   ├── config.py                  # Pydantic BaseSettings (env, timeouts, auth mode)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── router.py              # Main API router (/api/v1)
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── sessions.py        # POST /api/v1/sessions, GET /api/v1/sessions/{id}
│   │       ├── evaluation.py      # POST /api/v1/sessions/{id}/evaluate (SSE) & /sync
│   │       ├── user.py            # GET /api/v1/user/profile, PUT /api/v1/user/profile
│   │       ├── prompts.py         # GET /api/v1/prompts
│   │       ├── health.py          # GET /api/v1/health
│   │       └── benchmark.py       # POST /api/v1/benchmark/latency
│   ├── core/
│   │   ├── __init__.py
│   │   ├── auth.py                # Firebase JWT verification (PyJWT) & mock auth
│   │   ├── security.py            # CORS & security headers
│   │   └── exceptions.py          # Global exception handlers
│   ├── models/
│   │   ├── __init__.py
│   │   ├── session.py             # SessionCreateRequest, SessionResponse
│   │   ├── evaluation.py          # EvaluationRequest, EvaluationResult, SSEStreamEvent
│   │   ├── grammar.py             # GrammarErrorSpan, SemanticValidation, StyleAlternative
│   │   ├── user.py                # UserProfile, UserProfileUpdate, HistoryListResponse
│   │   └── prompt.py              # Prompt schema & difficulty enums
│   ├── services/
│   │   ├── __init__.py
│   │   ├── prompt_store.py        # Curated prompts for Mode A & Mode B
│   │   ├── session_store.py       # In-memory session state management
│   │   ├── llm_service.py         # Gemini Flash REST client (via httpx)
│   │   └── mock_llm_service.py    # Deterministic streaming mock for tests (<500ms)
│   └── utils/
│       ├── __init__.py
│       ├── sse.py                 # Starlette SSE event generator
│       └── latency.py             # High-resolution benchmark timers
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Fixtures: async client, test sessions, mock auth
│   ├── test_contract.py           # Validates Pydantic models vs contracts/api_v1.json
│   ├── test_sessions.py           # Session creation & constraint validation
│   ├── test_evaluation_stream.py  # SSE stream formatting and event sequence tests
│   ├── test_evaluation_sync.py    # Synchronous evaluation tests
│   ├── test_auth.py               # Token verification & unauthorized access tests
│   ├── test_prompts.py            # Mode A & Mode B catalog retrieval
│   └── test_latency_benchmark.py  # Automated latency SLA assertions (<2.5s / <3.0s)
├── pyproject.toml                 # Tooling configuration (pytest, coverage)
├── requirements.txt               # Documented dependencies
├── apphosting.yaml                # Firebase App Hosting / Cloud Run configuration
└── run.py                         # Local server runner (python run.py)
```

### 4.2 Recommended `apphosting.yaml`
```yaml
# apphosting.yaml
runConfig:
  cpu: 1
  memoryMiB: 512
  minInstances: 1 # Pre-warmed to prevent 2-4s cold start latency violations
  maxInstances: 10
  concurrency: 80

env:
  - variable: GEMINI_API_KEY
    secret: geminiApiKey
    availability:
      - RUNTIME
  - variable: FIREBASE_PROJECT_ID
    value: linguatype-prod
    availability:
      - BUILD
      - RUNTIME
  - variable: AUTH_MODE
    value: firebase
    availability:
      - RUNTIME
```

### 4.3 Input for `PROJECT.md` Backend Milestones
- **Milestone B1: Core API & Contract Models**:
  Implement `backend/app/models/` mirroring `contracts/api_v1.json`, configure FastAPI application with CORS and route handlers.
- **Milestone B2: Session & Prompt Catalog Engine**:
  Implement `backend/app/services/session_store.py` and `prompt_store.py` supporting Mode A (translation) and Mode B (situation) with timer (15s/30s/60s) and word count constraints.
- **Milestone B3: Low-Latency Streaming Evaluation & LLM Service**:
  Implement `backend/app/services/llm_service.py` and `backend/app/utils/sse.py` with progressive SSE delivery (`token`, `grammar_errors`, `semantic_check`, `style_alternative`, `done`).
- **Milestone B4: Firebase Auth Integration**:
  Implement `backend/app/core/auth.py` supporting Bearer ID token validation with cached Google JWKS keys and `AUTH_MODE=mock` for testing.
- **Milestone B5: Automated Latency Benchmarking & Health**:
  Implement `POST /api/v1/benchmark/latency` and `backend/tests/test_latency_benchmark.py` validating TTFT < 800ms, total inference < 2.5s, and pipeline < 3.0s.

---

## 5. Verification Method

To independently verify the findings in this report:

1. **Verify Python & Tooling**:
   ```powershell
   python --version
   python -m pip list
   python -m pytest --version
   ```
   *Expected*: Python 3.14.3, pytest 9.0.3, fastapi 0.136.3, pydantic 2.13.3, uvicorn 0.48.0, PyJWT 2.12.1.

2. **Verify Native Starlette SSE & Package Imports**:
   ```powershell
   python -c "from starlette.responses import StreamingResponse; import fastapi, pydantic, httpx, jwt, cryptography; print('ALL CORE DEPS VERIFIED')"
   ```
   *Expected*: `ALL CORE DEPS VERIFIED` output with exit code 0.

3. **Verify Pytest Execution Capability**:
   ```powershell
   python -m pytest -c /dev/null -q --collect-only
   ```
   *Expected*: Pytest launches cleanly without configuration or plugin errors.

4. **Verify Contract File Presence**:
   Inspect `c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\spec_miner_survey_1\api_v1.json`.
   *Expected*: Valid OpenAPI 3.1.0 document defining `/api/v1/sessions`, `/api/v1/sessions/{session_id}/evaluate`, and `/api/v1/benchmark/latency`.
