# Task Assignment: Worker M3 (Frontend LinguaType Core)

Working directory: c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\worker_m3_1
Target files owned exclusively:
- frontend/src/ts/components/pages/linguatype/**
- frontend/src/ts/states/linguatype.ts
- frontend/src/ts/queries/linguatype-api.ts
- frontend/src/ts/input/hotkeys/linguatype.ts
- frontend/src/ts/components/pages/page-registry.ts
- frontend/src/ts/controllers/route-controller.ts
- frontend/src/ts/components/layout/header/Nav.tsx
- frontend/src/ts/__tests__/linguatype/**

Contract: c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\contracts\api_v1.json
Project definition: c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\orchestrator_1\PROJECT.md
Original Request: c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\ORIGINAL_REQUEST.md
Survey Report: c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\explorer_survey_1\handoff.md
Coding Standards: c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\CODING_STANDARDS.md

## MANDATORY INTEGRITY WARNING
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Objectives
1. Implement the LinguaType mode in SolidJS (.tsx) under `frontend/src/ts/components/pages/linguatype/`:
   - `LinguaTypePage.tsx`: Top-level page container, binds hotkeys, timer countdown, auto-focus, responsive layout.
   - `LinguaTypeConfig.tsx`: Mode selector (Mode A: translation, Mode B: situation/image), timer buttons (15s, 30s, 60s, untimed), target word count, style preference dropdown.
   - `PromptCard.tsx`: Displays prompt source sentence or situation/image context with clean typography.
   - `LinguaTypeInput.tsx`: Free typing text area with live word counter (target + margin buffer), smooth caret, focus management.
   - `StreamingFeedbackCard.tsx`: Real-time SSE rendering (progressive stream tokens, inline character span highlights for grammar errors, semantic validity badge & score, exactly ONE recommended style alternative).
2. State & API Integration:
   - `frontend/src/ts/states/linguatype.ts`: Solid store for session status, prompt, typed buffer, timer, live metrics, and stream feedback.
   - `frontend/src/ts/queries/linguatype-api.ts`: SSE stream client reading `POST /api/v1/sessions/{id}/evaluate` chunks via `fetch` + `ReadableStreamDefaultReader`, parsing event lines (`session_start`, `token`, `grammar_errors`, `semantic_check`, `style_alternative`, `metrics`, `done`, `error`), with fallback to `/sync`.
3. Routing & Navigation:
   - Add `linguatype` to `page-registry.ts`.
   - Add `/linguatype` route handler to `route-controller.ts`.
   - Add navigation icon button (FontAwesome `fa-language`) in `frontend/src/ts/components/layout/header/Nav.tsx`.
4. Accessibility & UI Rules:
   - Full keyboard navigation: `Tab+Enter` triggers test restart, `Esc` cancels/resets test, auto-focus input.
   - Accessibility (WCAG): `aria-live="polite"` for streaming LLM text, `aria-invalid="true"` and `aria-describedby` for error spans.
   - Strictly MINIMALIST dark Monkeytype aesthetic using Tailwind variables (`bg-bg`, `text-text`, `text-main`, `bg-sub`, `text-error`), **STRICTLY ZERO STICKERS**, no decorative cartoon widgets.
5. Automated Tests:
   - Write unit tests under `frontend/src/ts/__tests__/linguatype/`:
     * `state.spec.ts`: test session state transitions, word count, timer expiration
     * `sse-parser.spec.ts`: test parsing of all 8 SSE stream events and error spans
   - Run Vitest tests (`pnpm vitest run frontend/src/ts/__tests__/linguatype` or node/vitest command).
6. Write your handoff report to `c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\worker_m3_1\handoff.md`.


## 2026-10-17T06:10:36Z
[Message] timestamp=2026-10-17T06:10:36Z sender=3b1515b3-2073-47ba-bf07-f8f58de22f4d priority=MESSAGE_PRIORITY_HIGH content=You are Worker 1 for Milestone 3 (Frontend LinguaType Core).
Your working directory is: c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\worker_m3_1
Read:
- c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\worker_m3_1\DISPATCH.md
- c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\contracts\api_v1.json
- c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\orchestrator_1\PROJECT.md
- c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\ORIGINAL_REQUEST.md
- c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\explorer_survey_1\handoff.md
- c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\CODING_STANDARDS.md

DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

You own exclusively:
- frontend/src/ts/components/pages/linguatype/**
- frontend/src/ts/states/linguatype.ts
- frontend/src/ts/queries/linguatype-api.ts
- frontend/src/ts/input/hotkeys/linguatype.ts
- frontend/src/ts/components/pages/page-registry.ts
- frontend/src/ts/controllers/route-controller.ts
- frontend/src/ts/components/layout/header/Nav.tsx
- frontend/src/ts/__tests__/linguatype/**

Implement the SolidJS LinguaType page (Mode A & B, timer options, word count budget, real-time SSE feedback card, keyboard navigation Tab+Enter/Esc, a11y live regions, strictly minimalist aesthetic with NO stickers).
Write automated unit tests under frontend/src/ts/__tests__/linguatype/ and verify using vitest or node test runner.
Write your handoff report to c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\worker_m3_1\handoff.md and notify me via send_message when done.
