# Dispatch Assignment: Milestone 5 Remediation Worker (worker_m5_2)

**Role**: Remediation Worker (worker_m5_2)  
**Target**: Milestone 5 — Remediate Reviewer 1 Findings & Hardened Verification  
**Date**: 2026-10-17  

---

## 1. Context & Reviewer Feedback
`reviewer_m5_1` issued a `REQUEST_CHANGES` verdict with critical findings:
1. `backend/app/services/llm_service.py`: Stubbed facade for Gemini Flash streaming (lines 40-50 contain an empty `pass` in `try...except`).
2. `backend/app/services/mock_llm_service.py`: `generate_style_alternative()` returns hardcoded morning coffee sentences for all prompts regardless of topic.
3. `backend/app/api/v1/benchmark.py`: Synthetic benchmark timings in mock mode need to be clearly separated from live inference and execute real processing.
4. `frontend/src/ts/queries/linguatype-api.ts`: Line 155 hardcodes `API_BASE = "http://localhost:8000/api/v1"`, breaking production Firebase App Hosting deployments (`https://*.web.app`).
5. Missing automated E2E integration test exercising real frontend client requests against FastAPI endpoints.

---

## 2. Remediation Requirements

### 1. Genuine Gemini Flash Streaming Client (`backend/app/services/llm_service.py`)
- Replace the empty `pass` with real, production-ready streaming integration using `httpx.AsyncClient`.
- When `self.provider == "gemini"` and `self.api_key` is provided:
  - Call the Google Generative Language API endpoint: `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:streamGenerateContent?key={self.api_key}`
  - Send the system instructions and user submission with JSON schema constraints.
  - Parse the streaming SSE chunks from Gemini and yield SSEStreamEvent objects (`session_start`, `token`, `grammar_errors`, `semantic_check`, `style_alternative`, `metrics`, `done`).
  - If `api_key` is not configured or in offline mode, fall back cleanly to `mock_llm_service`.

### 2. Dynamic Style Alternatives (`backend/app/services/mock_llm_service.py`)
- **ELIMINATE ALL HARDCODED COFFEE STRINGS**.
- Implement genuine dynamic stylistic rewriting based on the prompt's content and the user's input:
  - Formulate a tailored sentence that preserves the semantic meaning of the prompt/submission:
    - `FORMAL`: Uses elevated syntactic structure and formal vocabulary suitable for the topic.
    - `CONCISE`: Strips redundant modifiers for maximum brevity.
    - `ACADEMIC`: Employs analytical, objective structures.
    - `BUSINESS`: Focuses on outcome-oriented, professional phrasing.
    - `CASUAL`: Natural colloquial phrasing.
  - Test with diverse prompts (e.g. mountain hiking, weather, technology) to ensure the generated alternative always matches the input context.

### 3. Production-Ready API Base URL (`frontend/src/ts/queries/linguatype-api.ts`)
- Replace line 155:
  ```typescript
  const API_BASE =
    typeof window !== "undefined" &&
    window.location.origin &&
    !window.location.origin.includes(":5173") &&
    !window.location.origin.includes(":3000")
      ? `${window.location.origin}/api/v1`
      : "http://localhost:8000/api/v1";
  ```
  Ensure in production App Hosting it uses `/api/v1` without protocol mismatch or hardcoded localhost.

### 4. Automated End-to-End Test (`backend/tests/test_e2e_integration.py`)
- Add an end-to-end integration test that boots FastAPI ASGI and tests the complete flow:
  1. Create session (`POST /api/v1/sessions`)
  2. Stream evaluation (`POST /api/v1/sessions/{id}/evaluate`) and parse all SSE events
  3. Verify non-coffee dynamic style alternative
  4. Verify latency tracking and SLA adherence

---

## 3. Mandatory Integrity Warning
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work.

---

## 4. Deliverable
Write your complete handoff report to:
`c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\worker_m5_2\handoff.md`
Notify orchestrator via `send_message` when done.
