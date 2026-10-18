# Task Assignment: Worker M2 (Backend FastAPI Service)

Working directory: c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\worker_m2_1
Target files owned exclusively: backend/app/**, backend/tests/**, backend/pyproject.toml, backend/requirements.txt
Contract: c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\contracts\api_v1.json
Project definition: c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\orchestrator_1\PROJECT.md
Original Request: c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\ORIGINAL_REQUEST.md
Survey Report: c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\explorer_survey_2\handoff.md

## MANDATORY INTEGRITY WARNING
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Objectives
1. Implement a clean, modular Python FastAPI service under `backend/app/` strictly conforming to `contracts/api_v1.json`:
   - `backend/app/main.py`: FastAPI app, CORS middleware, global exception handlers, lifespan management
   - `backend/app/config.py`: Pydantic BaseSettings
   - `backend/app/api/v1/`:
     * `sessions.py`: POST /api/v1/sessions (Mode A translation Russian->English, Mode B situation_image; timers 15/30/60/null; word limits), GET /api/v1/sessions/{id}
     * `evaluation.py`: POST /api/v1/sessions/{id}/evaluate (SSE text/event-stream via StreamingResponse yielding events: session_start, token, grammar_errors, semantic_check, style_alternative, metrics, done, error) & POST /api/v1/sessions/{id}/evaluate/sync
     * `user.py`: GET /api/v1/user/profile, PUT /api/v1/user/profile, GET /api/v1/results
     * `prompts.py`: GET /api/v1/prompts
     * `health.py`: GET /api/v1/health
     * `benchmark.py`: POST /api/v1/benchmark/latency
   - `backend/app/models/`: Pydantic models matching all 23 contract schemas
   - `backend/app/services/`:
     * `prompt_store.py`: Curated prompts for Mode A (Russian source sentences) and Mode B (situation/image prompts)
     * `session_store.py`: In-memory session tracking
     * `llm_service.py`: Async streaming client using `httpx` to Google Gemini Flash REST API
     * `mock_llm_service.py`: High-performance deterministic mock for offline sandbox testing (<500ms TTFT, realistic grammar error spans, semantic validation, single style alternative)
     * `metrics_service.py`: Calculates WPM, accuracy score, duration, word count, target_met
   - `backend/app/utils/`: SSE formatting generator and latency timer
2. Implement automated test suite under `backend/tests/`:
   - `test_contract.py`: Pydantic models vs contracts/api_v1.json schemas
   - `test_sessions.py`: Mode A/B creation, constraints (timers 15/30/60/null, target_word_count)
   - `test_evaluation_stream.py`: Full SSE event sequence and payload schema validity
   - `test_evaluation_sync.py`: Synchronous evaluation
   - `test_latency_benchmark.py`: Automated assertion confirming TTFT < 800ms, total inference < 2.5s, total pipeline < 3.0s SLA
3. Run `pytest backend/tests` to verify 100% of tests pass.
4. Write your handoff report to `c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\worker_m2_1\handoff.md`.


## 2026-10-17T06:10:36Z
[Message] timestamp=2026-10-17T06:10:36Z sender=3b1515b3-2073-47ba-bf07-f8f58de22f4d priority=MESSAGE_PRIORITY_HIGH content=You are Worker 1 for Milestone 2 (Backend FastAPI Service).
Your working directory is: c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\worker_m2_1
Read:
- c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\worker_m2_1\DISPATCH.md
- c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\contracts\api_v1.json
- c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\orchestrator_1\PROJECT.md
- c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\ORIGINAL_REQUEST.md
- c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\explorer_survey_2\handoff.md

DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

You own exclusively: backend/app/**, backend/tests/**, backend/pyproject.toml, backend/requirements.txt.
Implement the FastAPI service with streaming evaluation SSE, error spans, semantic check, style alternative, latency benchmarking, and automated pytest suite.
Run pytest and confirm 100% tests pass.
Write your handoff report to c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\worker_m2_1\handoff.md and notify me via send_message when done.
