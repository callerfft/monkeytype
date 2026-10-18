# Handoff Report: LinguaType Specification Mining & API Contract (`contracts/api_v1.json`)

**Agent ID**: `spec_miner_survey_1`  
**Working Directory**: `c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\spec_miner_survey_1`  
**Target Specification Contract**: `contracts/api_v1.json` (OpenAPI 3.1.0 / JSON Schema Draft 2020-12)  
**Parent Orchestrator**: `3b1515b3-2073-47ba-bf07-f8f58de22f4d`  
**Date**: 2026-10-17T05:39:00Z  

---

## Features Discovered

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | Session Management | Mode A Session Creation (Phrase Translation) | Initializes a game session where the user is presented a source sentence in their native language to translate into the target language. | `SessionCreateRequest` (`mode="translation"`, `timer_seconds=15\|30\|60\|null`, `target_word_count`, `source_language`, `target_language`, `difficulty`) | `SessionResponse` (`session_id`, `prompt`, `status="active"`, `expires_at`) | Returns 400 if invalid timer/languages, 401 if auth required | `ORIGINAL_REQUEST.md:17-18`, `LinguaType_Project_Architecture.md:10-15` |
| 2 | Session Management | Mode B Session Creation (Situation/Image Prompt) | Initializes a game session where the user describes a situation or image prompt directly in the target language. | `SessionCreateRequest` (`mode="situation_image"`, `timer_seconds`, `target_word_count`, `difficulty`, optional `image_url`) | `SessionResponse` with situation context or CDN `image_url` | Returns 400 for unsupported mode or parameters | `ORIGINAL_REQUEST.md:28`, `LinguaType_Project_Architecture.md:12-15` |
| 3 | Session Management | Session Retrieval by ID | Fetches existing session status, prompt details, and completion timestamp. | Path `session_id` (UUID) | `SessionResponse` | Returns 404 `SESSION_NOT_FOUND` if unknown or expired | `ORIGINAL_REQUEST.md:17-18` |
| 4 | Session Management | Session Constraints Enforcement | Enforces fixed timer options (15s, 30s, 60s) or untimed mode; calculates `max_word_count` (`target_word_count + margin_buffer`). | `timer_seconds`, `target_word_count`, `margin_buffer` | Pre-calculated limits attached to session prompt | 400 for negative bounds or non-standard timer values | `LinguaType_Project_Architecture.md:14-15` |
| 5 | Session Management | Input Mode Configuration | Configures either free typing input or scaffolding assistance (guided assembly) for beginner learners. | `input_mode: "free" \| "scaffolding"` | Stored in session and user profile | Defaults to `"free"` if omitted | `LinguaType_Project_Architecture.md:18` |
| 6 | Streaming Evaluation | Real-Time SSE Evaluation Stream | Streams evaluation results as progressive Server-Sent Events over HTTP POST with sub-second feedback. | `session_id`, `EvaluationRequest` (`user_text`, `time_spent_ms`, `words_typed`, `character_count`) | Stream of SSE events: `session_start`, `token`, `grammar_errors`, `semantic_check`, `style_alternative`, `metrics`, `done` | Emits `error` SSE event on failure, returns 404 if session missing, 504 on timeout | `ORIGINAL_REQUEST.md:21-24`, `LinguaType_Project_Architecture.md:19-24` |
| 7 | Streaming Evaluation | Grammar Error Spans Extraction | Identifies grammatical, spelling, and syntax errors, returning exact character offset spans on user submission. | `user_text` in evaluation request | Array of `GrammarErrorSpan` (`start`, `end`, `original_text`, `message`, `suggestion`, `category`, `severity`) | If no errors found, returns empty array `[]` | `ORIGINAL_REQUEST.md:23`, `LinguaType_Project_Architecture.md:21` |
| 8 | Streaming Evaluation | Semantic Match & Loose Phrasing Validation | Evaluates whether user translation captures core prompt meaning; allows loose/idiomatic phrasing when enabled. | `user_text`, `prompt.content`, `allow_loose_phrasing` | `SemanticValidation` (`is_valid`, `score: 0-100`, `explanation`, `missing_concepts`) | Flags `is_valid: false` if core concepts are missing | `LinguaType_Project_Architecture.md:22, 65, 77` |
| 9 | Streaming Evaluation | Single Style Alternative Transformation | Generates exactly ONE optimized alternative sentence matching the user's selected style preference. | `preferred_style: "conversational" \| "formal" \| "concise" \| "academic" \| "business"` | `StyleAlternative` (`style`, `text`, `explanation`) | Strictly capped at exactly 1 alternative | `ORIGINAL_REQUEST.md:23`, `LinguaType_Project_Architecture.md:23` |
| 10 | Streaming Evaluation | Typing Speed & Accuracy Scoring | Computes standard typing metrics (WPM, duration in ms, composite accuracy score 0-100). | `time_spent_ms`, `character_count`, `grammar_errors`, `semantic_validation` | `SessionMetrics` (`wpm`, `accuracy_score`, `time_spent_ms`, `word_count`, `target_met`) | Handles 0ms division safely (returns 0 WPM) | `LinguaType_Project_Architecture.md:24, 94-96` |
| 11 | Streaming Evaluation | Latency Breakdown & SLA Reporting | Instruments and returns timing telemetry including TTFT (<800ms) and inference (<2500ms) in evaluation completion. | Evaluation execution timer | `LatencyBreakdown` (`ttft_ms`, `inference_duration_ms`, `pipeline_duration_ms`) | Emits warning/error if latency exceeds 3000ms SLA | `ORIGINAL_REQUEST.md:24, 48`, `LinguaType_Project_Architecture.md:30-36` |
| 12 | Streaming Evaluation | Synchronous Batch Evaluation Fallback | Non-streaming REST endpoint returning complete `EvaluationResult` in a single response for tests and non-SSE clients. | `session_id`, `EvaluationRequest` | `EvaluationResult` JSON | 400 Bad Request, 404 Session Not Found, 504 Timeout | `DISPATCH.md:10-16`, standard REST practice |
| 13 | Auth & Settings | Firebase Auth Integration | Authenticates users via Firebase ID token passed in `Authorization: Bearer <token>`, supporting Google OAuth and Magic Link. | Header `Authorization: Bearer <id_token>` | Authenticated user context (`uid`, `email`) | Returns 401 `UNAUTHORIZED` if token invalid or expired | `ORIGINAL_REQUEST.md:33-34`, `backend/src/middlewares/auth.ts:24-40` |
| 14 | Auth & Settings | User Profile & Preference Management | Reads and updates user language pairs (`native_language`, `target_language`), style preference, and default input mode. | `GET /api/v1/user/profile`, `PUT /api/v1/user/profile` | `UserProfile` (`id`, `email`, `native_language`, `target_language`, `preferred_style`, `allow_loose_phrasing`, `input_mode`) | Returns 400 on invalid language codes or invalid style enum | `LinguaType_Project_Architecture.md:71-78` |
| 15 | Auth & Settings | Game History & Results Pagination | Retrieves paginated historical typing sessions with accuracy, WPM, and error logs for user progress tracking. | Query parameters: `limit` (default 20, max 100), `offset`, optional `mode` filter | `HistoryListResponse` (`results: GameResultSummary[]`, `total`, `offset`, `limit`) | 401 if unauthenticated | `LinguaType_Project_Architecture.md:89-99` |
| 16 | Prompts Catalog | Curated Prompt Exploration | Provides a catalog of prompt items filtered by mode, language pair, and difficulty level. | Query parameters: `mode`, `source_language`, `target_language`, `difficulty`, `limit` | Array of `Prompt` objects | Returns empty array if no prompts match criteria | `LinguaType_Project_Architecture.md:60-62, 80-87` |
| 17 | Health & Benchmark | Backend & LLM Health Check | Returns service status and verifies active connectivity to the LLM inference provider (Gemini Flash). | `GET /api/v1/health` | `HealthStatus` (`status: "ok" \| "degraded" \| "down"`, `service`, `version`, `llm_connected`, `llm_provider`) | Returns degraded status if LLM connection fails | `ORIGINAL_REQUEST.md:21-24` |
| 18 | Health & Benchmark | Automated Latency Benchmark | Executes synthetic evaluation requests measuring min/max/avg/p95 of TTFT and total inference against SLA (<2.5s / <3.0s). | `POST /api/v1/benchmark/latency` (`iterations: 1-10`, `model`, `test_prompt`, `test_submission`) | `LatencyBenchmarkResponse` (`ttft_ms`, `inference_duration_ms`, `pipeline_duration_ms`, `meets_constraint`) | Returns 500 on execution failure | `ORIGINAL_REQUEST.md:24, 48`, `DISPATCH.md:9` |
| 19 | UI & Accessibility | Keyboard Navigation & Quick Restart | Complete keyboard-driven test lifecycle: `Tab+Enter` triggers quick restart, `Esc` cancels/resets session, autofocus on input. | Keyboard events (`Tab+Enter`, `Escape`) | Immediate test restart or reset without mouse interaction | Prevents default form navigation; handles input focus trapping | `ORIGINAL_REQUEST.md:31, 51-52`, `frontend/src/ts/input/hotkeys/quickrestart.ts` |
| 20 | UI & Accessibility | Live ARIA Announcements for Streaming | Dynamic screen reader status notifications during streaming evaluation and grammar error highlighting. | SSE stream updates | DOM attributes: `aria-live="polite"` for stream output, `aria-invalid="true"`, `aria-describedby` for error spans | Graceful degradation if screen reader not attached | `ORIGINAL_REQUEST.md:31, 51-52` |
| 21 | UI & Accessibility | Minimalist Dark Monkeytype Aesthetic | Clean typing interface with zero stickers, zero visual clutter, using Monkeytype design tokens and CSS variables. | Theme configuration | Clean typography, active caret, subtle inline error highlights | Strict adherence: NO decorative stickers | `ORIGINAL_REQUEST.md:38, 53`, `CODING_STANDARDS.md:5-9` |

