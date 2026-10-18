# Project: LinguaType

## Architecture
LinguaType is a fast keyboard-driven translation and sentence-construction trainer built on Monkeytype with streaming LLM evaluation (<3.0s latency SLA).

```
┌─────────────────────────────────────────────────────────────────┐
│                    Monkeytype Web Client                        │
│             (SolidJS + Vite + Tailwind v4 CSS)                  │
│                                                                 │
│  ┌────────────────────────┐      ┌───────────────────────────┐  │
│  │ LinguaTypePage (/linguatype) │  │ Firebase Auth (v12)       │  │
│  │  - Mode A (Translation)│      │  - Google OAuth           │  │
│  │  - Mode B (Situation)  │      │  - Magic Link             │  │
│  │  - Keyboard (Tab+Enter)│      │  - Bearer Token Provider  │  │
│  │  - ARIA Live Regions   │      └─────────────┬─────────────┘  │
│  │  - Minimalist UI       │                    │                │
│  └───────────┬────────────┘                    │                │
└──────────────┼─────────────────────────────────┼────────────────┘
               │                                 │
     HTTP SSE  │ POST /api/v1/...                │ Bearer JWT
               ▼                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LinguaType Backend                           │
│               (Python 3.14 + FastAPI + Uvicorn)                 │
│                                                                 │
│  ┌───────────────────────┐       ┌───────────────────────────┐  │
│  │ API Routers (/api/v1) │       │ Core Security & Auth      │  │
│  │  - /sessions          │       │  - Google JWKS / Mock Auth│  │
│  │  - /evaluate (SSE)    │       │  - CORS & Rate Limiting   │  │
│  │  - /user/profile      │       └───────────────────────────┘  │
│  │  - /benchmark/latency │                                      │
│  └───────────┬───────────┘                                      │
│              │                                                  │
│  ┌───────────▼───────────┐       ┌───────────────────────────┐  │
│  │ LLM Inference Service │──────▶│ Gemini 1.5 Flash          │  │
│  │  - Streaming REST     │       │ (or MockStreamingService) │  │
│  │  - TTFT < 800ms       │       │ - Error Spans             │  │
│  │  - Strict JSON Events │       │ - Semantic Check          │  │
│  │                       │       │ - 1 Style Alternative     │  │
│  └───────────────────────┘       └───────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | API Contract Definition | Formal OpenAPI 3.1.0 / JSON Schema contract covering all endpoints, SSE formats, and schemas | M1 | survey/R1 |
| 2 | Mode A Session Creation | Initialize Russian -> English translation session with 15/30/60s timer and word count budget | M2 | survey/R1 |
| 3 | Mode B Session Creation | Initialize situation/image description session in target language | M2 | survey/R1 |
| 4 | Session Retrieval | Retrieve session state, prompt details, and expiration status by UUID | M2 | survey/R1 |
| 5 | Session Constraints | Enforce 15/30/60s timers and calculate max word count budget (target + buffer) | M2 | survey/R1 |
| 6 | Real-time SSE Evaluation | Progressive Server-Sent Events stream emitting tokens, errors, semantic check, style, and metrics | M2 | survey/R2 |
| 7 | Grammar Error Spans | Extract 0-based character offsets (`start`, `end`), error message, suggestion, category, severity | M2 | survey/R2 |
| 8 | Semantic Match Check | Validate core concept coverage, allow loose phrasing, score 0-100, identify missing concepts | M2 | survey/R2 |
| 9 | Single Style Alternative | Generate strictly ONE stylistic rewrite matching selected style (academic, business, casual, etc.) | M2 | survey/R2 |
| 10 | Typing Metrics | Calculate WPM, accuracy score, duration in ms, and target-met flag | M2 | survey/R2 |
| 11 | Latency Telemetry | Measure TTFT (<800ms) and total inference (<2500ms) with breakdown in evaluation events | M2 | survey/R2 |
| 12 | Sync Evaluation Fallback | Synchronous REST endpoint `POST /api/v1/sessions/{id}/evaluate/sync` for testing/fallback | M2 | survey/R2 |
| 13 | Latency Benchmark Endpoint | Automated synthetic latency benchmark `POST /api/v1/benchmark/latency` asserting <2.5s / <3.0s | M2 | survey/R2 |
| 14 | Curated Prompt Catalog | Prompt service providing curated prompts for Mode A and Mode B | M2 | survey/R2 |
| 15 | SolidJS LinguaType Shell | Dedicated SolidJS page `/linguatype` in `frontend/src/ts/components/pages/linguatype/` | M3 | survey/R3 |
| 16 | Mode A & B Gameplay UI | Input area, live word count progress, countdown timer, prompt card | M3 | survey/R3 |
| 17 | Streaming Feedback Display | Real-time rendering of LLM feedback card with inline error span highlighting and style suggestion | M3 | survey/R3 |
| 18 | Keyboard Controls & A11y | `Tab+Enter` restart, `Esc` reset, focus retention, `aria-live="polite"`, `aria-invalid` | M3 | survey/R3 |
| 19 | Minimalist Dark Theme | Clean Monkeytype design tokens, zero decorative stickers, no UI clutter | M3 | survey/R3 |
| 20 | Firebase Auth & Settings | Google OAuth + Magic Link, user profile preferences, session history retrieval, JWT Bearer | M4 | survey/R4 |
| 21 | Firebase App Hosting Config | `apphosting.yaml` with Cloud Run configuration (`minInstances: 1`, `cpu: 1`, `memoryMiB: 1024`) | M4 | survey/R5 |
| 22 | Sequential E2E Verification | End-to-end integration tests, latency SLA verification (<3.0s), `pytest`, `vitest`, `oxlint` | M5 | survey/R5 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | M1: API Contract Definition | Place and validate `contracts/api_v1.json` (OpenAPI 3.1.0) | None | DONE |
| 2 | M2: Backend FastAPI Service | Implement `backend/app/` (FastAPI, SSE streaming, Gemini/Mock LLM, error spans, style alternative, latency benchmark, pytest) | M1 | DONE |
| 3 | M3: Frontend LinguaType Core | Implement `frontend/src/ts/components/pages/linguatype/` (SolidJS, Mode A/B, keyboard hotkeys, a11y, minimalist UI) | M1 | DONE |
| 4 | M4: Auth & App Hosting | Implement Firebase Auth (Google OAuth + Magic Link), user profile/history API, and `apphosting.yaml` | M2, M3 | DONE |
| 5 | M5: Integration & Verification | Sequential E2E integration, latency benchmarking (<3.0s), full test suite (`pytest`, `vitest run`, `oxlint`) | M2, M3, M4 | DONE |

## Interface Contracts
### Frontend (`frontend/src/ts/queries/linguatype-api.ts`) ↔ Backend (`backend/app/api/v1/`)
- **Contract Source of Truth**: `contracts/api_v1.json`
- **Session Create**: `POST /api/v1/sessions` -> Body: `SessionCreateRequest` -> Response: `SessionResponse`
- **Session Get**: `GET /api/v1/sessions/{session_id}` -> Response: `SessionResponse`
- **Streaming Evaluation**: `POST /api/v1/sessions/{session_id}/evaluate` -> Accept: `text/event-stream` -> Events:
  - `session_start`: `{"session_id": "...", "status": "active"}`
  - `token`: `{"text": "..."}`
  - `grammar_errors`: `[{"start": int, "end": int, "original_text": "...", "message": "...", "suggestion": "...", "category": "grammar"|"spelling"|"syntax", "severity": "error"|"warning"}]`
  - `semantic_check`: `{"is_valid": bool, "score": float, "explanation": "...", "missing_concepts": []}`
  - `style_alternative`: `{"style": "...", "text": "...", "explanation": "..."}` (strictly ONE alternative)
  - `metrics`: `{"wpm": float, "accuracy_score": float, "time_spent_ms": int, "word_count": int, "target_met": bool}`
  - `done`: `{"evaluation_id": "...", "latency": {"ttft_ms": int, "inference_duration_ms": int, "pipeline_duration_ms": int}}`
  - `error`: `{"code": "...", "message": "..."}`
- **Sync Fallback**: `POST /api/v1/sessions/{session_id}/evaluate/sync` -> Response: `EvaluationResult`
- **User Profile**: `GET /api/v1/user/profile`, `PUT /api/v1/user/profile` (Requires Bearer token)
- **User History**: `GET /api/v1/results` (Requires Bearer token)
- **Latency Benchmark**: `POST /api/v1/benchmark/latency` -> Response: `LatencyBenchmarkResponse` (`meets_constraint: bool`)

## Code Layout
- `contracts/api_v1.json`: Formal API specification
- `backend/`:
  - `backend/app/main.py`: FastAPI application entrypoint
  - `backend/app/config.py`: Pydantic settings & environment configuration
  - `backend/app/api/v1/`: Endpoints (sessions, evaluation, user, prompts, health, benchmark)
  - `backend/app/core/`: Security, Firebase JWT validation, exceptions
  - `backend/app/models/`: Pydantic schemas corresponding to `contracts/api_v1.json`
  - `backend/app/services/`: LLM client (Gemini Flash + MockStreamingService), prompt catalog, session store
  - `backend/app/utils/`: SSE generator, latency timer
  - `backend/tests/`: Automated pytest suite (contract tests, session tests, stream tests, latency tests)
  - `backend/pyproject.toml`, `backend/requirements.txt`
- `frontend/`:
  - `frontend/src/ts/components/pages/linguatype/`: SolidJS LinguaType page and components
  - `frontend/src/ts/states/linguatype.ts`: Reactive state management
  - `frontend/src/ts/queries/linguatype-api.ts`: SSE stream consumer and REST client
  - `frontend/src/ts/input/hotkeys/linguatype.ts`: Keyboard event handlers (Tab+Enter, Esc)
  - `frontend/src/ts/firebase.ts`: Enhanced Firebase Auth (Google OAuth + Magic Link)
  - `frontend/src/ts/components/pages/page-registry.ts`: Route registration
  - `frontend/src/ts/controllers/route-controller.ts`: URL routing (`/linguatype`)
  - `frontend/src/ts/components/layout/header/Nav.tsx`: Header navigation icon
- Root:
  - `apphosting.yaml`: Firebase App Hosting configuration
