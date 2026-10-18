import json
import sys
import jsonschema

def main():
    print("=== Reviewer 3 Independent Contract Remediation & Adversarial Verification ===")
    
    contract_file = "contracts/api_v1.json"
    with open(contract_file, "r", encoding="utf-8") as f:
        doc = json.load(f)
    
    schemas = doc["components"]["schemas"]
    resolver = jsonschema.RefResolver.from_schema(doc)
    validator_cls = jsonschema.Draft202012Validator
    
    passed = 0
    failed = 0
    
    def assert_check(name, condition, details=""):
        nonlocal passed, failed
        if condition:
            passed += 1
            print(f"[PASS] {name}")
        else:
            failed += 1
            print(f"[FAIL] {name}: {details}")

    # =========================================================================
    # 1. REMEDIATION POINTS VERIFICATION
    # =========================================================================
    
    # 1.1 SSETokenPayload
    token_schema = schemas.get("SSETokenPayload", {})
    assert_check(
        "Remediation 1.1: SSETokenPayload has required: ['text']",
        token_schema.get("required") == ["text"],
        f"Actual: {token_schema.get('required')}"
    )
    assert_check(
        "Remediation 1.2: SSETokenPayload has additionalProperties: False",
        token_schema.get("additionalProperties") is False,
        f"Actual: {token_schema.get('additionalProperties')}"
    )
    
    # 1.2 SSEStreamEvent data anyOf & inline errors branch
    stream_event_schema = schemas.get("SSEStreamEvent", {})
    data_prop = stream_event_schema.get("properties", {}).get("data", {})
    assert_check(
        "Remediation 2.1: SSEStreamEvent.properties.data uses anyOf",
        "anyOf" in data_prop and isinstance(data_prop["anyOf"], list),
        f"Keys in data: {list(data_prop.keys())}"
    )
    assert_check(
        "Remediation 2.2: SSEStreamEvent.properties.data has no oneOf",
        "oneOf" not in data_prop,
        "oneOf still present in data"
    )
    
    # Find inline error envelope branch
    inline_errors_branch = None
    for branch in data_prop.get("anyOf", []):
        if branch.get("type") == "object" and "errors" in branch.get("properties", {}):
            inline_errors_branch = branch
            break
            
    assert_check(
        "Remediation 2.3: Inline errors envelope branch found",
        inline_errors_branch is not None,
        "No object branch with 'errors' property found"
    )
    if inline_errors_branch:
        assert_check(
            "Remediation 2.4: Inline errors branch requires 'errors'",
            inline_errors_branch.get("required") == ["errors"],
            f"Actual required: {inline_errors_branch.get('required')}"
        )
        assert_check(
            "Remediation 2.5: Inline errors branch additionalProperties is False",
            inline_errors_branch.get("additionalProperties") is False,
            f"Actual additionalProperties: {inline_errors_branch.get('additionalProperties')}"
        )

    # 1.3 SessionMetrics.required contains "target_met"
    metrics_schema = schemas.get("SessionMetrics", {})
    metrics_required = metrics_schema.get("required", [])
    assert_check(
        "Remediation 3.1: SessionMetrics.required contains 'target_met'",
        "target_met" in metrics_required,
        f"Actual required: {metrics_required}"
    )
    assert_check(
        "Remediation 3.2: SessionMetrics properties defines target_met as boolean",
        metrics_schema.get("properties", {}).get("target_met", {}).get("type") == "boolean",
        f"Actual target_met def: {metrics_schema.get('properties', {}).get('target_met')}"
    )

    # 1.4 EvaluationRequest.properties.user_text minLength is 0
    eval_req_schema = schemas.get("EvaluationRequest", {})
    user_text_prop = eval_req_schema.get("properties", {}).get("user_text", {})
    assert_check(
        "Remediation 4.1: EvaluationRequest.properties.user_text minLength is 0",
        user_text_prop.get("minLength") == 0,
        f"Actual minLength: {user_text_prop.get('minLength')}"
    )

    # =========================================================================
    # 2. VALIDATION OF ALL 8 STANDARD SSE EVENT TYPES
    # =========================================================================
    v_sse = validator_cls(stream_event_schema, resolver=resolver)

    standard_events = [
        ("1. session_start", {
            "event": "session_start",
            "data": {
                "session_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "active"
            }
        }),
        ("2. token", {
            "event": "token",
            "data": {
                "text": "hello world",
                "index": 0
            }
        }),
        ("3a. grammar_errors (bare array)", {
            "event": "grammar_errors",
            "data": [
                {
                    "start": 0,
                    "end": 4,
                    "original_text": "Thay",
                    "message": "Possible spelling mistake",
                    "suggestion": "They",
                    "category": "spelling",
                    "severity": "error"
                }
            ]
        }),
        ("3b. grammar_errors (envelope object)", {
            "event": "grammar_errors",
            "data": {
                "errors": [
                    {
                        "start": 0,
                        "end": 4,
                        "original_text": "Thay",
                        "message": "Possible spelling mistake",
                        "suggestion": "They",
                        "category": "spelling",
                        "severity": "error"
                    }
                ]
            }
        }),
        ("4. semantic_check", {
            "event": "semantic_check",
            "data": {
                "is_valid": True,
                "score": 92.5,
                "explanation": "Adequate translation captures main ideas.",
                "missing_concepts": []
            }
        }),
        ("5. style_alternative", {
            "event": "style_alternative",
            "data": {
                "style": "formal",
                "text": "Would you be interested in participating?",
                "explanation": "More formal phrasing suitable for business context."
            }
        }),
        ("6. metrics", {
            "event": "metrics",
            "data": {
                "wpm": 72.4,
                "accuracy_score": 96.0,
                "time_spent_ms": 12500,
                "word_count": 18,
                "target_met": True
            }
        }),
        ("7. done", {
            "event": "done",
            "data": {
                "evaluation_id": "123e4567-e89b-12d3-a456-426614174000",
                "result_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "latency": {
                    "ttft_ms": 420.0,
                    "inference_duration_ms": 1200.0,
                    "pipeline_duration_ms": 1450.0
                }
            }
        }),
        ("8. error", {
            "event": "error",
            "data": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": "Too many requests. Please slow down."
            }
        })
    ]

    for label, payload in standard_events:
        errors = list(v_sse.iter_errors(payload))
        assert_check(
            f"SSE Event Validation: {label}",
            len(errors) == 0,
            f"Errors: {[e.message for e in errors]}"
        )

    # =========================================================================
    # 3. ADVERSARIAL STRESS-TESTING & BOUNDARY CHECKS
    # =========================================================================

    # Adversarial SSE Stream Checks
    adv_invalid_events = [
        ("Unknown event name", {"event": "heartbeat", "data": {"text": "ping"}}),
        ("Missing event property", {"data": {"text": "ping"}}),
        ("Missing data property", {"event": "token"}),
        ("Data is string not object/array", {"event": "token", "data": "plain text"}),
        ("Data is null", {"event": "token", "data": None}),
        ("Token data missing 'text'", {"event": "token", "data": {"index": 1}}),
        ("Token data has unknown property", {"event": "token", "data": {"text": "hi", "foo": "bar"}}),
        ("Inline error envelope with unknown property", {"event": "grammar_errors", "data": {"errors": [], "extra": 1}}),
        ("Inline error envelope missing 'errors'", {"event": "grammar_errors", "data": {"not_errors": []}}),
    ]

    for desc, payload in adv_invalid_events:
        errors = list(v_sse.iter_errors(payload))
        assert_check(
            f"Adversarial Rejection: {desc}",
            len(errors) > 0,
            "Expected failure but payload passed!"
        )

    # SessionMetrics Boundary Checks
    v_metrics = validator_cls(metrics_schema, resolver=resolver)
    assert_check(
        "Metrics: Valid with target_met=True",
        v_metrics.is_valid({"wpm": 50.0, "accuracy_score": 90.0, "time_spent_ms": 5000, "word_count": 10, "target_met": True})
    )
    assert_check(
        "Metrics: Valid with target_met=False",
        v_metrics.is_valid({"wpm": 20.0, "accuracy_score": 70.0, "time_spent_ms": 5000, "word_count": 5, "target_met": False})
    )
    assert_check(
        "Metrics: Missing target_met is rejected",
        not v_metrics.is_valid({"wpm": 50.0, "accuracy_score": 90.0, "time_spent_ms": 5000, "word_count": 10})
    )
    assert_check(
        "Metrics: Non-boolean target_met is rejected",
        not v_metrics.is_valid({"wpm": 50.0, "accuracy_score": 90.0, "time_spent_ms": 5000, "word_count": 10, "target_met": "yes"})
    )
    assert_check(
        "Metrics: Negative WPM is rejected",
        not v_metrics.is_valid({"wpm": -5.0, "accuracy_score": 90.0, "time_spent_ms": 5000, "word_count": 10, "target_met": True})
    )
    assert_check(
        "Metrics: Accuracy > 100 is rejected",
        not v_metrics.is_valid({"wpm": 50.0, "accuracy_score": 105.0, "time_spent_ms": 5000, "word_count": 10, "target_met": True})
    )

    # EvaluationRequest Boundary Checks
    v_eval = validator_cls(eval_req_schema, resolver=resolver)
    assert_check(
        "EvalRequest: Empty string user_text (minLength: 0) is valid",
        v_eval.is_valid({"user_text": "", "time_spent_ms": 15000, "words_typed": 0})
    )
    assert_check(
        "EvalRequest: 1000 char user_text is valid",
        v_eval.is_valid({"user_text": "a" * 1000, "time_spent_ms": 30000, "words_typed": 100})
    )
    assert_check(
        "EvalRequest: 1001 char user_text is rejected",
        not v_eval.is_valid({"user_text": "a" * 1001, "time_spent_ms": 30000, "words_typed": 100})
    )
    assert_check(
        "EvalRequest: Negative time_spent_ms is rejected",
        not v_eval.is_valid({"user_text": "abc", "time_spent_ms": -1, "words_typed": 1})
    )
    assert_check(
        "EvalRequest: Negative words_typed is rejected",
        not v_eval.is_valid({"user_text": "abc", "time_spent_ms": 100, "words_typed": -1})
    )

    # Reference Resolution Audit
    dollar_ref = "$ref"
    all_refs = []
    def extract_refs(o):
        if isinstance(o, dict):
            for k, val in o.items():
                if k == dollar_ref and isinstance(val, str):
                    all_refs.append(val)
                else:
                    extract_refs(val)
        elif isinstance(o, list):
            for item in o:
                extract_refs(item)
    extract_refs(doc)
    
    broken_refs = []
    for r in all_refs:
        if r.startswith("#/components/schemas/"):
            schema_name = r.replace("#/components/schemas/", "")
            if schema_name not in schemas:
                broken_refs.append(r)
        else:
            broken_refs.append(r)

    assert_check(
        f"All {len(all_refs)} $ref references resolve (0 broken)",
        len(broken_refs) == 0,
        f"Broken refs: {broken_refs}"
    )

    print("\n" + "="*50)
    print(f"Total verification checks: {passed + failed}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print("="*50)

    if failed > 0:
        print("\nVERIFICATION FAILED")
        sys.exit(1)
    else:
        print("\nALL REVIEWER 3 VERIFICATIONS PASSED (100% SUCCESS)")

if __name__ == "__main__":
    main()
