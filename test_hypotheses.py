import json
import copy
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

with open("contracts/api_v1.json", "r", encoding="utf-8") as f:
    doc = json.load(f)

# Hypothesis 1: Replace oneOf with anyOf in SSEStreamEvent.data
doc_anyof = copy.deepcopy(doc)
data_schema = doc_anyof["components"]["schemas"]["SSEStreamEvent"]["properties"]["data"]
data_schema["anyOf"] = data_schema.pop("oneOf")

res_anyof = Resource.from_contents(doc_anyof, default_specification=DRAFT202012)
reg_anyof = Registry().with_resource("http://example.com/api_v1.json", res_anyof)
v_anyof = Draft202012Validator({
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$ref": "http://example.com/api_v1.json#/components/schemas/SSEStreamEvent"
}, registry=reg_anyof)

events = [
    ("session_start", {"session_id": "123e4567-e89b-12d3-a456-426614174000", "status": "active"}),
    ("token", {"text": "Hello ", "index": 0}),
    ("grammar_errors", [{"start": 0, "end": 4, "original_text": "Heey", "message": "err", "suggestion": "Hey", "category": "spelling", "severity": "warning"}]),
    ("grammar_errors_obj", {"errors": [{"start": 0, "end": 4, "original_text": "Heey", "message": "err", "suggestion": "Hey", "category": "spelling", "severity": "warning"}]}),
    ("semantic_check", {"is_valid": True, "score": 95.0, "explanation": "Accurate", "missing_concepts": []}),
    ("style_alternative", {"style": "formal", "text": "Good day.", "explanation": "Formal"}),
    ("metrics", {"wpm": 55.0, "accuracy_score": 95.0, "time_spent_ms": 4000, "word_count": 6}),
    ("done", {"latency": {"ttft_ms": 350.0, "inference_duration_ms": 1200.0, "pipeline_duration_ms": 1500.0}}),
    ("error", {"code": "LLM_TIMEOUT", "message": "Timeout exceeded"}),
]

print("--- Testing Hypothesis 1: anyOf instead of oneOf in data ---")
all_passed = True
for ev, data in events:
    event_type = ev.split("_obj")[0]
    payload = {"event": event_type, "data": data}
    errs = list(v_anyof.iter_errors(payload))
    res = "PASS" if not errs else "FAIL: " + str(errs[0].message)
    print(f" - {ev}: {res}")
    if errs:
        all_passed = False
print("Hypothesis 1 (anyOf) all passed:", all_passed)

# Hypothesis 2: Keeping oneOf but fixing schemas to be mutually exclusive:
# - SSETokenPayload requires text or token
# - subschema 4 requires errors
# - SSETokenPayload / other objects use additionalProperties or discriminator
doc_fixed_oneof = copy.deepcopy(doc)
# Require errors in subschema 4
doc_fixed_oneof["components"]["schemas"]["SSEStreamEvent"]["properties"]["data"]["oneOf"][3]["required"] = ["errors"]
# In SSETokenPayload, require at least one property or text
doc_fixed_oneof["components"]["schemas"]["SSETokenPayload"]["anyOf"] = [
    {"required": ["text"]},
    {"required": ["token"]}
]

res_h2 = Resource.from_contents(doc_fixed_oneof, default_specification=DRAFT202012)
reg_h2 = Registry().with_resource("http://example.com/api_v1.json", res_h2)
v_h2 = Draft202012Validator({
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$ref": "http://example.com/api_v1.json#/components/schemas/SSEStreamEvent"
}, registry=reg_h2)

print("\n--- Testing Hypothesis 2: oneOf with required properties on SSETokenPayload and subschema 4 ---")
all_passed_h2 = True
for ev, data in events:
    event_type = ev.split("_obj")[0]
    payload = {"event": event_type, "data": data}
    errs = list(v_h2.iter_errors(payload))
    res = "PASS" if not errs else "FAIL: " + str(errs[0].message)
    print(f" - {ev}: {res}")
    if errs:
        all_passed_h2 = False
print("Hypothesis 2 (oneOf tightened) all passed:", all_passed_h2)
