# Handoff Report: Milestone 1 (API Contract Definition — Challenger 2)

## 1. Observation
- **Target File**: `c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\contracts\api_v1.json`
- **Execution Environment**: Python 3.14.3, `jsonschema` 4.26.0 (implementing JSON Schema Draft 2020-12 / OpenAPI 3.1.0), `referencing` 0.37.0.
- **Empirical Test Suite**: Executed 93 empirical schema constraint and payload validation assertions via `python empirical_stress_test.py`.
- **Summary of Test Results**:
  - Total assertions: 93
  - Passed: 85
  - Failed: 8
  - Machine-readable test log saved to: `test_results.json`

### Direct Observations on Schema Groups:
1. **`SessionCreateRequest` (lines 569-634)**:
   - Valid Mode A (`translation`) and Mode B (`situation_image`) payloads validate successfully.
   - Invalid modes (`arcade`, `speed`, `""`, `123`) correctly rejected.
   - Timers `15`, `30`, `60`, and `null` validate successfully.
   - Invalid timers (`45`, `0`, `-10`, `120`, `"30"`, `15.5`) correctly rejected.
   - Word limit boundary constraints strictly enforced: `target_word_count` min 3, max 50 (values 3, 10, 50 passed; values 2, 0, -5, 51, 100 rejected).
   - Margin buffer boundaries strictly enforced: `margin_buffer` min 0, max 15 (values 0, 5, 15 passed; values -1, 16, 25 rejected).
   - Language code regex `^[a-z]{2}(-[A-Z]{2})?$` strictly enforced: `ru`, `en`, `uz`, `en-US`, `es-ES` passed; `RUS`, `en_US`, `english`, `12`, `en-us` rejected.
   - Preferred style enum strictly enforced (`conversational`, `formal`, `concise`, `academic`, `business` passed; `slang` rejected).

2. **`EvaluationRequest` (lines 746-777)**:
   - Required fields (`user_text`, `time_spent_ms`, `words_typed`) enforced.
   - `user_text` bounds strictly enforced: empty string `""` rejected (minLength 1); 1000 chars passed; 1001 chars rejected (maxLength 1000).
   - Negative numbers strictly rejected: `time_spent_ms: -1` and `words_typed: -1` rejected (minimum 0).

3. **`GrammarErrorSpan` (lines 778-815)**:
   - Required fields (`start`, `end`, `original_text`, `message`, `suggestion`, `category`, `severity`) enforced.
   - 0-based indexing strictly enforced: negative start `-1` and negative end `-1` rejected (minimum 0).
   - Category enum (`grammar`, `spelling`, `punctuation`, `syntax`, `word_choice`, `agreement`, `tense`) strictly enforced; invalid category `vocabulary` rejected.
   - Severity enum (`error`, `warning`, `info`) strictly enforced; invalid severity `critical` rejected.

4. **`StyleAlternative` (lines 843-861)**:
   - Required fields (`style`, `text`, `explanation`) strictly enforced.
   - Style enum strictly enforced; invalid style `poetic` rejected.
   - Verifies exactly one alternative sentence format.

5. **`LatencyBenchmarkResponse` & `LatencyBreakdown` (lines 911-928, 1320-1362)**:
   - Required fields (`timestamp`, `iterations`, `ttft_ms`, `inference_duration_ms`, `pipeline_duration_ms`, `meets_constraint`) enforced.
   - `LatencyPercentiles` requires `min`, `max`, `avg`, `p95`; payloads missing `p95` rejected.
   - `meets_constraint` boolean property verified.

