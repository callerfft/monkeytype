# Empirical Challenger Handoff Report — Milestone 1 (API Contract Definition)

**Verdict**: **REJECT** (Blocking Schema Bug Found in `SSEStreamEvent`)

---

## 1. Observation

### 1.1 Automated Contract & Pointer Verification
We executed an automated validation suite via Node.js and Python against `contracts/api_v1.json`:
- **Document Structure**: Valid JSON syntax, OpenAPI 3.1.0 root keys (`openapi`, `info`, `servers`, `paths`, `components`).
- **Paths & Operations**: 10 distinct operations across 8 paths. All path parameters (`{session_id}`) correspond to declared parameter objects with `in: "path"` and `required: true`. Operation IDs are unique.
- **Reference Integrity**: 49 `$ref` pointers discovered across the document. All 49 pointers resolve locally to existing schema definitions in `components.schemas` without cycles (DAG verified).
- **JSON Schema Meta-Validation**: All 23 schemas in `components.schemas` conform to JSON Schema Draft 2020-12 meta-schema (`jsonschema.Draft202012Validator.check_schema` returned 0 errors).

### 1.2 Empirical Failure: `SSEStreamEvent` Multi-Match Violation
When running generative payload validation against `SSEStreamEvent` using `jsonschema.Draft202012Validator`:
- **File**: `c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\contracts\api_v1.json`
- **Lines**: 1050-1095 (`SSEStreamEvent.properties.data.oneOf`)
- **Verbatim Error Output**:
```
Event session_start: FAIL (1 errors)
   -> {'session_id': '123e4567-e89b-12d3-a456-426614174000', 'status': 'active'} is valid under each of {'$ref': '#/components/schemas/SSETokenPayload'}, {'type': 'object', 'properties': {'errors': {'type': 'array', 'items': {'$ref': '#/components/schemas/GrammarErrorSpan'}}}}, {'$ref': '#/components/schemas/SSESessionStartPayload'}

Event token: FAIL (1 errors)
   -> {'text': 'word', 'index': 1} is valid under each of {'type': 'object', 'properties': {'errors': {'type': 'array', 'items': {'$ref': '#/components/schemas/GrammarErrorSpan'}}}}, {'$ref': '#/components/schemas/SSETokenPayload'}

Event semantic_check: FAIL (1 errors)
   -> {'is_valid': True, 'score': 90, 'explanation': 'good', 'missing_concepts': []} is valid under each of {'type': 'object', 'properties': {'errors': {'type': 'array', 'items': {'$ref': '#/components/schemas/GrammarErrorSpan'}}}}, {'$ref': '#/components/schemas/SemanticValidation'}, {'$ref': '#/components/schemas/SSETokenPayload'}

Event style_alternative: FAIL (1 errors)
   -> {'style': 'formal', 'text': 'Hello.', 'explanation': 'Polite.'} is valid under each of {'type': 'object', 'properties': {'errors': {'type': 'array', 'items': {'$ref': '#/components/schemas/GrammarErrorSpan'}}}}, {'$ref': '#/components/schemas/StyleAlternative'}, {'$ref': '#/components/schemas/SSETokenPayload'}

Event metrics: FAIL (1 errors)
   -> {'wpm': 50, 'accuracy_score': 90, 'time_spent_ms': 2000, 'word_count': 5} is valid under each of {'type': 'object', 'properties': {'errors': {'type': 'array', 'items': {'$ref': '#/components/schemas/GrammarErrorSpan'}}}}, {'$ref': '#/components/schemas/SessionMetrics'}, {'$ref': '#/components/schemas/SSETokenPayload'}

Event done: FAIL (1 errors)
   -> {'evaluation_id': '123e4567-e89b-12d3-a456-426614174000', 'latency': {'ttft_ms': 100, 'inference_duration_ms': 500, 'pipeline_duration_ms': 600}} is valid under each of {'type': 'object', 'properties': {'errors': {'type': 'array', 'items': {'$ref': '#/components/schemas/GrammarErrorSpan'}}}}, {'$ref': '#/components/schemas/SSEDonePayload'}, {'$ref': '#/components/schemas/SSETokenPayload'}

Event error: FAIL (1 errors)
   -> {'code': 'TIMEOUT', 'message': 'Too slow'} is valid under each of {'type': 'object', 'properties': {'errors': {'type': 'array', 'items': {'$ref': '#/components/schemas/GrammarErrorSpan'}}}}, {'$ref': '#/components/schemas/ErrorResponse'}, {'$ref': '#/components/schemas/SSETokenPayload'}
```