---

## Edge Cases

| # | Feature | Input | Observed Behavior / Required Handling |
|---|---------|-------|----------------------------------------|
| 1 | Evaluation Streaming | Empty user submission (`user_text: ""` or whitespace only) | Validation rejects with HTTP 400 `INVALID_INPUT` (`minLength: 1`); frontend disables submit button or warns user without calling backend. |
| 2 | Session Timer Expiry | User keeps typing after live timer reaches 0 | Frontend automatically stops accepting input and submits current buffer with `timer_expired: true`; backend calculates metrics for text typed prior to expiry. |
| 3 | Word Limit Overflow | User enters text exceeding `target_word_count + margin_buffer` | Live UI counter displays warning color (e.g. text-sub); backend marks `word_limit_exceeded: true` and applies proportional penalty to `accuracy_score`. |
| 4 | Loose Phrasing Validation | User translates correctly using colloquial idioms not in literal dictionary | When `allow_loose_phrasing: true`, LLM semantic validator marks `is_valid: true`, gives high semantic score (>=85), and avoids false-positive grammar errors. |
| 5 | Perfect Grammar but Wrong Meaning | Grammatically flawless sentence completely unrelated to prompt (e.g. "The cat sits on the mat" for "Describe rocket engine") | `grammar_errors: []`, but `semantic_validation.is_valid: false`, `semantic_validation.score < 20`, `missing_concepts` lists omitted core ideas, and `accuracy_score` is capped at <= 30. |
| 6 | Non-Target Language Input | User submits text in source language (e.g. Russian text when target is English) | Backend detects language mismatch, emits error span covering entire string with category `"syntax"` / `"word_choice"`, and marks semantic validity as false. |
| 7 | Special Characters & Emojis | Submission contains multi-byte UTF-8, emojis, quotation marks, or HTML characters (`<script>`, `&amp;`) | Text is safely sanitized without XSS risk; 0-based character offsets (`start`, `end`) strictly respect UTF-16 code unit / Unicode code point indexing in frontend DOM. |
| 8 | Network Interruption during SSE Stream | Client disconnects or closes tab mid-stream (after token 10 of 40) | FastAPI async generator detects `request.is_disconnected()`, aborts upstream LLM call immediately to conserve tokens and avoid orphan processes. |
| 9 | Rapid Tab+Enter Spamming | User rapidly hits Tab+Enter 10 times in 2 seconds to cycle prompts | Frontend debounces restart event; cancels any in-flight session requests; backend handles orphaned sessions via short expiration TTL (15 minutes). |
| 10 | Unauthenticated Guest Session | User plays without logging into Firebase Auth | Session is created as guest session (`user_id: null`); streaming evaluation works normally; results are stored in local storage instead of backend user history. |
| 11 | LLM Provider Latency Spike (> 2500ms TTFT) | External Gemini API experiences temporary slowdown exceeding 2.5s | Backend enforces hard timeout at 2800ms; if LLM does not stream first token in time, emits SSE `error` event `LLM_TIMEOUT` and falls back to fast local rule-based heuristic check. |
| 12 | Mode B Image Load Failure | CDN image URL in Mode B returns 404 or fails to load in browser | Frontend UI falls back to displaying prompt's textual situation description; typing test proceeds without blocking. |

