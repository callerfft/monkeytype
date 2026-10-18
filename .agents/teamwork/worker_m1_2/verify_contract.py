import json
import jsonschema
import sys

def main():
    print("=== Contract Verification Suite: Worker M1-2 ===")
    
    with open("contracts/api_v1.json", "r", encoding="utf-8") as f:
        doc = json.load(f)
    
    schemas = doc["components"]["schemas"]
    resolver = jsonschema.RefResolver.from_schema(doc)
    validator_cls = jsonschema.Draft202012Validator
    
    passed = 0
    failed = 0
    
    def check(name, condition, msg=""):
        nonlocal passed, failed
        if condition:
            passed += 1
            print(f"[PASS] {name}")
        else:
            failed += 1
            print(f"[FAIL] {name}: {msg}")

    # 1. Structural Checks
    check("Root OpenAPI 3.1.0", doc.get("openapi") == "3.1.0")
    check("All 23 schemas present", len(schemas) == 23)
    
    # 2. Fix 1: SSETokenPayload checks
    token_schema = schemas["SSETokenPayload"]
    check("SSETokenPayload requires 'text'", token_schema.get("required") == ["text"])
    check("SSETokenPayload additionalProperties is False", token_schema.get("additionalProperties") is False)
    
    v_token = validator_cls(token_schema, resolver=resolver)
    check("Valid SSETokenPayload passes", v_token.is_valid({"text": "sample token", "index": 0}))
    check("SSETokenPayload missing text fails", not v_token.is_valid({"index": 0}))
    check("SSETokenPayload empty object fails", not v_token.is_valid({}))
    check("SSETokenPayload additional properties fail", not v_token.is_valid({"text": "sample", "extra": 123}))

    # 3. Fix 2: SSEStreamEvent.properties.data checks
    sse_schema = schemas["SSEStreamEvent"]
    data_prop = sse_schema["properties"]["data"]
    check("SSEStreamEvent data has 'anyOf'", "anyOf" in data_prop)
    check("SSEStreamEvent data does not have 'oneOf'", "oneOf" not in data_prop)
    
    # Check inline errors subschema
    inline_errors_branch = None
    for b in data_prop["anyOf"]:
        if b.get("type") == "object" and "errors" in b.get("properties", {}):
            inline_errors_branch = b
            break
    check("Inline errors branch found", inline_errors_branch is not None)
    if inline_errors_branch:
        check("Inline errors branch requires 'errors'", inline_errors_branch.get("required") == ["errors"])
        check("Inline errors branch additionalProperties is False", inline_errors_branch.get("additionalProperties") is False)

    v_sse = validator_cls(sse_schema, resolver=resolver)
    
    events_to_test = [
        ("session_start", {"session_id": "123e4567-e89b-12d3-a456-426614174000", "status": "active"}),
        ("token", {"text": "hello", "index": 0}),
        ("grammar_errors (bare array)", [{"start": 0, "end": 4, "original_text": "Thay", "message": "typo", "suggestion": "They", "category": "spelling", "severity": "error"}]),
        ("grammar_errors (envelope object)", {"errors": [{"start": 0, "end": 4, "original_text": "Thay", "message": "typo", "suggestion": "They", "category": "spelling", "severity": "error"}]}),
        ("semantic_check", {"is_valid": True, "score": 95.0, "explanation": "accurate", "missing_concepts": []}),
        ("style_alternative", {"style": "formal", "text": "Greetings", "explanation": "Polite form"}),
        ("metrics", {"wpm": 65.0, "accuracy_score": 98.0, "time_spent_ms": 4000, "word_count": 8, "target_met": True}),
        ("done", {"evaluation_id": "123e4567-e89b-12d3-a456-426614174000", "latency": {"ttft_ms": 300.0, "inference_duration_ms": 1000.0, "pipeline_duration_ms": 1300.0}}),
        ("error", {"code": "VALIDATION_ERROR", "message": "Failed validation"}),
    ]
    
    for ev_name, ev_data in events_to_test:
        raw_event = ev_name.split()[0]
        event_obj = {"event": raw_event, "data": ev_data}
        check(f"SSEStreamEvent payload '{ev_name}' passes", v_sse.is_valid(event_obj))

    # Test invalid SSE events fail
    check("SSEStreamEvent invalid event name fails", not v_sse.is_valid({"event": "unknown_event", "data": {"text": "hi"}}))
    check("SSEStreamEvent missing event fails", not v_sse.is_valid({"data": {"text": "hi"}}))
    check("SSEStreamEvent missing data fails", not v_sse.is_valid({"event": "token"}))

    # 4. Fix 3: SessionMetrics checks
    metrics_schema = schemas["SessionMetrics"]
    check("'target_met' in SessionMetrics.required", "target_met" in metrics_schema.get("required", []))
    v_metrics = validator_cls(metrics_schema, resolver=resolver)
    valid_metrics_base = {
        "wpm": 60.0,
        "accuracy_score": 95.0,
        "time_spent_ms": 10000,
        "word_count": 15,
        "target_met": True
    }
    check("Valid SessionMetrics with target_met: True passes", v_metrics.is_valid(valid_metrics_base))
    valid_metrics_false = dict(valid_metrics_base, target_met=False)
    check("Valid SessionMetrics with target_met: False passes", v_metrics.is_valid(valid_metrics_false))
    missing_target_met = {k: v for k, v in valid_metrics_base.items() if k != "target_met"}
    check("SessionMetrics missing target_met fails", not v_metrics.is_valid(missing_target_met))

    # 5. Fix 4: EvaluationRequest checks
    eval_schema = schemas["EvaluationRequest"]
    user_text_prop = eval_schema["properties"]["user_text"]
    check("EvaluationRequest user_text minLength is 0", user_text_prop.get("minLength") == 0)
    v_eval = validator_cls(eval_schema, resolver=resolver)
    check("EvaluationRequest with empty text (timer expired) passes", v_eval.is_valid({"user_text": "", "time_spent_ms": 15000, "words_typed": 0}))
    check("EvaluationRequest with normal text passes", v_eval.is_valid({"user_text": "Hello world", "time_spent_ms": 5000, "words_typed": 2}))
    check("EvaluationRequest exceeding 1000 chars fails", not v_eval.is_valid({"user_text": "a" * 1001, "time_spent_ms": 5000, "words_typed": 1}))

    print(f"\nTotal checks: {passed + failed}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed > 0:
        sys.exit(1)
    else:
        print("\nALL VERIFICATIONS PASSED (100% SUCCESS)")

if __name__ == "__main__":
    main()
