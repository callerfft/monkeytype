# Task Assignment: Worker M1-2 (Contract Remediation)

Working directory: c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\worker_m1_2
Target contract: c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\contracts\api_v1.json
Reviewer 2 handoff: c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\reviewer_m1_2\handoff.md
Challenger 1 handoff: c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\challenger_m1_1\handoff.md
Challenger 2 handoff: c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\challenger_m1_2\handoff.md

## MANDATORY INTEGRITY WARNING
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Context
Iteration 1 review & challenge gate rejected the contract due to a blocking defect in `SSEStreamEvent`:
1. `SSEStreamEvent.properties.data` uses `oneOf` across 10 subschemas. Because `SSETokenPayload` and the inline `{properties: {errors: ...}}` schema lack `required` properties and allow `additionalProperties: true`, they match any generic JSON object. This causes 7 out of 8 standard SSE events (`session_start`, `token`, `semantic_check`, `style_alternative`, `metrics`, `done`, `error`) to fail `oneOf` validation due to multiple branch matches.
2. `SessionMetrics.required` is missing `"target_met"`.
3. In `EvaluationRequest.user_text`, support `minLength: 0` so empty input upon timer expiration can be cleanly reported.

## Action Items
1. Edit `contracts/api_v1.json`:
   - In `SSETokenPayload`: add `"required": ["text"]` and `"additionalProperties": false`.
   - In `SSEStreamEvent.properties.data`: change `"oneOf"` to `"anyOf"` (or add `"required": ["errors"]` and `"additionalProperties": false` to the inline errors schema).
   - In `SessionMetrics`: add `"target_met"` to `"required"`.
   - In `EvaluationRequest.properties.user_text`: change `"minLength": 1` to `"minLength": 0` with description noting 0-length text upon timer expiration.
2. Run automated validation:
   - Run the reproduction script from `.agents/teamwork/challenger_m1_1/handoff.md` and `.agents/teamwork/reviewer_m1_2/test_schema.py` to ensure 100% of SSE event types pass validation.
   - Verify syntax with `node -e "JSON.parse(fs.readFileSync('contracts/api_v1.json'))"`.
3. Document all changes and verification output in `c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\worker_m1_2\handoff.md`.


## 2026-10-17T05:56:59Z
You are Worker 2 for Milestone 1 (Contract Remediation).
Your working directory is: c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\worker_m1_2
Read:
- c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\worker_m1_2\DISPATCH.md
- c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\contracts\api_v1.json
- c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\reviewer_m1_2\handoff.md
- c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\challenger_m1_1\handoff.md

DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Apply the required fixes to contracts/api_v1.json:
1. In SSETokenPayload: add required: ["text"], additionalProperties: false.
2. In SSEStreamEvent.properties.data: change oneOf to anyOf (and add required: ["errors"], additionalProperties: false to the inline error envelope).
3. In SessionMetrics: add target_met to required array.
4. In EvaluationRequest.properties.user_text: change minLength to 0 for timer expiration.

Verify the fix using node and python jsonschema scripts so 100% of event types pass validation.
Write your handoff report to c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\worker_m1_2\handoff.md and notify me via send_message when done.
