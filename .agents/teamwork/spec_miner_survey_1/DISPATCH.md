# Task Assignment for Spec Miner 1: Specification Mining & Contract Formulation

Working directory: c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\spec_miner_survey_1
Original Request: c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\ORIGINAL_REQUEST.md

## Objectives
1. Analyze `ORIGINAL_REQUEST.md`, `CODING_STANDARDS.md`, `AGENTS.md` and related specs.
2. Formalize complete JSON Schema / OpenAPI 3.1 specifications needed for `contracts/api_v1.json`:
   - Session creation & retrieval (Mode A: phrase translation, Mode B: situation/image prompt; timers 15/30/60s; word limits).
   - Evaluation streaming request and response format (SSE / JSON events):
     * Token-by-token or chunk-by-chunk stream
     * Grammar error spans (`start`, `end`, `message`, `suggestion`, `category`)
     * Semantic validity check (boolean / score / explanation)
     * Style alternative: exactly ONE alternative tailored to selected style (academic, business, casual, etc.)
   - Auth & Settings schema: user profile, native/target languages, preferred style, session history.
   - Error schemas and latency constraints.
3. Detail all gameplay rules, a11y specifications (keyboard shortcuts Tab+Enter, Esc, ARIA attributes), and design constraints (minimalist, no stickers).

## Output
Write a structured handoff report in `c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\spec_miner_survey_1\handoff.md` with:
- Complete feature inventory with requirement traceability
- Draft schema definitions ready for `contracts/api_v1.json`
- Verification criteria for contract compliance


## 2026-10-17T05:31:16Z
From: 3b1515b3-2073-47ba-bf07-f8f58de22f4d
You are Spec Miner 1 for the LinguaType project survey phase.
Your working directory is: c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\spec_miner_survey_1
Please read:
- c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\spec_miner_survey_1\DISPATCH.md
- c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\ORIGINAL_REQUEST.md
- c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\CODING_STANDARDS.md

Mine and formalize all requirements into a complete specification for contracts/api_v1.json (OpenAPI 3.1 / JSON Schema) covering sessions (Mode A/B, timers 15/30/60s, word limits), streaming SSE evaluation (error spans, semantic validity, exactly 1 style alternative), auth/settings (languages, style), error handling, and latency constraints.
Write your complete structured handoff report in c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\spec_miner_survey_1\handoff.md.
When finished, notify me using send_message.