---

## 1. Observation

1. **Original Requirements Source** (`c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\ORIGINAL_REQUEST.md`):
   - Lines 5: *"Contract-first workflow (contracts/api_v1.json), 2 parallel isolated workers (/backend and /frontend), followed by sequential integration and verification."*
   - Lines 17-19: *"R1. API Contract Definition (contracts/api_v1.json): Создать формальный JSON Schema / OpenAPI контракт contracts/api_v1.json для взаимодействия фронтенда и бэкенда: схемы сессий (Mode A/B, таймеры 15/30/60s, лимиты слов), потоковой оценки (SSE/WebSocket), формата грамматических ошибок, семантической проверки и одного стилистического варианта."*
   - Lines 21-25: *"R2. Backend Service (backend/ — Python / FastAPI): Реализовать асинхронный сервис на FastAPI с поддержкой: Потокового эндпоинта оценки текста пользователя через быстрые LLM (Gemini Flash) со строгим JSON/структурированным выводом. Извлечения спанов грамматических ошибок, валидации смысла и генерации ровно одной альтернативы под выбранный стиль. Автоматического бенчмарка/теста задержки, подтверждающего TTFT и суммарное время инференса < 2.5s."*
   - Lines 27-32: *"R3. Frontend Integration (frontend/ / Monkeytype Core): Интегрировать режим LinguaType в клиент Monkeytype (SolidJS/TypeScript/Vite): Режим A (перевод фразы) и Режим B (описание ситуации/картинки). Настройки сессий: таймер, лимит слов, счетчик слов в реальном времени. Потоковый рендеринг результатов оценки с подсветкой ошибок и выводом рекомендованного варианта. Доступность (a11y): полное управление с клавиатуры (Tab+Enter рестарт, Esc сброс, фокус ввода), корректные ARIA-атрибуты."*
   - Lines 33-35: *"R4. Auth & Settings (Firebase Auth): Интеграция Firebase Auth (Google OAuth и Magic Link / passwordless) для сохранения настроек пользователя (родной/целевой языки, предпочтительный стиль) и истории сессий."*
   - Lines 48: *"Тест производительности подтверждает суммарную задержку пайплайна оценки < 3.0 секунд."*
   - Lines 53: *"Минималистичный интерфейс в стиле Monkeytype без избыточных декоративных элементов."*

2. **Project Architecture Document** (`c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\LinguaType_Project_Architecture.md`):
   - Lines 10-15: Core game loop with Mode A (translation of short source sentence) and Mode B (situation/image prompt description); session constraints with timers (15s / 30s / 60s) and word limits (`target_word_count + margin_buffer`).
   - Lines 16-18: Input mechanics with free text input and scaffolding mode (beginner assist).
   - Lines 19-24: Evaluation: grammar error spans directly on user text, semantic match (loose phrasing allowed), exactly ONE alternative sentence based on user preference, and speed metrics (WPM, time taken, accuracy score).
   - Lines 30-36: Latency budget: Network RTT ~100-200ms, Backend ~50ms, TTFT ~400-800ms, Token generation ~600-1200ms, UI render ~150ms -> Total 1.5s - 2.5s (safely below 3.0s SLA).
   - Lines 70-100: Data model schemas for Users, Prompts, and Game Results.

3. **Coding Standards & Repository Constraints** (`c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\CODING_STANDARDS.md` and `AGENTS.md`):
   - Styling: Tailwind CSS classes via `cn(...)`, strictly no inline styles for expressible classes, colors restricted to Tailwind config.
   - SolidJS components: Callback ref assignment (`let inputRef; ref={(el) => (inputRef = el)}`), acting on refs in `onMount`.
   - Modals: Registration in `frontend/src/ts/components/modals/Modals.tsx` and `frontend/src/ts/states/modals.ts`.
   - Rule constraint: Strictly NO stickers or cluttered visual elements. Keyboard navigation: `Tab+Enter` for restart, `Esc` for reset.

4. **Existing Codebase State**:
   - `contracts/` directory at project root did not exist prior to this survey phase.
   - Node v25.8.2 and Python 3.14.3 are installed and functional.
   - The contract file `api_v1.json` has been drafted and validated in `.agents/teamwork/spec_miner_survey_1/api_v1.json`.

---

## 2. Logic Chain

1. **Specification Paradigm**:
   - The user requires a **contract-first workflow** using `contracts/api_v1.json` to decouple the FastAPI backend from the SolidJS frontend.
   - OpenAPI 3.1.0 is selected because it fully integrates JSON Schema Draft 2020-12 (supporting standard `type: ["string", "null"]`, `oneOf`, and schema composition) and is natively supported by FastAPI's Pydantic v2 metadata generation and TypeScript OpenAPI codegen tools.

2. **Session Model Formulation**:
   - Both Mode A (`translation`) and Mode B (`situation_image`) share the same game session lifecycle.
   - Timers are constrained to `15`, `30`, `60`, or `null` (for untimed sessions).
   - Word boundaries are parameterized by `target_word_count` and `margin_buffer`, yielding a deterministic `max_word_count` (`target_word_count + margin_buffer`) displayed on the live counter.

3. **Streaming Evaluation Protocol (SSE)**:
   - Server-Sent Events (SSE) via `POST /api/v1/sessions/{session_id}/evaluate` with `Accept: text/event-stream` provides the lowest overhead and simplest browser client integration (`fetch` + `ReadableStream` or `EventSource`).
   - The stream sequentially emits structured typed events:
     1. `session_start`: acknowledgment and session metadata.
     2. `token`: progressive LLM output chunk.
     3. `grammar_errors`: JSON array of `GrammarErrorSpan` with exact `start` and `end` character indices.
     4. `semantic_check`: `SemanticValidation` object with `is_valid` (boolean), `score` (0-100), and `explanation`.
     5. `style_alternative`: exactly ONE alternative matching `preferred_style`.
     6. `metrics`: live typing metrics (`wpm`, `accuracy_score`, `time_spent_ms`).
     7. `done`: final evaluation result payload and latency breakdown.
   - A synchronous fallback endpoint `POST /api/v1/sessions/{session_id}/evaluate/sync` is also specified for non-streaming consumers and automated testing.