6. **Defect in `SSEStreamEvent` (lines 1031-1096)**:
   - `SSEStreamEvent.properties.event` has enum `['session_start', 'token', 'grammar_errors', 'semantic_check', 'style_alternative', 'metrics', 'done', 'error']`.
   - `SSEStreamEvent.properties.data` specifies `oneOf` with 10 candidate subschemas.
   - Verbatim test failures from `python empirical_stress_test.py`:
     ```
     [-] [SSEStreamEvent (Real-world valid payloads)] Event 'session_start' validation against SSEStreamEvent
         Expected valid: True, Got: False
         Error: {'session_id': '123e4567-e89b-12d3-a456-426614174000', 'status': 'active'} is valid under each of {'$ref': '#/components/schemas/SSETokenPayload'}, {'type': 'object', 'properties': {'errors': {'type': 'array', 'items': {'$ref': '#/components/schemas/GrammarErrorSpan'}}}}, {'$ref': '#/components/schemas/SSESessionStartPayload'} (path: ['data'])

     [-] [SSEStreamEvent (Real-world valid payloads)] Event 'token' validation against SSEStreamEvent
         Expected valid: True, Got: False
         Error: {'text': 'Hello ', 'index': 0} is valid under each of {'type': 'object', 'properties': {'errors': {'type': 'array', 'items': {'$ref': '#/components/schemas/GrammarErrorSpan'}}}}, {'$ref': '#/components/schemas/SSETokenPayload'} (path: ['data'])

     [-] [SSEStreamEvent (Real-world valid payloads)] Event 'semantic_check' validation against SSEStreamEvent
         Expected valid: True, Got: False
         Error: {'is_valid': True, 'score': 95.0, 'explanation': 'Accurate', 'missing_concepts': []} is valid under each of {'type': 'object', 'properties': {'errors': {'type': 'array', 'items': {'$ref': '#/components/schemas/GrammarErrorSpan'}}}}, {'$ref': '#/components/schemas/SemanticValidation'}, {'$ref': '#/components/schemas/SSETokenPayload'} (path: ['data'])

     [-] [SSEStreamEvent (Real-world valid payloads)] Event 'style_alternative' validation against SSEStreamEvent
         Expected valid: True, Got: False
         Error: {'style': 'formal', 'text': 'Good day to you.', 'explanation': 'Formal greeting'} is valid under each of {'type': 'object', 'properties': {'errors': {'type': 'array', 'items': {'$ref': '#/components/schemas/GrammarErrorSpan'}}}}, {'$ref': '#/components/schemas/StyleAlternative'}, {'$ref': '#/components/schemas/SSETokenPayload'} (path: ['data'])

     [-] [SSEStreamEvent (Real-world valid payloads)] Event 'metrics' validation against SSEStreamEvent
         Expected valid: True, Got: False
         Error: {'wpm': 55.0, 'accuracy_score': 95.0, 'time_spent_ms': 4000, 'word_count': 6} is valid under each of {'type': 'object', 'properties': {'errors': {'type': 'array', 'items': {'$ref': '#/components/schemas/GrammarErrorSpan'}}}}, {'$ref': '#/components/schemas/SessionMetrics'}, {'$ref': '#/components/schemas/SSETokenPayload'} (path: ['data'])

     [-] [SSEStreamEvent (Real-world valid payloads)] Event 'done' validation against SSEStreamEvent
         Expected valid: True, Got: False
         Error: {'latency': {'ttft_ms': 350.0, 'inference_duration_ms': 1200.0, 'pipeline_duration_ms': 1500.0}} is valid under each of {'type': 'object', 'properties': {'errors': {'type': 'array', 'items': {'$ref': '#/components/schemas/GrammarErrorSpan'}}}}, {'$ref': '#/components/schemas/SSEDonePayload'}, {'$ref': '#/components/schemas/SSETokenPayload'} (path: ['data'])

     [-] [SSEStreamEvent (Real-world valid payloads)] Event 'error' validation against SSEStreamEvent
         Expected valid: True, Got: False
         Error: {'code': 'LLM_TIMEOUT', 'message': 'Inference exceeded SLA deadline of 3.0 seconds'} is valid under each of {'type': 'object', 'properties': {'errors': {'type': 'array', 'items': {'$ref': '#/components/schemas/GrammarErrorSpan'}}}}, {'$ref': '#/components/schemas/ErrorResponse'}, {'$ref': '#/components/schemas/SSETokenPayload'} (path: ['data'])
     ```

## 2. Logic Chain
1. In JSON Schema Draft 2020-12 (and OpenAPI 3.1.0), the keyword `oneOf` requires that a validated JSON value MUST match **exactly one** of the subschemas.
2. In `contracts/api_v1.json`, `components.schemas.SSETokenPayload` (lines 997-1013) defines an object with optional properties (`text`, `token`, `index`) and **no `required` array**. By definition of JSON Schema, an object with no required properties and default `additionalProperties: true` matches **every possible JSON object**.
3. In `contracts/api_v1.json`, candidate 4 of `SSEStreamEvent.properties.data.oneOf` (lines 1065-1075) defines `{ "type": "object", "properties": { "errors": ... } }` with **no `required` array**. It also matches **every possible JSON object**.
4. Consequently, when an event payload for `session_start`, `semantic_check`, `style_alternative`, `metrics`, `done`, or `error` is sent, it matches its designated schema, BUT also matches `SSETokenPayload` and candidate 4 simultaneously (3 matches total).
5. Because 3 subschemas match simultaneously, JSON Schema validation fails with `is valid under each of ...`.
6. Empirical verification in `test_hypotheses.py` proved that replacing `oneOf` with `anyOf` in `SSEStreamEvent.properties.data` completely resolves this defect, resulting in a 100% pass rate (9/9 SSE event types validating cleanly).

## 3. Caveats
- No caveats. The issue was reproduced and confirmed empirically across multiple test runs using Python 3.14 standard `jsonschema` library.

## 4. Conclusion & Explicit Verdict
- **Verdict**: **`REJECT`**
- **Rationale**: While all endpoint request/response models (`SessionCreateRequest`, `EvaluationRequest`, `GrammarErrorSpan`, `StyleAlternative`, `LatencyBenchmarkResponse`, `UserProfile`, etc.) have excellent and robust constraints, the core real-time streaming schema `SSEStreamEvent` is broken under standard JSON Schema / OpenAPI 3.1 validation due to the `oneOf` multi-match collision.
- **Actionable Fix for Worker 1**:
  In `contracts/api_v1.json` at line 1052, change:
  ```json
  "data": {
    "description": "JSON-encoded payload corresponding to event name",
    "oneOf": [
  ```
  to:
  ```json
  "data": {
    "description": "JSON-encoded payload corresponding to event name",
    "anyOf": [
  ```
  Additionally, add `"required": ["errors"]` to candidate 4 (line 1066) and ensure `SSETokenPayload` specifies `"required": ["text"]` (or `"anyOf": [{"required": ["text"]}, {"required": ["token"]}]`).

## 5. Verification Method
1. Run the empirical test suite:
   ```powershell
   python empirical_stress_test.py
   ```
2. Inspect the test failure log:
   ```powershell
   python -c "import json; res = json.load(open('test_results.json')); print('Total:', len(res), 'Passed:', sum(1 for r in res if r['passed']), 'Failed:', sum(1 for r in res if not r['passed']))"
   ```
3. Test hypothesis verification script:
   ```powershell
   python test_hypotheses.py
   ```
4. Invalidation condition: `python empirical_stress_test.py` reports 0 failed assertions once `anyOf` is adopted in `contracts/api_v1.json`.
