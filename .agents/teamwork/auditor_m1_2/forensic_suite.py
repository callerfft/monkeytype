import json
import re
import sys
import traceback
import jsonschema

def run_audit():
    try:
        contract_path = r"c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\contracts\api_v1.json"
        print(f"[*] Auditing contract: {contract_path}")

        with open(contract_path, "r", encoding="utf-8") as f:
            raw_text = f.read()

        # 1. Structural & Syntax Check + Duplicate Keys
        duplicate_keys = []
        def check_duplicate_keys(pairs):
            seen = set()
            d = {}
            for k, v in pairs:
                if k in seen:
                    duplicate_keys.append(k)
                seen.add(k)
                d[k] = v
            return d

        doc = json.loads(raw_text, object_pairs_hook=check_duplicate_keys)
        print(f"[+] JSON loaded successfully. Root keys: {list(doc.keys())}")
        assert len(duplicate_keys) == 0, f"Duplicate keys found: {duplicate_keys}"
        print(f"[PASS] Duplicate keys check: 0 duplicate keys found.")

        # 2. Hardcoded / Facade Scan
        banned_keywords = ["TODO", "FIXME", "TBD", "placeholder", "dummy", "lorem ipsum", "asdf"]
        found_banned = []
        for kw in banned_keywords:
            matches = re.findall(rf"\b{kw}\b", raw_text, re.IGNORECASE)
            if matches:
                found_banned.append((kw, len(matches)))
        assert len(found_banned) == 0, f"Banned facade keywords found: {found_banned}"
        print(f"[PASS] Facade keywords check: 0 banned keywords found.")

        # 3. Schema component count
        schemas = doc.get("components", {}).get("schemas", {})
        print(f"[+] Total schemas in components: {len(schemas)}")
        assert len(schemas) == 23, f"Expected 23 schemas, found {len(schemas)}"

        # 4. $ref Resolution Integrity
        refs = []
        def extract_refs(obj, p=""):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k == "$ref":
                        refs.append((p, v))
                    else:
                        extract_refs(v, f"{p}.{k}")
            elif isinstance(obj, list):
                for i, it in enumerate(obj):
                    extract_refs(it, f"{p}[{i}]")

        extract_refs(doc, "root")
        print(f"[+] Found {len(refs)} $ref pointers.")
        broken_refs = []
        for path, ref in refs:
            if ref.startswith("#/components/schemas/"):
                schema_name = ref.replace("#/components/schemas/", "")
                if schema_name not in schemas:
                    broken_refs.append((path, ref))
            else:
                broken_refs.append((path, ref))
        assert len(broken_refs) == 0, f"Broken $ref pointers: {broken_refs}"
        print(f"[PASS] All {len(refs)} $ref pointers resolve locally (0 broken).")

        # 5. Inspection of Remediation Fixes
        # Fix 1: SSETokenPayload
        token_schema = schemas.get("SSETokenPayload", {})
        assert token_schema.get("required") == ["text"], f"SSETokenPayload required mismatch: {token_schema.get('required')}"
        assert token_schema.get("additionalProperties") is False, f"SSETokenPayload additionalProperties is not False: {token_schema.get('additionalProperties')}"
        print(f"[PASS] Fix 1 verified: SSETokenPayload required=['text'] and additionalProperties=False.")

        # Fix 2: SSEStreamEvent.properties.data
        sse_schema = schemas.get("SSEStreamEvent", {})
        data_schema = sse_schema.get("properties", {}).get("data", {})
        assert "anyOf" in data_schema, "SSEStreamEvent.properties.data does not have anyOf"
        assert "oneOf" not in data_schema, "SSEStreamEvent.properties.data still has oneOf"
        any_of_branches = data_schema.get("anyOf", [])
        inline_errors_branch = None
        for b in any_of_branches:
            if b.get("type") == "object" and "errors" in b.get("properties", {}):
                inline_errors_branch = b
                break
        assert inline_errors_branch is not None, "Inline errors branch not found in anyOf"
        assert inline_errors_branch.get("required") == ["errors"], f"Inline errors branch required mismatch: {inline_errors_branch.get('required')}"
        assert inline_errors_branch.get("additionalProperties") is False, f"Inline errors branch additionalProperties is not False: {inline_errors_branch.get('additionalProperties')}"
        print(f"[PASS] Fix 2 verified: SSEStreamEvent uses anyOf (oneOf removed), inline errors branch requires ['errors'] with additionalProperties=False.")

        # Fix 3: SessionMetrics.required
        metrics_schema = schemas.get("SessionMetrics", {})
        assert "target_met" in metrics_schema.get("required", []), f"'target_met' not in SessionMetrics.required: {metrics_schema.get('required')}"
        print(f"[PASS] Fix 3 verified: 'target_met' is in SessionMetrics.required.")

        # Fix 4: EvaluationRequest.properties.user_text minLength
        eval_req_schema = schemas.get("EvaluationRequest", {})
        user_text_prop = eval_req_schema.get("properties", {}).get("user_text", {})
        assert user_text_prop.get("minLength") == 0, f"EvaluationRequest user_text minLength is not 0: {user_text_prop.get('minLength')}"
        assert user_text_prop.get("maxLength") == 1000, f"EvaluationRequest user_text maxLength is not 1000: {user_text_prop.get('maxLength')}"
        print(f"[PASS] Fix 4 verified: EvaluationRequest.user_text minLength=0, maxLength=1000.")

        # 6. Behavioral Validation Engine Setup
        resolver = jsonschema.RefResolver.from_schema(doc)
        validator_cache = {}

        def get_validator(schema_name):
            if schema_name not in validator_cache:
                sub = schemas[schema_name]
                validator_cache[schema_name] = jsonschema.Draft202012Validator(sub, resolver=resolver)
            return validator_cache[schema_name]

        v_sse = get_validator("SSEStreamEvent")
        v_token = get_validator("SSETokenPayload")
        v_metrics = get_validator("SessionMetrics")
        v_eval = get_validator("EvaluationRequest")
        v_session = get_validator("SessionCreateRequest")

        # 7. Behavioral Tests on Valid SSE Payloads (Including target_met)
        valid_sse_events = [
            ("session_start", "session_start", {"session_id": "123e4567-e89b-12d3-a456-426614174000", "status": "active"}),
            ("token", "token", {"text": "hello", "index": 0}),
            ("grammar_errors", "grammar_errors", [{"start": 0, "end": 4, "original_text": "Heey", "message": "Typo", "suggestion": "Hey", "category": "spelling", "severity": "warning"}]),
            ("grammar_errors_wrapped", "grammar_errors", {"errors": [{"start": 0, "end": 4, "original_text": "Heey", "message": "Typo", "suggestion": "Hey", "category": "spelling", "severity": "warning"}]}),
            ("semantic_check", "semantic_check", {"is_valid": True, "score": 92.5, "explanation": "Adequate translation", "missing_concepts": []}),
            ("style_alternative", "style_alternative", {"style": "formal", "text": "Good evening.", "explanation": "More polite phrasing"}),
            ("metrics", "metrics", {"wpm": 62.0, "accuracy_score": 97.5, "time_spent_ms": 3200, "word_count": 8, "target_met": True}),
            ("metrics_target_false", "metrics", {"wpm": 40.0, "accuracy_score": 85.0, "time_spent_ms": 6000, "word_count": 4, "target_met": False}),
            ("done", "done", {"evaluation_id": "123e4567-e89b-12d3-a456-426614174000", "latency": {"ttft_ms": 320.0, "inference_duration_ms": 1100.0, "pipeline_duration_ms": 1400.0}}),
            ("error", "error", {"code": "LLM_TIMEOUT", "message": "Inference deadline exceeded"})
        ]

        for label, ev_name, payload in valid_sse_events:
            full_event = {"event": ev_name, "data": payload}
            errors = list(v_sse.iter_errors(full_event))
            assert len(errors) == 0, f"Valid SSE payload '{label}' failed validation: {[e.message for e in errors]}"
            print(f"[PASS] Behavioral SSE event '{label}' accepted.")

        # 8. Adversarial Stress-Testing (Rejecting Malformed / Ambiguous Payloads)
        # A. SSETokenPayload strictness
        assert len(list(v_token.iter_errors({"text": "hello"}))) == 0
        assert len(list(v_token.iter_errors({"index": 0}))) > 0, "SSETokenPayload missing 'text' must fail"
        assert len(list(v_token.iter_errors({}))) > 0, "Empty SSETokenPayload must fail"
        assert len(list(v_token.iter_errors({"text": "ok", "unexpected": "property"}))) > 0, "SSETokenPayload with additionalProperties must fail"
        print(f"[PASS] Adversarial: SSETokenPayload strictly enforces required and additionalProperties.")

        # B. SessionMetrics target_met strictness
        valid_met = {"wpm": 50.0, "accuracy_score": 90.0, "time_spent_ms": 2000, "word_count": 5, "target_met": True}
        assert len(list(v_metrics.iter_errors(valid_met))) == 0
        invalid_met = {"wpm": 50.0, "accuracy_score": 90.0, "time_spent_ms": 2000, "word_count": 5}
        assert len(list(v_metrics.iter_errors(invalid_met))) > 0, "SessionMetrics without target_met must fail"
        print(f"[PASS] Adversarial: SessionMetrics strictly enforces target_met.")

        # C. EvaluationRequest user_text length boundaries
        assert len(list(v_eval.iter_errors({"user_text": "", "time_spent_ms": 100, "words_typed": 0}))) == 0, "user_text='' on timer expiration must pass"
        assert len(list(v_eval.iter_errors({"user_text": "a" * 1000, "time_spent_ms": 100, "words_typed": 100}))) == 0, "user_text=1000 chars must pass"
        assert len(list(v_eval.iter_errors({"user_text": "a" * 1001, "time_spent_ms": 100, "words_typed": 100}))) > 0, "user_text=1001 chars must fail"
        assert len(list(v_eval.iter_errors({"user_text": "valid", "time_spent_ms": -1, "words_typed": 1}))) > 0, "negative time_spent_ms must fail"
        print(f"[PASS] Adversarial: EvaluationRequest enforces minLength=0, maxLength=1000, and non-negative constraints.")

        # D. Malformed SSEStreamEvent payloads
        malformed_sse_cases = [
            ("Missing event", {"data": {"text": "hello"}}),
            ("Invalid event enum", {"event": "heartbeat", "data": {"text": "hello"}}),
            ("Missing data", {"event": "token"}),
            ("Empty object data", {"event": "token", "data": {}}),
            ("Primitive integer data", {"event": "token", "data": 12345}),
            ("Null data", {"event": "token", "data": None}),
            ("Unmatched object data", {"event": "session_start", "data": {"unrelated_field": "test"}}),
            ("Arbitrary garbage envelope", {"event": "grammar_errors", "data": {"not_errors": [1, 2, 3]}}),
            ("Metrics data missing target_met", {"event": "metrics", "data": {"wpm": 50.0, "accuracy_score": 90.0, "time_spent_ms": 2000, "word_count": 5}})
        ]

        for desc, case in malformed_sse_cases:
            errs = list(v_sse.iter_errors(case))
            assert len(errs) > 0, f"Malformed SSE case '{desc}' unexpectedly passed validation!"
            print(f"[PASS] Adversarial: Malformed SSE case '{desc}' correctly rejected.")

        # E. SessionCreateRequest strict domain constraints
        valid_session = {"mode": "translation", "source_language": "ru", "target_language": "en", "timer_seconds": 30, "target_word_count": 10}
        assert len(list(v_session.iter_errors(valid_session))) == 0

        session_invalid_cases = [
            ("Invalid mode", {**valid_session, "mode": "arcade"}),
            ("Invalid timer 45s", {**valid_session, "timer_seconds": 45}),
            ("Invalid timer 0s", {**valid_session, "timer_seconds": 0}),
            ("Word count below min (2)", {**valid_session, "target_word_count": 2}),
            ("Word count above max (51)", {**valid_session, "target_word_count": 51}),
            ("Invalid language code", {**valid_session, "source_language": "RUSSIAN"})
        ]
        for desc, case in session_invalid_cases:
            errs = list(v_session.iter_errors(case))
            assert len(errs) > 0, f"Invalid session case '{desc}' unexpectedly passed!"
            print(f"[PASS] Adversarial: Invalid session case '{desc}' correctly rejected.")

        print("\n" + "="*70)
        print("ALL FORENSIC AUDIT CHECKS AND STRESS TESTS PASSED SUCCESSFULLY!")
        print("VERDICT: CLEAN")
        print("="*70)

    except Exception as e:
        print("\n[!] EXCEPTION ENCOUNTERED DURING AUDIT:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_audit()