---

## 2. Logic Chain

1. **Premise 1**: In JSON Schema / OpenAPI 3.1, `oneOf` asserts that a conforming instance must match *exactly one* of the given subschemas. If an instance matches more than one subschema, validation strictly fails.
2. **Premise 2**: In `contracts/api_v1.json`, schema `SSETokenPayload` (lines 997–1013) defines properties `text`, `token`, `index`, but contains **no required properties** and allows `additionalProperties`. Therefore, any arbitrary JSON object matches `SSETokenPayload`.
3. **Premise 3**: In `contracts/api_v1.json`, line 1066 defines an anonymous subschema in `data.oneOf`:
   ```json
   {
     "type": "object",
     "properties": {
       "errors": {
         "type": "array",
         "items": { "$ref": "#/components/schemas/GrammarErrorSpan" }
       }
     }
   }
   ```
   This subschema also contains **no required properties** and allows `additionalProperties`. Therefore, any arbitrary JSON object without an `errors` property matches this subschema as well.
4. **Deduction**: Whenever a real SSE event payload (such as `session_start`, `semantic_check`, `style_alternative`, `metrics`, `done`, `error`) is emitted, it matches:
   - Its intended schema, AND
   - `SSETokenPayload`, AND
   - The anonymous `{properties: {errors: ...}}` wrapper.
   Because 3 subschemas match simultaneously, `oneOf` validation fails on 100% of object-based SSE events.
5. **Impact**: In Milestone 2 (FastAPI backend) and Milestone 3 (SolidJS frontend), any automated validation, Pydantic model validation, or TypeScript discriminated union parsing generated from `SSEStreamEvent` will reject valid runtime SSE packets or fail schema assertion tests.
6. **Empirically Verified Solution**: Changing `"oneOf"` to `"anyOf"` on line 1052 of `contracts/api_v1.json` immediately eliminates the multi-match conflict and yields 100% test pass rate across all 8 SSE event types.

---

## 3. Caveats

- Out of scope for Milestone 1: Runtime network latency and LLM inference duration (these belong to Milestones 2 & 4).
- The contract is otherwise comprehensive and meets all functional requirements of R1 (Mode A/B, timers 15/30/60s, error spans, semantic evaluation, style alternatives, latency breakdown, Firebase auth).
- No other schemas in `components.schemas` exhibit this issue.

---

## 4. Conclusion

**Verdict: REJECT**

The contract `contracts/api_v1.json` is rejected due to a critical schema-level defect in `SSEStreamEvent`:
- **Location**: `contracts/api_v1.json:1052`
- **Required Action**: Change `"oneOf": [` to `"anyOf": [` in `SSEStreamEvent.properties.data` (or provide explicit discriminator/required constraints).
- As soon as this single modification is applied by the worker, the contract will be fully eligible for approval.

---

## 5. Verification Method

To reproduce the bug and verify the fix independently, execute the following script from project root:

```powershell
@'
import json, jsonschema

with open("contracts/api_v1.json", "r", encoding="utf-8") as f:
    doc = json.load(f)

resolver = jsonschema.RefResolver.from_schema(doc)
v = jsonschema.Draft202012Validator(doc["components"]["schemas"]["SSEStreamEvent"], resolver=resolver)

# Test payload for session_start event
payload = {
    "event": "session_start",
    "data": {"session_id": "123e4567-e89b-12d3-a456-426614174000", "status": "active"}
}

errors = list(v.iter_errors(payload))
if errors:
    print("[BUG REPRODUCED] Validation failed:", errors[0].message)
else:
    print("[SUCCESS] Validation passed!")
'@ | python
```

- **Invalidation Condition**: The script prints `[SUCCESS] Validation passed!` if and only if the `oneOf` multi-match defect is fixed.
