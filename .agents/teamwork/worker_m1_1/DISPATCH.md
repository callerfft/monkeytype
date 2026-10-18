# Task Assignment: Worker M1 (Contract Definition)

Working directory: c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\worker_m1_1
Project definition: c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\orchestrator_1\PROJECT.md
Original Request: c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\ORIGINAL_REQUEST.md
Spec Miner Contract Draft: c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\spec_miner_survey_1\api_v1.json

## MANDATORY INTEGRITY WARNING
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Objectives
1. Read the drafted contract in `c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\spec_miner_survey_1\api_v1.json`.
2. Ensure directory `contracts/` exists at project root `c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\contracts`.
3. Create/write `contracts/api_v1.json` with the complete, validated OpenAPI 3.1.0 specification.
4. Verify JSON syntax and schema validity using node:
   `node -e "const fs = require('fs'); const data = JSON.parse(fs.readFileSync('contracts/api_v1.json', 'utf8')); console.log('Contract valid:', data.info.title, data.openapi);"`
5. Verify all endpoints and schemas are covered:
   - Sessions (Mode A translation, Mode B situation_image, timers 15/30/60/null, word limits)
   - Real-time SSE streaming evaluation (`POST /api/v1/sessions/{session_id}/evaluate`) with events (`session_start`, `token`, `grammar_errors`, `semantic_check`, `style_alternative`, `metrics`, `done`, `error`)
   - Grammar error spans (`start`, `end`, `original_text`, `message`, `suggestion`, `category`, `severity`)
   - Semantic validity check (`is_valid`, `score`, `explanation`, `missing_concepts`)
   - Exactly ONE style alternative (`preferred_style`)
   - Latency benchmark endpoint (`POST /api/v1/benchmark/latency`)
   - Auth & Settings schemas (`UserProfile`, `HistoryListResponse`)
6. Write a complete handoff report in `c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\worker_m1_1\handoff.md`.

## 2026-10-17T05:42:24Z
From: 3b1515b3-2073-47ba-bf07-f8f58de22f4d
You are Worker 1 for Milestone 1 (API Contract Definition) of the LinguaType project.
Your working directory is: c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\worker_m1_1
Please read:
- c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\worker_m1_1\DISPATCH.md
- c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\orchestrator_1\PROJECT.md
- c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\ORIGINAL_REQUEST.md
- c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\spec_miner_survey_1\api_v1.json

DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Place the complete OpenAPI 3.1.0 contract into contracts/api_v1.json at the project root.
Verify its syntax and all schema definitions using node.
Write your handoff report to c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\worker_m1_1\handoff.md and notify me via send_message when done.