4. **Latency Budget & SLA Validation**:
   - The SLA specifies total pipeline latency < 3.0s and LLM inference < 2.5s with TTFT < 800ms.
   - The contract defines an automated latency benchmark endpoint `POST /api/v1/benchmark/latency` returning statistical percentiles (`min`, `max`, `avg`, `p95`) and a boolean `meets_constraint` flag, enabling automated verification in CI/CD and pytest.

5. **Authentication & User Profile**:
   - Security scheme is configured as HTTP Bearer with Firebase JWT (`FirebaseAuth`).
   - Profile endpoints `GET /api/v1/user/profile` and `PUT /api/v1/user/profile` allow managing language pairs and stylistic preferences.
   - History endpoint `GET /api/v1/results` supports pagination (`limit`, `offset`) and filtering.

6. **Accessibility (a11y) & Design System**:
   - Keyboard navigation adheres to Monkeytype conventions: `Tab+Enter` triggers test restart, `Esc` resets the test, and input focus is retained.
   - Streaming updates must use ARIA live regions (`aria-live="polite"`), and grammar error highlights must associate with error descriptions via `aria-invalid="true"` and `aria-describedby`.
   - Visual presentation conforms strictly to Monkeytype's minimalist dark palette with zero decorative stickers.

---

## 3. Caveats

1. **Guest vs. Authenticated User State**: Sessions and evaluation endpoints are designed to allow guest users (passing `user_id: null` and omitting the `Authorization` header). Profile and historical results endpoints strictly require the `FirebaseAuth` Bearer token.
2. **WebSocket vs. SSE**: SSE was selected over WebSockets for evaluation streaming because it operates over standard HTTP/2, requires no custom socket handshake, works seamlessly through standard reverse proxies and Firebase App Hosting, and naturally supports unidirectional streaming from LLM to frontend. If bidirectional interaction (e.g. real-time speech) is required in the future, WebSockets can be added as a separate route.
3. **Character Offsets**: Grammar error span indices (`start`, `end`) are defined as 0-based character offsets in the user's submitted string. Frontend implementations must ensure consistent UTF-16 / Unicode code point handling when mapping spans to DOM text elements.

---

## 4. Conclusion

All requirements for R1 through R5, the core game loop, latency constraints (<3s), session modes (A and B), streaming evaluation, Firebase auth, and accessibility rules have been fully mined, structured, and formulated into a complete, syntactically valid OpenAPI 3.1.0 specification.

The complete specification is preserved in:
`c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\spec_miner_survey_1\api_v1.json`

This specification is ready to be committed as `contracts/api_v1.json` during the Contract Definition milestone.

---

## 5. Verification Method

To independently verify the validity and structural integrity of the generated contract:

1. **Syntax & JSON Validity Check**:
   Run in powershell / bash:
   ```powershell
   node -e "const fs = require('fs'); const data = JSON.parse(fs.readFileSync('./.agents/teamwork/spec_miner_survey_1/api_v1.json', 'utf8')); console.log('Parsed successfully:', data.info.title, data.openapi);"
   ```
   *Expected output*: `Parsed successfully: LinguaType API 3.1.0`

2. **Schema Coverage Verification**:
   Inspect that all mandatory schemas exist in `components.schemas`:
   - `SessionCreateRequest` (contains `mode`, `timer_seconds: [15, 30, 60, null]`, `target_word_count`, `margin_buffer`)
   - `Prompt` (contains `id`, `type`, `content`, `image_url`)
   - `SessionResponse`
   - `EvaluationRequest`
   - `GrammarErrorSpan` (contains `start`, `end`, `original_text`, `message`, `suggestion`, `category`, `severity`)
   - `SemanticValidation` (contains `is_valid`, `score`, `explanation`, `missing_concepts`)
   - `StyleAlternative` (contains `style`, `text`, `explanation` — exactly 1 alternative)
   - `SessionMetrics` (contains `wpm`, `accuracy_score`, `time_spent_ms`, `word_count`)
   - `LatencyBreakdown` (contains `ttft_ms`, `inference_duration_ms`, `pipeline_duration_ms`)
   - `EvaluationResult`
   - `SSEStreamEvent`
   - `UserProfile`, `UserProfileUpdate`, `GameResultSummary`, `HistoryListResponse`
   - `LatencyBenchmarkRequest`, `LatencyBenchmarkResponse`
   - `ErrorResponse`

3. **Endpoint Path Verification**:
   - `POST /api/v1/sessions`
   - `GET /api/v1/sessions/{session_id}`
   - `POST /api/v1/sessions/{session_id}/evaluate` (SSE stream: `text/event-stream`)
   - `POST /api/v1/sessions/{session_id}/evaluate/sync` (JSON fallback)
   - `GET /api/v1/user/profile` & `PUT /api/v1/user/profile`
   - `GET /api/v1/results`
   - `GET /api/v1/prompts`
   - `GET /api/v1/health`
   - `POST /api/v1/benchmark/latency`

---

## 6. Full Contract Specification (`contracts/api_v1.json`)

The full JSON specification drafted and validated for `contracts/api_v1.json` is reproduced below:

