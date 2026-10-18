"""
Challenger M1-3 Empirical Stress Testing Harness for contracts/api_v1.json
"""

import json
import re
import sys
from typing import Any, Dict, List
import jsonschema
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

def test_suite():
    print("=" * 80)
    print("CHALLENGER M1-3: EMPIRICAL CONTRACT REMEDIATION STRESS TEST SUITE")
    print("=" * 80)

    with open("contracts/api_v1.json", "r", encoding="utf-8") as f:
        doc = json.load(f)

    BASE_URI = "http://example.com/api_v1.json"
    resource = Resource.from_contents(doc, default_specification=DRAFT202012)
    registry = Registry().with_resource(BASE_URI, resource)
    format_checker = jsonschema.FormatChecker()

    def get_validator(schema_name: str, with_format: bool = False) -> jsonschema.Draft202012Validator:
        schema_ref = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$ref": f"{BASE_URI}#/components/schemas/{schema_name}",
        }
        fc = format_checker if with_format else None
        return jsonschema.Draft202012Validator(schema_ref, registry=registry, format_checker=fc)

    results = []

    def assert_case(section: str, name: str, expected: bool, actual: bool, details: str = ""):
        passed = (expected == actual)
        results.append({
            "section": section,
            "name": name,
            "expected": expected,
            "actual": actual,
            "passed": passed,
            "details": details
        })
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {section} | {name} (expected={expected}, actual={actual}) {details}")
        return passed

    # --------------------------------------------------------------------------
    # 1. $ref Resolution Integrity (All 49 pointers)
    # --------------------------------------------------------------------------
    print("\n--- 1. $ref Resolution Integrity ---")
    ref_pattern = re.compile(r'"\$ref":\s*"([^"]+)"')
    raw_text = open("contracts/api_v1.json", "r", encoding="utf-8").read()
    all_refs = ref_pattern.findall(raw_text)
    
    assert_case("References", "Discovered $refs count == 49", True, len(all_refs) == 49, f"Found {len(all_refs)}")

    broken_refs = []
    for ref in all_refs:
        if ref.startswith("#/"):
            parts = ref.lstrip("#/").split("/")
            curr = doc
            found = True
            for part in parts:
                if isinstance(curr, dict) and part in curr:
                    curr = curr[part]
                else:
                    found = False
                    break
            if not found:
                broken_refs.append(ref)
        else:
            broken_refs.append(ref)
    
    assert_case("References", "All 49 $refs resolve cleanly without broken pointers", True, len(broken_refs) == 0, f"Broken: {broken_refs}")

    # --------------------------------------------------------------------------
    # 2. SSEStreamEvent Schema Remediation & oneOf Removal
    # --------------------------------------------------------------------------
    print("\n--- 2. SSEStreamEvent Schema Remediation ---")
    sse_schema = doc["components"]["schemas"]["SSEStreamEvent"]
    data_props = sse_schema["properties"]["data"]
    
    assert_case("SSEStreamEvent", "'oneOf' completely removed from data", True, "oneOf" not in data_props)
    assert_case("SSEStreamEvent", "'anyOf' present in data", True, "anyOf" in data_props)
    assert_case("SSEStreamEvent", "SSEStreamEvent requires 'event' and 'data'", True, 
                set(sse_schema.get("required", [])) == {"event", "data"})

    token_schema = doc["components"]["schemas"]["SSETokenPayload"]
    assert_case("SSETokenPayload", "Requires 'text'", True, token_schema.get("required") == ["text"])
    assert_case("SSETokenPayload", "additionalProperties is False", True, token_schema.get("additionalProperties") is False)

    inline_err = None
    for branch in data_props.get("anyOf", []):
        if branch.get("type") == "object" and "errors" in branch.get("properties", {}):
            inline_err = branch
            break
    assert_case("InlineErrorsBranch", "Branch exists in anyOf", True, inline_err is not None)
    if inline_err:
        assert_case("InlineErrorsBranch", "Requires 'errors'", True, inline_err.get("required") == ["errors"])
        assert_case("InlineErrorsBranch", "additionalProperties is False", True, inline_err.get("additionalProperties") is False)

    # --------------------------------------------------------------------------
    # 3. Positive Validation for All 9 SSE Event Payloads
    # --------------------------------------------------------------------------
    print("\n--- 3. Positive Validation: All 9 SSE Event Payloads ---")
    v_sse = get_validator("SSEStreamEvent")

    positive_events = [
        ("1. session_start", {
            "event": "session_start",
            "data": {
                "session_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "active"
            }
        }),
        ("2. token (standard text & index)", {
            "event": "token",
            "data": {
                "text": "The ",
                "index": 0
            }
        }),
        ("3. token (with alias token field)", {
            "event": "token",
            "data": {
                "text": "quick ",
                "token": "quick ",
                "index": 1
            }
        }),
        ("4. grammar_errors (bare array)", {
            "event": "grammar_errors",
            "data": [
                {
                    "start": 0,
                    "end": 4,
                    "original_text": "Thay",
                    "message": "Possible typo",
                    "suggestion": "They",
                    "category": "spelling",
                    "severity": "error"
                }
            ]
        }),
        ("5. grammar_errors (envelope object)", {
            "event": "grammar_errors",
            "data": {
                "errors": [
                    {
                        "start": 0,
                        "end": 4,
                        "original_text": "Thay",
                        "message": "Possible typo",
                        "suggestion": "They",
                        "category": "spelling",
                        "severity": "error"
                    }
                ]
            }
        }),
        ("6. semantic_check", {
            "event": "semantic_check",
            "data": {
                "is_valid": True,
                "score": 92.5,
                "explanation": "Core semantic meaning preserved accurately.",
                "missing_concepts": []
            }
        }),
        ("7. style_alternative", {
            "event": "style_alternative",
            "data": {
                "style": "formal",
                "text": "Could you please clarify your statement?",
                "explanation": "Provides a polite and courteous phrasing."
            }
        }),
        ("8. metrics (with target_met: true)", {
            "event": "metrics",
            "data": {
                "wpm": 62.5,
                "accuracy_score": 97.0,
                "time_spent_ms": 8500,
                "word_count": 12,
                "target_met": True
            }
        }),
        ("8b. metrics (with target_met: false)", {
            "event": "metrics",
            "data": {
                "wpm": 30.0,
                "accuracy_score": 75.0,
                "time_spent_ms": 15000,
                "word_count": 8,
                "target_met": False
            }
        }),
        ("9. done", {
            "event": "done",
            "data": {
                "evaluation_id": "123e4567-e89b-12d3-a456-426614174000",
                "latency": {
                    "ttft_ms": 320.5,
                    "inference_duration_ms": 1150.0,
                    "pipeline_duration_ms": 1470.5
                }
            }
        }),
        ("10. error", {
            "event": "error",
            "data": {
                "code": "INFERENCE_TIMEOUT",
                "message": "LLM response generation exceeded 3000ms deadline",
                "details": {"deadline_ms": 3000}
            }
        })
    ]

    for label, payload in positive_events:
        errors = list(v_sse.iter_errors(payload))
        err_str = "; ".join([e.message for e in errors]) if errors else ""
        assert_case("SSEStreamEvent Positive", label, True, len(errors) == 0, err_str)

    # --------------------------------------------------------------------------
    # 4. Negative Cases & Boundary Stress Testing on SSEStreamEvent
    # --------------------------------------------------------------------------
    print("\n--- 4. Negative Cases & Boundary Stress Testing on SSEStreamEvent ---")
    v_sse_format = get_validator("SSEStreamEvent", with_format=True)

    negative_events = [
        ("Invalid event name: 'invalid_event'", v_sse, {"event": "invalid_event", "data": {"text": "hi"}}, False),
        ("Invalid event name: 'heartbeat'", v_sse, {"event": "heartbeat", "data": {"text": "hi"}}, False),
        ("Invalid event name: empty string ''", v_sse, {"event": "", "data": {"text": "hi"}}, False),
        ("Invalid event name: null", v_sse, {"event": None, "data": {"text": "hi"}}, False),
        ("Invalid event name: integer 123", v_sse, {"event": 123, "data": {"text": "hi"}}, False),
        ("Missing 'event' key", v_sse, {"data": {"text": "hi"}}, False),
        ("Missing 'data' key", v_sse, {"event": "token"}, False),
        ("Null data", v_sse, {"event": "token", "data": None}, False),
        ("Empty string data", v_sse, {"event": "token", "data": ""}, False),
        ("Empty object data {}", v_sse, {"event": "token", "data": {}}, False),
        ("Token payload missing required 'text'", v_sse, {"event": "token", "data": {"index": 0}}, False),
        ("Token payload with extra unrecognized property", v_sse, {"event": "token", "data": {"text": "hi", "extra_prop": 123}}, False),
        ("session_start missing required 'session_id'", v_sse, {"event": "session_start", "data": {"status": "active"}}, False),
        ("session_start missing required 'status'", v_sse, {"event": "session_start", "data": {"session_id": "123e4567-e89b-12d3-a456-426614174000"}}, False),
        ("session_start invalid UUID format (with FormatChecker)", v_sse_format, {"event": "session_start", "data": {"session_id": "not-a-uuid", "status": "active"}}, False),
        ("session_start invalid status enum", v_sse, {"event": "session_start", "data": {"session_id": "123e4567-e89b-12d3-a456-426614174000", "status": "closed"}}, False),
        ("metrics missing required 'target_met'", v_sse, {"event": "metrics", "data": {"wpm": 50, "accuracy_score": 90, "time_spent_ms": 2000, "word_count": 5}}, False),
        ("metrics missing required 'wpm'", v_sse, {"event": "metrics", "data": {"accuracy_score": 90, "time_spent_ms": 2000, "word_count": 5, "target_met": True}}, False),
        ("metrics negative wpm", v_sse, {"event": "metrics", "data": {"wpm": -5, "accuracy_score": 90, "time_spent_ms": 2000, "word_count": 5, "target_met": True}}, False),
        ("metrics accuracy_score > 100", v_sse, {"event": "metrics", "data": {"wpm": 50, "accuracy_score": 105, "time_spent_ms": 2000, "word_count": 5, "target_met": True}}, False),
        ("metrics accuracy_score < 0", v_sse, {"event": "metrics", "data": {"wpm": 50, "accuracy_score": -1, "time_spent_ms": 2000, "word_count": 5, "target_met": True}}, False),
        ("done missing required 'latency'", v_sse, {"event": "done", "data": {"evaluation_id": "123e4567-e89b-12d3-a456-426614174000"}}, False),
        ("done latency missing required 'ttft_ms'", v_sse, {"event": "done", "data": {"latency": {"inference_duration_ms": 100, "pipeline_duration_ms": 200}}}, False),
        ("error missing required 'code'", v_sse, {"event": "error", "data": {"message": "something failed"}}, False),
        ("error missing required 'message'", v_sse, {"event": "error", "data": {"code": "ERR_01"}}, False),
        ("style_alternative invalid style enum", v_sse, {"event": "style_alternative", "data": {"style": "poetic", "text": "...", "explanation": "..."}}, False),
        ("semantic_check missing required 'missing_concepts'", v_sse, {"event": "semantic_check", "data": {"is_valid": True, "score": 90, "explanation": "ok"}}, False),
        ("grammar_errors array item negative start", v_sse, {"event": "grammar_errors", "data": [{"start": -1, "end": 4, "original_text": "a", "message": "b", "suggestion": "c", "category": "spelling", "severity": "error"}]}, False),
        ("grammar_errors array item invalid category", v_sse, {"event": "grammar_errors", "data": [{"start": 0, "end": 4, "original_text": "a", "message": "b", "suggestion": "c", "category": "unknown", "severity": "error"}]}, False),
        ("grammar_errors array item invalid severity", v_sse, {"event": "grammar_errors", "data": [{"start": 0, "end": 4, "original_text": "a", "message": "b", "suggestion": "c", "category": "spelling", "severity": "critical"}]}, False),
        ("grammar_errors envelope missing required 'errors'", v_sse, {"event": "grammar_errors", "data": {"not_errors": []}}, False),
        ("grammar_errors envelope with extra properties", v_sse, {"event": "grammar_errors", "data": {"errors": [], "extra": 123}}, False),
    ]

    for label, validator, payload, expected_valid in negative_events:
        errors = list(validator.iter_errors(payload))
        is_valid = (len(errors) == 0)
        assert_case("SSEStreamEvent Negative", label, expected_valid, is_valid)

    # --------------------------------------------------------------------------
    # 5. Token Text Specific Testing: Empty string vs Missing vs Valid
    # --------------------------------------------------------------------------
    print("\n--- 5. Token Text Specific Testing ---")
    v_token = get_validator("SSETokenPayload")
    
    assert_case("SSETokenPayload", "Empty token object {} rejected (missing required 'text')", False, v_token.is_valid({}))
    assert_case("SSETokenPayload", "Missing text rejected {'index': 0}", False, v_token.is_valid({"index": 0}))
    assert_case("SSETokenPayload", "Non-string text rejected {'text': 123}", False, v_token.is_valid({"text": 123}))
    assert_case("SSETokenPayload", "Null text rejected {'text': None}", False, v_token.is_valid({"text": None}))
    assert_case("SSETokenPayload", "Additional properties rejected {'text': 'a', 'x': 1}", False, v_token.is_valid({"text": "a", "x": 1}))
    # Note on empty string text:
    empty_token_valid = v_token.is_valid({"text": ""})
    print(f"[INFO] SSETokenPayload accepts empty string text {{'text': ''}}: {empty_token_valid}")
    assert_case("SSETokenPayload", "Empty string text {'text': ''} conforms to string schema (minLength unspecified)", True, empty_token_valid)

    # --------------------------------------------------------------------------
    # 6. EvaluationRequest & SessionMetrics Boundary Testing
    # --------------------------------------------------------------------------
    print("\n--- 6. EvaluationRequest & SessionMetrics Boundary Testing ---")
    v_eval = get_validator("EvaluationRequest")
    assert_case("EvaluationRequest", "Empty user_text '' (timer expired) passes (minLength=0)", True,
                v_eval.is_valid({"user_text": "", "time_spent_ms": 15000, "words_typed": 0}))
    assert_case("EvaluationRequest", "Normal user_text passes", True,
                v_eval.is_valid({"user_text": "Hello world", "time_spent_ms": 5000, "words_typed": 2}))
    assert_case("EvaluationRequest", "user_text length 1000 chars passes", True,
                v_eval.is_valid({"user_text": "x" * 1000, "time_spent_ms": 5000, "words_typed": 10}))
    assert_case("EvaluationRequest", "user_text length 1001 chars rejected (maxLength=1000)", False,
                v_eval.is_valid({"user_text": "x" * 1001, "time_spent_ms": 5000, "words_typed": 10}))
    assert_case("EvaluationRequest", "Negative time_spent_ms rejected", False,
                v_eval.is_valid({"user_text": "Hi", "time_spent_ms": -1, "words_typed": 1}))
    assert_case("EvaluationRequest", "Negative words_typed rejected", False,
                v_eval.is_valid({"user_text": "Hi", "time_spent_ms": 1000, "words_typed": -1}))

    v_metrics = get_validator("SessionMetrics")
    assert_case("SessionMetrics", "Valid metrics with target_met: True passes", True,
                v_metrics.is_valid({"wpm": 60.0, "accuracy_score": 95.0, "time_spent_ms": 5000, "word_count": 10, "target_met": True}))
    assert_case("SessionMetrics", "Valid metrics with target_met: False passes", True,
                v_metrics.is_valid({"wpm": 60.0, "accuracy_score": 95.0, "time_spent_ms": 5000, "word_count": 10, "target_met": False}))
    assert_case("SessionMetrics", "Missing target_met rejected", False,
                v_metrics.is_valid({"wpm": 60.0, "accuracy_score": 95.0, "time_spent_ms": 5000, "word_count": 10}))

    # --------------------------------------------------------------------------
    # Final Summary
    # --------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    total = len(results)
    passed_count = sum(1 for r in results if r["passed"])
    failed_count = total - passed_count
    print(f"Total assertions:  {total}")
    print(f"Passed assertions: {passed_count}")
    print(f"Failed assertions: {failed_count}")

    if failed_count > 0:
        print("\nFailed assertions:")
        for r in results:
            if not r["passed"]:
                print(f"[-] {r['section']} | {r['name']} (Expected: {r['expected']}, Actual: {r['actual']}) {r['details']}")
        sys.exit(1)
    else:
        print("\nALL ASSERTIONS PASSED EMPIRICALLY! (100% SUCCESS)")

if __name__ == "__main__":
    test_suite()
