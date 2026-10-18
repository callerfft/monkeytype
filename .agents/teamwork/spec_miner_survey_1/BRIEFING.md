# BRIEFING — 2026-10-17T05:32:00Z

## Mission
Mine and formalize all requirements into a complete specification for contracts/api_v1.json (OpenAPI 3.1 / JSON Schema) covering sessions, streaming SSE evaluation, auth/settings, error handling, and latency constraints.

## 🔒 My Identity
- Archetype: teamwork_preview_spec_miner
- Roles: spec_miner, specification_analyst
- Working directory: c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\spec_miner_survey_1
- Original parent: 3b1515b3-2073-47ba-bf07-f8f58de22f4d
- Milestone: Survey & Contract Specification Mining

## 🔒 Key Constraints
- Do NOT implement anything — read-only with respect to project source code. Write only to own metadata folder (.agents/teamwork/spec_miner_survey_1).
- Prioritize authoritative sources over assumptions.
- Must cover: Mode A (translation), Mode B (situation/image), timers (15/30/60s), word limits, SSE streaming evaluation (grammar error spans, semantic validation, exactly 1 style alternative), auth/settings (languages, style), latency constraints (<3s total, <2.5s inference), a11y keyboard shortcuts (Tab+Enter, Esc, ARIA), and minimalist UI (no stickers).
- Follow CODING_STANDARDS.md and AGENTS.md rules.

## Current Parent
- Conversation ID: 3b1515b3-2073-47ba-bf07-f8f58de22f4d
- Updated: not yet

## Task Summary
- **What to build**: Full OpenAPI 3.1 and JSON Schema draft specification for contracts/api_v1.json, feature inventory, edge cases, and handoff report.
- **Success criteria**: Complete coverage of R1-R5, data models, error formats, SSE events, and acceptance criteria. [COMPLETED]
- **Interface contracts**: Validated in .agents/teamwork/spec_miner_survey_1/api_v1.json and handoff.md
- **Code layout**: backend/ (FastAPI) and frontend/ (SolidJS Monkeytype)

## Key Decisions Made
- OpenAPI 3.1.0 chosen for `contracts/api_v1.json` to leverage native JSON Schema Draft 2020-12 alignment.
- Evaluation stream defined via Server-Sent Events (SSE) with structured event types: `session_start`, `token`, `grammar_errors`, `semantic_check`, `style_alternative`, `metrics`, `done`, `error`.
- Error spans strictly typed: `start` (0-based char index), `end` (0-based char index), `message`, `suggestion`, `category`, `severity`.
- Style alternatives strictly limited to exactly 1 choice matching user style preference (`conversational`, `formal`, `concise`, `academic`, `business`).
- Latency SLA hard-coded in contract: TTFT < 800ms, total inference < 2500ms, pipeline < 3000ms, verified via automated `/api/v1/benchmark/latency` endpoint.
- Accessibility and UI constraints formalized: Tab+Enter quick restart, Esc reset, aria-live stream announcements, strictly no stickers.

## Artifact Index
- c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\ORIGINAL_REQUEST.md — Original User Requirements
- c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\LinguaType_Project_Architecture.md — Architecture & Core Game Loop specification
- c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\spec_miner_survey_1\DISPATCH.md — Task assignment
- c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\spec_miner_survey_1\progress.md — Liveness & task execution log
- c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\spec_miner_survey_1\handoff.md — Final handoff report & contract draft

## Loaded Skills
- None requested or loaded.