```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "LinguaType API",
    "version": "1.0.0",
    "description": "API contract for LinguaType: low-latency, gamified translation and sentence construction trainer based on Monkeytype with streaming evaluation via fast LLMs (latency < 3s).",
    "contact": {
      "name": "LinguaType Team"
    }
  },
  "servers": [
    {
      "url": "http://localhost:8000",
      "description": "Local development backend server"
    },
    {
      "url": "/api/v1",
      "description": "Production API base path"
    }
  ],
  "tags": [
    {
      "name": "Sessions",
      "description": "Game session creation, configuration, and state retrieval"
    },
    {
      "name": "Evaluation",
      "description": "Low-latency streaming (SSE) and synchronous submission evaluation"
    },
    {
      "name": "User & Settings",
      "description": "User profile, language/style preferences, and session history"
    },
    {
      "name": "Prompts",
      "description": "Prompt catalog and difficulty management"
    },
    {
      "name": "Health & Benchmarking",
      "description": "System health, model readiness, and automated latency validation"
    }
  ],
  "paths": {
    "/api/v1/sessions": {
      "post": {
        "tags": ["Sessions"],
        "summary": "Create a new LinguaType game session",
        "description": "Initializes a game session for Mode A (phrase translation) or Mode B (situation/image prompt) with selected constraints (timer: 15s/30s/60s, word limits, input mode).",
        "operationId": "createSession",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/SessionCreateRequest"
              }
            }
          }
        },
        "responses": {
          "201": {
            "description": "Session created successfully",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/SessionResponse"
                }
              }
            }
          },
          "400": {
            "description": "Invalid session parameters",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          },
          "401": {
            "description": "Unauthorized access when authenticated session is required",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/sessions/{session_id}": {
      "get": {
        "tags": ["Sessions"],
        "summary": "Get session details and prompt by ID",
        "description": "Retrieves the session state, prompt content, time constraints, and completion status.",
        "operationId": "getSessionById",
        "parameters": [
          {
            "name": "session_id",
            "in": "path",
            "required": true,
            "description": "Unique session identifier",
            "schema": {
              "type": "string",
              "format": "uuid"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Session found",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/SessionResponse"
                }
              }
            }
          },
          "404": {
            "description": "Session not found",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/sessions/{session_id}/evaluate": {
      "post": {
        "tags": ["Evaluation"],
        "summary": "Stream evaluation feedback via Server-Sent Events (SSE)",
        "description": "Accepts user text input and streams progressive evaluation events (grammar error spans, semantic validation, exactly one stylistic alternative, speed metrics, latency breakdown). Target latency: TTFT < 800ms, total inference < 2500ms, end-to-end pipeline < 3000ms.",
        "operationId": "evaluateSessionStream",
        "parameters": [
          {
            "name": "session_id",
            "in": "path",
            "required": true,
            "description": "Unique session identifier",
            "schema": {
              "type": "string",
              "format": "uuid"
            }
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/EvaluationRequest"
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Server-Sent Events stream delivering real-time evaluation chunks and structured JSON events",
            "content": {
              "text/event-stream": {
                "schema": {
                  "$ref": "#/components/schemas/SSEStreamEvent"
                }
              }
            }
          },
          "400": {
            "description": "Invalid evaluation payload or text exceeds constraints",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          },
          "404": {
            "description": "Session not found or expired",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          },
          "504": {
            "description": "LLM evaluation timeout exceeded (> 3s)",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/sessions/{session_id}/evaluate/sync": {
      "post": {
        "tags": ["Evaluation"],
        "summary": "Synchronous evaluation (batch / non-streaming fallback)",
        "description": "Non-streaming fallback for clients or unit tests that require the complete evaluation result in a single JSON payload.",
        "operationId": "evaluateSessionSync",
        "parameters": [
          {
            "name": "session_id",
            "in": "path",
            "required": true,
            "description": "Unique session identifier",
            "schema": {
              "type": "string",
              "format": "uuid"
            }
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/EvaluationRequest"
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Complete evaluation result",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/EvaluationResult"
                }
              }
            }
          },
          "400": {
            "description": "Invalid submission payload",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          },
          "404": {
            "description": "Session not found",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/user/profile": {
      "get": {
        "tags": ["User & Settings"],
        "summary": "Get current user profile and settings",
        "description": "Fetches user configuration including native/target languages, preferred style, loose phrasing allowance, and input mode.",
        "operationId": "getUserProfile",
        "security": [
          {
            "FirebaseAuth": []
          }
        ],
        "responses": {
          "200": {
            "description": "User profile retrieved successfully",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/UserProfile"
                }
              }
            }
          },
          "401": {
            "description": "Missing or invalid Firebase token",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          }
        }
      },
      "put": {
        "tags": ["User & Settings"],
        "summary": "Update user settings and preferences",
        "description": "Updates language pairs, style preferences, and default input configurations.",
        "operationId": "updateUserProfile",
        "security": [
          {
            "FirebaseAuth": []
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/UserProfileUpdate"
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Profile updated successfully",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/UserProfile"
                }
              }
            }
          },
          "400": {
            "description": "Validation error in updated preferences",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          },
          "401": {
            "description": "Unauthorized",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/results": {
      "get": {
        "tags": ["User & Settings"],
        "summary": "Retrieve user session history and game results",
        "description": "Returns paginated list of past game results for the authenticated user, with accuracy, WPM, grammar errors, and style suggestions.",
        "operationId": "getResultsHistory",
        "security": [
          {
            "FirebaseAuth": []
          }
        ],
        "parameters": [
          {
            "name": "limit",
            "in": "query",
            "required": false,
            "description": "Maximum number of items to return (default 20, max 100)",
            "schema": {
              "type": "integer",
              "default": 20,
              "minimum": 1,
              "maximum": 100
            }
          },
          {
            "name": "offset",
            "in": "query",
            "required": false,
            "description": "Offset from beginning of dataset",
            "schema": {
              "type": "integer",
              "default": 0,
              "minimum": 0
            }
          },
          {
            "name": "mode",
            "in": "query",
            "required": false,
            "description": "Filter by game mode",
            "schema": {
              "type": "string",
              "enum": ["translation", "situation_image"]
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Paginated history retrieved successfully",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HistoryListResponse"
                }
              }
            }
          },
          "401": {
            "description": "Unauthorized",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/prompts": {
      "get": {
        "tags": ["Prompts"],
        "summary": "List available curated prompts",
        "description": "Fetches curated prompts filtered by mode, source/target languages, and difficulty level.",
        "operationId": "listPrompts",
        "parameters": [
          {
            "name": "mode",
            "in": "query",
            "required": false,
            "schema": {
              "type": "string",
              "enum": ["translation", "situation_image"]
            }
          },
          {
            "name": "source_language",
            "in": "query",
            "required": false,
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "target_language",
            "in": "query",
            "required": false,
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "difficulty",
            "in": "query",
            "required": false,
            "schema": {
              "type": "string",
              "enum": ["easy", "medium", "hard"]
            }
          },
          {
            "name": "limit",
            "in": "query",
            "required": false,
            "schema": {
              "type": "integer",
              "default": 10,
              "minimum": 1,
              "maximum": 50
            }
          }
        ],
        "responses": {
          "200": {
            "description": "List of matching prompts",
            "content": {
              "application/json": {
                "schema": {
                  "type": "array",
                  "items": {
                    "$ref": "#/components/schemas/Prompt"
                  }
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/health": {
      "get": {
        "tags": ["Health & Benchmarking"],
        "summary": "Service health check",
        "description": "Returns operational status of the FastAPI backend and connectivity to LLM provider.",
        "operationId": "healthCheck",
        "responses": {
          "200": {
            "description": "Service is healthy",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HealthStatus"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/benchmark/latency": {
      "post": {
        "tags": ["Health & Benchmarking"],
        "summary": "Run automated latency verification benchmark",
        "description": "Executes synthetic benchmark evaluation tests against the LLM provider to measure TTFT and total inference duration, verifying compliance with the <2.5s inference and <3.0s total pipeline SLA.",
        "operationId": "runLatencyBenchmark",
        "requestBody": {
          "required": false,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/LatencyBenchmarkRequest"
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Benchmark execution results and latency statistics",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/LatencyBenchmarkResponse"
                }
              }
            }
          },
          "500": {
            "description": "Benchmark execution failed",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          }
        }
      }
    }
  },
  "components": {
    "securitySchemes": {
      "FirebaseAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "Firebase ID Token passed as standard Bearer token in the Authorization header"
      }
    },
    "schemas": {
      "SessionCreateRequest": {
        "type": "object",
        "required": ["mode", "source_language", "target_language"],
        "properties": {
          "mode": {
            "type": "string",
            "enum": ["translation", "situation_image"],
            "description": "Game mode: Mode A (translation) or Mode B (situation/image prompt)"
          },
          "timer_seconds": {
            "type": ["integer", "null"],
            "enum": [15, 30, 60, null],
            "default": 30,
            "description": "Time limit in seconds (15s, 30s, or 60s; null for untimed word-limit mode)"
          },
          "target_word_count": {
            "type": "integer",
            "minimum": 3,
            "maximum": 50,
            "default": 10,
            "description": "Target word count for the sentence"
          },
          "margin_buffer": {
            "type": "integer",
            "minimum": 0,
            "maximum": 15,
            "default": 5,
            "description": "Additional allowed word count buffer beyond target_word_count"
          },
          "source_language": {
            "type": "string",
            "pattern": "^[a-z]{2}(-[A-Z]{2})?$",
            "default": "ru",
            "description": "Source/native language ISO code (e.g., 'ru', 'uz', 'es')"
          },
          "target_language": {
            "type": "string",
            "pattern": "^[a-z]{2}(-[A-Z]{2})?$",
            "default": "en",
            "description": "Target learning language ISO code (e.g., 'en')"
          },
          "difficulty": {
            "type": "string",
            "enum": ["easy", "medium", "hard"],
            "default": "medium",
            "description": "Prompt vocabulary and complexity difficulty"
          },
          "input_mode": {
            "type": "string",
            "enum": ["free", "scaffolding"],
            "default": "free",
            "description": "Free typing input or guided scaffolding assist"
          },
          "preferred_style": {
            "type": "string",
            "enum": ["conversational", "formal", "concise", "academic", "business"],
            "default": "conversational",
            "description": "Preferred stylistic tone for recommended alternative"
          },
          "allow_loose_phrasing": {
            "type": "boolean",
            "default": true,
            "description": "Whether semantic verification allows idiomatic and loose phrasing"
          }
        }
      },
      "Prompt": {
        "type": "object",
        "required": [
          "id",
          "type",
          "source_language",
          "target_language",
          "content",
          "difficulty",
          "target_word_count",
          "margin_buffer",
          "max_word_count"
        ],
        "properties": {
          "id": {
            "type": "string",
            "format": "uuid",
            "description": "Unique prompt identifier"
          },
          "type": {
            "type": "string",
            "enum": ["translation", "situation_image"],
            "description": "Prompt type"
          },
          "source_language": {
            "type": "string",
            "description": "Language of prompt"
          },
          "target_language": {
            "type": "string",
            "description": "Expected language for user submission"
          },
          "content": {
            "type": "string",
            "description": "Prompt textual content (phrase to translate or situation description)"
          },
          "image_url": {
            "type": ["string", "null"],
            "format": "uri",
            "description": "URL to image if Mode B situation uses an illustration"
          },
          "difficulty": {
            "type": "string",
            "enum": ["easy", "medium", "hard"]
          },
          "target_word_count": {
            "type": "integer"
          },
          "margin_buffer": {
            "type": "integer"
          },
          "max_word_count": {
            "type": "integer",
            "description": "Upper hard cap on words (target_word_count + margin_buffer)"
          }
        }
      },
      "SessionResponse": {
        "type": "object",
        "required": [
          "session_id",
          "status",
          "mode",
          "prompt",
          "timer_seconds",
          "input_mode",
          "preferred_style",
          "allow_loose_phrasing",
          "created_at",
          "expires_at"
        ],
        "properties": {
          "session_id": {
            "type": "string",
            "format": "uuid"
          },
          "status": {
            "type": "string",
            "enum": ["active", "completed", "cancelled", "expired"]
          },
          "mode": {
            "type": "string",
            "enum": ["translation", "situation_image"]
          },
          "prompt": {
            "$ref": "#/components/schemas/Prompt"
          },
          "timer_seconds": {
            "type": ["integer", "null"]
          },
          "input_mode": {
            "type": "string",
            "enum": ["free", "scaffolding"]
          },
          "preferred_style": {
            "type": "string",
            "enum": ["conversational", "formal", "concise", "academic", "business"]
          },
          "allow_loose_phrasing": {
            "type": "boolean"
          },
          "created_at": {
            "type": "string",
            "format": "date-time"
          },
          "expires_at": {
            "type": "string",
            "format": "date-time"
          }
        }
      },
      "EvaluationRequest": {
        "type": "object",
        "required": ["user_text", "time_spent_ms", "words_typed"],
        "properties": {
          "user_text": {
            "type": "string",
            "minLength": 1,
            "maxLength": 1000,
            "description": "Raw text submitted by user"
          },
          "time_spent_ms": {
            "type": "integer",
            "minimum": 0,
            "description": "Total active time in milliseconds from first keypress to submission"
          },
          "words_typed": {
            "type": "integer",
            "minimum": 0,
            "description": "Total count of whitespace-delimited words typed"
          },
          "character_count": {
            "type": "integer",
            "minimum": 0,
            "description": "Total characters typed"
          },
          "keystroke_count": {
            "type": "integer",
            "minimum": 0,
            "description": "Raw count of keystrokes registered"
          }
        }
      },
      "GrammarErrorSpan": {
        "type": "object",
        "required": ["start", "end", "original_text", "message", "suggestion", "category", "severity"],
        "properties": {
          "start": {
            "type": "integer",
            "minimum": 0,
            "description": "0-based start index inclusive in user_text"
          },
          "end": {
            "type": "integer",
            "minimum": 0,
            "description": "0-based end index exclusive in user_text"
          },
          "original_text": {
            "type": "string",
            "description": "Exact text excerpt containing error"
          },
          "message": {
            "type": "string",
            "description": "Human-readable explanation of the grammatical issue"
          },
          "suggestion": {
            "type": "string",
            "description": "Recommended correction replacement for this span"
          },
          "category": {
            "type": "string",
            "enum": ["grammar", "spelling", "punctuation", "syntax", "word_choice", "agreement", "tense"],
            "description": "Category of error"
          },
          "severity": {
            "type": "string",
            "enum": ["error", "warning", "info"],
            "description": "Severity level for UI rendering and scoring"
          }
        }
      },
      "SemanticValidation": {
        "type": "object",
        "required": ["is_valid", "score", "explanation", "missing_concepts"],
        "properties": {
          "is_valid": {
            "type": "boolean",
            "description": "True if meaning matches prompt intent, allowing loose phrasing"
          },
          "score": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100,
            "description": "Semantic preservation score from 0 (completely wrong) to 100 (exact match)"
          },
          "explanation": {
            "type": "string",
            "description": "Concise reasoning for the semantic validation verdict"
          },
          "missing_concepts": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "Key conceptual elements omitted by user (empty if valid)"
          }
        }
      },
      "StyleAlternative": {
        "type": "object",
        "required": ["style", "text", "explanation"],
        "properties": {
          "style": {
            "type": "string",
            "enum": ["conversational", "formal", "concise", "academic", "business"],
            "description": "Stylistic register applied"
          },
          "text": {
            "type": "string",
            "description": "Exactly ONE optimized alternative sentence matching the user's preferred style"
          },
          "explanation": {
            "type": "string",
            "description": "Brief explanation of how this alternative improves phrasing or style"
          }
        }
      },
      "SessionMetrics": {
        "type": "object",
        "required": [
          "wpm",
          "accuracy_score",
          "time_spent_ms",
          "word_count",
          "target_word_count",
          "word_limit_exceeded",
          "timer_expired"
        ],
        "properties": {
          "wpm": {
            "type": "number",
            "minimum": 0,
            "description": "Typing speed in Words Per Minute ((chars / 5) / (minutes))"
          },
          "accuracy_score": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100,
            "description": "Overall score taking into account grammar, semantic match, and length"
          },
          "time_spent_ms": {
            "type": "integer",
            "minimum": 0
          },
          "word_count": {
            "type": "integer",
            "minimum": 0
          },
          "target_word_count": {
            "type": "integer",
            "minimum": 1
          },
          "word_limit_exceeded": {
            "type": "boolean",
            "description": "True if word count exceeded max_word_count (target + buffer)"
          },
          "timer_expired": {
            "type": "boolean",
            "description": "True if user was cut off by timer reaching 0"
          }
        }
      },
      "LatencyBreakdown": {
        "type": "object",
        "required": ["ttft_ms", "inference_duration_ms", "pipeline_duration_ms"],
        "properties": {
          "ttft_ms": {
            "type": "number",
            "description": "Time To First Token in milliseconds (< 800ms SLA)"
          },
          "inference_duration_ms": {
            "type": "number",
            "description": "Total LLM inference duration in milliseconds (< 2500ms SLA)"
          },
          "pipeline_duration_ms": {
            "type": "number",
            "description": "Total end-to-end processing duration in milliseconds (< 3000ms SLA)"
          }
        }
      },
      "EvaluationResult": {
        "type": "object",
        "required": [
          "result_id",
          "session_id",
          "user_id",
          "user_text",
          "semantic_validation",
          "grammar_errors",
          "style_alternative",
          "metrics",
          "latency",
          "created_at"
        ],
        "properties": {
          "result_id": {
            "type": "string",
            "format": "uuid"
          },
          "session_id": {
            "type": "string",
            "format": "uuid"
          },
          "user_id": {
            "type": ["string", "null"],
            "description": "Firebase UID or null for guest"
          },
          "user_text": {
            "type": "string"
          },
          "semantic_validation": {
            "$ref": "#/components/schemas/SemanticValidation"
          },
          "grammar_errors": {
            "type": "array",
            "items": {
              "$ref": "#/components/schemas/GrammarErrorSpan"
            }
          },
          "style_alternative": {
            "$ref": "#/components/schemas/StyleAlternative"
          },
          "metrics": {
            "$ref": "#/components/schemas/SessionMetrics"
          },
          "latency": {
            "$ref": "#/components/schemas/LatencyBreakdown"
          },
          "created_at": {
            "type": "string",
            "format": "date-time"
          }
        }
      },
      "SSEStreamEvent": {
        "type": "object",
        "description": "Structured Server-Sent Event emitted during streaming evaluation",
        "required": ["event", "data"],
        "properties": {
          "event": {
            "type": "string",
            "enum": [
              "session_start",
              "token",
              "grammar_errors",
              "semantic_check",
              "style_alternative",
              "metrics",
              "done",
              "error"
            ],
            "description": "SSE event name"
          },
          "data": {
            "description": "JSON-encoded payload corresponding to event name",
            "oneOf": [
              {
                "type": "object",
                "properties": {
                  "status": { "type": "string" },
                  "session_id": { "type": "string", "format": "uuid" }
                }
              },
              {
                "type": "object",
                "properties": {
                  "token": { "type": "string" },
                  "index": { "type": "integer" }
                }
              },
              {
                "type": "object",
                "properties": {
                  "errors": {
                    "type": "array",
                    "items": { "$ref": "#/components/schemas/GrammarErrorSpan" }
                  }
                }
              },
              {
                "$ref": "#/components/schemas/SemanticValidation"
              },
              {
                "$ref": "#/components/schemas/StyleAlternative"
              },
              {
                "$ref": "#/components/schemas/SessionMetrics"
              },
              {
                "$ref": "#/components/schemas/EvaluationResult"
              },
              {
                "$ref": "#/components/schemas/ErrorResponse"
              }
            ]
          }
        }
      },
      "UserProfile": {
        "type": "object",
        "required": [
          "id",
          "email",
          "native_language",
          "target_language",
          "preferred_style",
          "allow_loose_phrasing",
          "input_mode",
          "created_at",
          "updated_at"
        ],
        "properties": {
          "id": {
            "type": "string",
            "description": "Firebase UID"
          },
          "email": {
            "type": "string",
            "format": "email"
          },
          "display_name": {
            "type": ["string", "null"]
          },
          "native_language": {
            "type": "string",
            "default": "ru"
          },
          "target_language": {
            "type": "string",
            "default": "en"
          },
          "preferred_style": {
            "type": "string",
            "enum": ["conversational", "formal", "concise", "academic", "business"],
            "default": "conversational"
          },
          "allow_loose_phrasing": {
            "type": "boolean",
            "default": true
          },
          "input_mode": {
            "type": "string",
            "enum": ["free", "scaffolding"],
            "default": "free"
          },
          "created_at": {
            "type": "string",
            "format": "date-time"
          },
          "updated_at": {
            "type": "string",
            "format": "date-time"
          }
        }
      },
      "UserProfileUpdate": {
        "type": "object",
        "properties": {
          "native_language": {
            "type": "string"
          },
          "target_language": {
            "type": "string"
          },
          "preferred_style": {
            "type": "string",
            "enum": ["conversational", "formal", "concise", "academic", "business"]
          },
          "allow_loose_phrasing": {
            "type": "boolean"
          },
          "input_mode": {
            "type": "string",
            "enum": ["free", "scaffolding"]
          }
        }
      },
      "GameResultSummary": {
        "type": "object",
        "required": [
          "id",
          "session_id",
          "mode",
          "source_language",
          "target_language",
          "prompt_content",
          "user_text",
          "time_spent_ms",
          "wpm",
          "accuracy_score",
          "semantic_valid",
          "error_count",
          "recommended_variant",
          "preferred_style",
          "created_at"
        ],
        "properties": {
          "id": {
            "type": "string",
            "format": "uuid"
          },
          "session_id": {
            "type": "string",
            "format": "uuid"
          },
          "mode": {
            "type": "string",
            "enum": ["translation", "situation_image"]
          },
          "source_language": {
            "type": "string"
          },
          "target_language": {
            "type": "string"
          },
          "prompt_content": {
            "type": "string"
          },
          "user_text": {
            "type": "string"
          },
          "time_spent_ms": {
            "type": "integer"
          },
          "wpm": {
            "type": "number"
          },
          "accuracy_score": {
            "type": "integer"
          },
          "semantic_valid": {
            "type": "boolean"
          },
          "error_count": {
            "type": "integer"
          },
          "recommended_variant": {
            "type": "string"
          },
          "preferred_style": {
            "type": "string"
          },
          "created_at": {
            "type": "string",
            "format": "date-time"
          }
        }
      },
      "HistoryListResponse": {
        "type": "object",
        "required": ["results", "total", "offset", "limit"],
        "properties": {
          "results": {
            "type": "array",
            "items": {
              "$ref": "#/components/schemas/GameResultSummary"
            }
          },
          "total": {
            "type": "integer",
            "minimum": 0
          },
          "offset": {
            "type": "integer",
            "minimum": 0
          },
          "limit": {
            "type": "integer",
            "minimum": 1
          }
        }
      },
      "HealthStatus": {
        "type": "object",
        "required": ["status", "service", "version", "llm_connected"],
        "properties": {
          "status": {
            "type": "string",
            "enum": ["ok", "degraded", "down"]
          },
          "service": {
            "type": "string",
            "default": "linguatype-backend"
          },
          "version": {
            "type": "string",
            "default": "1.0.0"
          },
          "llm_connected": {
            "type": "boolean"
          },
          "llm_provider": {
            "type": "string",
            "default": "google-gemini-flash"
          }
        }
      },
      "LatencyBenchmarkRequest": {
        "type": "object",
        "properties": {
          "iterations": {
            "type": "integer",
            "minimum": 1,
            "maximum": 10,
            "default": 3
          },
          "model": {
            "type": "string",
            "default": "gemini-2.0-flash"
          },
          "test_prompt": {
            "type": "string",
            "default": "Опишите ваш утренний распорядок дня."
          },
          "test_submission": {
            "type": "string",
            "default": "Every morning I wake up at seven o'clock and drink a hot cup of coffee before starting my work."
          }
        }
      },
      "LatencyPercentiles": {
        "type": "object",
        "required": ["min", "max", "avg", "p95"],
        "properties": {
          "min": { "type": "number" },
          "max": { "type": "number" },
          "avg": { "type": "number" },
          "p95": { "type": "number" }
        }
      },
      "LatencyBenchmarkResponse": {
        "type": "object",
        "required": [
          "timestamp",
          "iterations",
          "ttft_ms",
          "inference_duration_ms",
          "pipeline_duration_ms",
          "meets_constraint"
        ],
        "properties": {
          "timestamp": {
            "type": "string",
            "format": "date-time"
          },
          "iterations": {
            "type": "integer"
          },
          "ttft_ms": {
            "$ref": "#/components/schemas/LatencyPercentiles"
          },
          "inference_duration_ms": {
            "$ref": "#/components/schemas/LatencyPercentiles"
          },
          "pipeline_duration_ms": {
            "$ref": "#/components/schemas/LatencyPercentiles"
          },
          "meets_constraint": {
            "type": "boolean",
            "description": "True if p95 inference_duration_ms < 2500ms and pipeline_duration_ms < 3000ms"
          }
        }
      },
      "ErrorResponse": {
        "type": "object",
        "required": ["code", "message"],
        "properties": {
          "code": {
            "type": "string",
            "description": "Standardized machine-readable error code (e.g. VALIDATION_ERROR, SESSION_NOT_FOUND, LLM_TIMEOUT, UNAUTHORIZED)"
          },
          "message": {
            "type": "string",
            "description": "Human-readable explanation of error"
          },
          "details": {
            "type": ["object", "array", "string", "null"],
            "description": "Optional debugging details or field-level validation errors"
          }
        }
      }
    }
  }
}
```
