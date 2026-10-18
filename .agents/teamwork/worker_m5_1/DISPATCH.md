# Dispatch Assignment: Milestone 5 — Sequential Integration, E2E Verification & Latency Benchmarks

**Role**: Integration & Verification Worker (worker_m5_1)  
**Assigned Agent**: worker_m5_1  
**Target Milestone**: Milestone 5  
**Timestamp**: 2026-10-17T07:19:00Z  

---

## 1. Context & Objectives

All functional milestones for LinguaType are now implemented:
- Milestone 1: API Contract (`contracts/api_v1.json`) — OpenAPI 3.1.0 specification.
- Milestone 2: Backend FastAPI Service (`backend/app/`, `backend/tests/`).
- Milestone 3: Frontend LinguaType Core (`frontend/src/ts/components/pages/linguatype/`, `frontend/src/ts/states/linguatype.ts`, `frontend/src/ts/queries/linguatype-api.ts`, hotkeys, route `/linguatype`).
- Milestone 4: Auth & App Hosting (`frontend/src/ts/firebase.ts`, `LinguaTypeConfig.tsx`, `apphosting.yaml`, `frontend/src/ts/__tests__/linguatype/auth-settings.spec.ts`).

Your task is to execute the comprehensive integration verification and latency benchmarking suite to validate that the entire system functions as a coherent, robust, and SLA-compliant application.

---

## 2. Core Execution Tasks

1. **Backend Test Suite & Latency SLA**:
   - Run `pytest backend/tests` using the test runner.
   - Verify that all 26 test cases pass (100% success rate).
   - Verify that latency benchmarks explicitly validate:
     - Time to First Token (TTFT) < 800ms
     - Complete LLM inference < 2,500ms
     - Total end-to-end pipeline latency < 3,000ms

2. **Frontend Test Suites**:
   - Run the full suite of frontend unit tests:
     ```powershell
     node --loader ./scripts/ts-loader.js --experimental-strip-types --test frontend/src/ts/__tests__/linguatype/auth-settings.spec.ts frontend/src/ts/__tests__/linguatype/sse-parser.spec.ts frontend/src/ts/__tests__/linguatype/state.spec.ts
     ```
   - Verify that all 33 tests across 6 test suites pass with 0 failures:
     - State & metrics calculation (word limits, error penalties, accuracy scoring)
     - SSE stream parser (chunk fragmentation, event dispatching, comment filtering)
     - Firebase Auth & Magic Link methods
     - Profile REST serialization & reactive preference sync
     - `apphosting.yaml` configuration validation

3. **Code Quality, Formatting & Static Checks**:
   - Verify linting and formatting on all touched files:
     - Check `frontend/src/ts/components/pages/linguatype/**`
     - Check `frontend/src/ts/states/linguatype.ts`
     - Check `frontend/src/ts/queries/linguatype-api.ts`
     - Check `frontend/src/ts/firebase.ts`
     - Check `backend/app/**`
   - Use `pnpm oxlint --format agent` or `npx oxfmt` if applicable, ensuring zero breaking lint errors.

4. **Architecture & Contract Verification**:
   - Verify 100% agreement between:
     - `contracts/api_v1.json` endpoints and payloads
     - `backend/app/api/v1/` route definitions and Pydantic schemas
     - `frontend/src/ts/queries/linguatype-api.ts` HTTP/SSE requests and data types

5. **UI & A11y Verification**:
   - Verify compliance with user rules:
     - Minimalist dark aesthetic adhering to Monkeytype CSS variables (`bg-bg`, `text-text`, `text-main`, `bg-sub-alt`, `text-error`).
     - **Strictly ZERO STICKERS** or unnecessary visual clutter.
     - WCAG accessibility: keyboard navigation (`Tab+Enter` restart, `Esc` reset, automatic input autofocus), ARIA live regions for streaming LLM feedback.

---

## 3. Mandatory Integrity Warning

DO NOT CHEAT. All implementations and verification outputs must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

---

## 4. Deliverable

Write your comprehensive, 5-component handoff report to:
`c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\worker_m5_1\handoff.md`

Include:
- 1. Observation (exact commands run and verbatim stdout/stderr output)
- 2. Logic Chain (analysis of integration, latency SLA compliance, and cross-module contracts)
- 3. Caveats (runtime limitations, environment notes)
- 4. Conclusion (clear summary of pass/fail status)
- 5. Verification Method (reproducible commands for reviewers)

When done, send a message to orchestrator notifying completion.
