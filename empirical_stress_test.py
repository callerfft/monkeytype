"""
Empirical Schema Constraints & Payload Stress Testing Harness for LinguaType Milestone 1
Target file: contracts/api_v1.json
"""

import json
from typing import Any, Dict, List
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

# 1. Load Contract Document
with open("contracts/api_v1.json", "r", encoding="utf-8") as f:
    doc = json.load(f)

BASE_URI = "http://example.com/api_v1.json"
resource = Resource.from_contents(doc, default_specification=DRAFT202012)
registry = Registry().with_resource(BASE_URI, resource)


def get_validator(schema_name: str) -> Draft202012Validator:
    schema_ref = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$ref": f"{BASE_URI}#/components/schemas/{schema_name}",
    }
    return Draft202012Validator(schema_ref, registry=registry)


test_results: List[Dict[str, Any]] = []


def run_case(
    category: str,
    case_name: str,
    validator: Draft202012Validator,
    payload: Any,
    expected_valid: bool,
    description: str = "",
) -> bool:
    errors = list(validator.iter_errors(payload))
    is_valid = len(errors) == 0
    passed = is_valid == expected_valid

    err_msgs = [f"{e.message} (path: {list(e.path)})" for e in errors]
    test_results.append(
        {
            "category": category,
            "case_name": case_name,
            "description": description,
            "expected_valid": expected_valid,
            "actual_valid": is_valid,
            "passed": passed,
            "errors": err_msgs,
        }
    )
    return passed


print("=" * 80)
print("STARTING EMPIRICAL SCHEMA CONSTRAINT & PAYLOAD STRESS TESTS (FULL SUITE)")
print("=" * 80)

# ==============================================================================
# Suite 1: SessionCreateRequest
# ==============================================================================
v_session = get_validator("SessionCreateRequest")

# 1.1 Valid Mode A & B
run_case("SessionCreateRequest", "Valid Mode A minimal", v_session,
         {"mode": "translation", "source_language": "ru", "target_language": "en"}, True,
         "Minimal Mode A required fields only")

run_case("SessionCreateRequest", "Valid Mode B full", v_session, {
    "mode": "situation_image",
    "timer_seconds": 60,
    "target_word_count": 25,
    "margin_buffer": 5,
    "source_language": "ru",
    "target_language": "en",
    "difficulty": "hard",
    "input_mode": "scaffolding",
    "preferred_style": "business",
    "allow_loose_phrasing": False,
}, True, "Full valid Mode B with all fields specified")

# 1.2 Timers
for t in [15, 30, 60, None]:
    run_case("SessionCreateRequest", f"Valid timer: {t}", v_session,
             {"mode": "translation", "source_language": "ru", "target_language": "en", "timer_seconds": t}, True,
             f"Timer {t} is in enum [15, 30, 60, null]")

for t in [45, 0, -10, 120, "30", 15.5]:
    run_case("SessionCreateRequest", f"Invalid timer: {t}", v_session,
             {"mode": "translation", "source_language": "ru", "target_language": "en", "timer_seconds": t}, False,
             f"Timer {t} violates enum/type")

# 1.3 Mode
for m in ["arcade", "speed", "", 123]:
    run_case("SessionCreateRequest", f"Invalid mode: {m}", v_session,
             {"mode": m, "source_language": "ru", "target_language": "en"}, False,
             f"Mode {m} violates enum ['translation', 'situation_image']")

# 1.4 Word limits boundaries
for wc in [3, 10, 50]:
    run_case("SessionCreateRequest", f"Valid target_word_count boundary: {wc}", v_session,
             {"mode": "translation", "source_language": "ru", "target_language": "en", "target_word_count": wc}, True,
             f"target_word_count={wc} satisfies 3 <= wc <= 50")

for wc in [2, 0, -5, 51, 100]:
    run_case("SessionCreateRequest", f"Invalid target_word_count boundary: {wc}", v_session,
             {"mode": "translation", "source_language": "ru", "target_language": "en", "target_word_count": wc}, False,
             f"target_word_count={wc} outside 3..50")

for mb in [0, 5, 15]:
    run_case("SessionCreateRequest", f"Valid margin_buffer boundary: {mb}", v_session,
             {"mode": "translation", "source_language": "ru", "target_language": "en", "margin_buffer": mb}, True,
             f"margin_buffer={mb} satisfies 0 <= mb <= 15")

for mb in [-1, 16, 25]:
    run_case("SessionCreateRequest", f"Invalid margin_buffer boundary: {mb}", v_session,
             {"mode": "translation", "source_language": "ru", "target_language": "en", "margin_buffer": mb}, False,
             f"margin_buffer={mb} outside 0..15")

# 1.5 Language codes
for lang in ["ru", "en", "uz", "en-US", "es-ES"]:
    run_case("SessionCreateRequest", f"Valid language code: {lang}", v_session,
             {"mode": "translation", "source_language": lang, "target_language": "en"}, True,
             f"Language {lang} matches ISO regex")

for lang in ["RUS", "en_US", "english", "12", "e", "en-us"]:
    run_case("SessionCreateRequest", f"Invalid language code: {lang}", v_session,
             {"mode": "translation", "source_language": lang, "target_language": "en"}, False,
             f"Language {lang} violates ISO regex")

# 1.6 Styles
for st in ["conversational", "formal", "concise", "academic", "business"]:
    run_case("SessionCreateRequest", f"Valid preferred_style: {st}", v_session,
             {"mode": "translation", "source_language": "ru", "target_language": "en", "preferred_style": st}, True,
             f"Style {st} in enum")

run_case("SessionCreateRequest", "Invalid preferred_style: slang", v_session,
         {"mode": "translation", "source_language": "ru", "target_language": "en", "preferred_style": "slang"}, False,
         "Style 'slang' not in enum")


# ==============================================================================
# Suite 2: EvaluationRequest
# ==============================================================================
v_eval_req = get_validator("EvaluationRequest")

run_case("EvaluationRequest", "Valid minimal EvaluationRequest", v_eval_req,
         {"user_text": "Hello world", "time_spent_ms": 2500, "words_typed": 2}, True,
         "Valid minimal payload")

run_case("EvaluationRequest", "Valid full EvaluationRequest", v_eval_req, {
    "user_text": "This is a tested sentence.",
    "time_spent_ms": 3200,
    "words_typed": 5,
    "character_count": 27,
    "keystroke_count": 30,
}, True, "Full valid payload with metrics")

run_case("EvaluationRequest", "Empty user_text (minLength=1)", v_eval_req,
         {"user_text": "", "time_spent_ms": 100, "words_typed": 0}, False,
         "user_text empty string should fail minLength")

run_case("EvaluationRequest", "Boundary max user_text (1000 chars)", v_eval_req,
         {"user_text": "a" * 1000, "time_spent_ms": 100, "words_typed": 100}, True,
         "user_text 1000 chars should pass maxLength")

run_case("EvaluationRequest", "Exceeded user_text (1001 chars)", v_eval_req,
         {"user_text": "a" * 1001, "time_spent_ms": 100, "words_typed": 100}, False,
         "user_text 1001 chars should fail maxLength")

run_case("EvaluationRequest", "Negative time_spent_ms", v_eval_req,
         {"user_text": "Test", "time_spent_ms": -1, "words_typed": 1}, False,
         "time_spent_ms cannot be negative")

run_case("EvaluationRequest", "Negative words_typed", v_eval_req,
         {"user_text": "Test", "time_spent_ms": 100, "words_typed": -1}, False,
         "words_typed cannot be negative")

run_case("EvaluationRequest", "Missing words_typed", v_eval_req,
         {"user_text": "Test", "time_spent_ms": 100}, False,
         "words_typed is required")


# ==============================================================================
# Suite 3: GrammarErrorSpan
# ==============================================================================
v_grammar = get_validator("GrammarErrorSpan")

run_case("GrammarErrorSpan", "Valid GrammarErrorSpan", v_grammar, {
    "start": 0,
    "end": 5,
    "original_text": "Theye",
    "message": "Spelling mistake",
    "suggestion": "They",
    "category": "spelling",
    "severity": "error",
}, True, "Valid GrammarErrorSpan with all required fields")

run_case("GrammarErrorSpan", "Negative start index", v_grammar, {
    "start": -1,
    "end": 5,
    "original_text": "Theye",
    "message": "Spelling mistake",
    "suggestion": "They",
    "category": "spelling",
    "severity": "error",
}, False, "start index must be >= 0")

run_case("GrammarErrorSpan", "Negative end index", v_grammar, {
    "start": 0,
    "end": -1,
    "original_text": "Theye",
    "message": "Spelling mistake",
    "suggestion": "They",
    "category": "spelling",
    "severity": "error",
}, False, "end index must be >= 0")

for cat in ["grammar", "spelling", "punctuation", "syntax", "word_choice", "agreement", "tense"]:
    run_case("GrammarErrorSpan", f"Valid category: {cat}", v_grammar, {
        "start": 0, "end": 3, "original_text": "bad", "message": "err", "suggestion": "good",
        "category": cat, "severity": "warning"
    }, True, f"Category {cat} in enum")

run_case("GrammarErrorSpan", "Invalid category: vocabulary", v_grammar, {
    "start": 0, "end": 3, "original_text": "bad", "message": "err", "suggestion": "good",
    "category": "vocabulary", "severity": "warning"
}, False, "Category 'vocabulary' not in enum")

for sev in ["error", "warning", "info"]:
    run_case("GrammarErrorSpan", f"Valid severity: {sev}", v_grammar, {
        "start": 0, "end": 3, "original_text": "bad", "message": "err", "suggestion": "good",
        "category": "grammar", "severity": sev
    }, True, f"Severity {sev} in enum")

run_case("GrammarErrorSpan", "Invalid severity: critical", v_grammar, {
    "start": 0, "end": 3, "original_text": "bad", "message": "err", "suggestion": "good",
    "category": "grammar", "severity": "critical"
}, False, "Severity 'critical' not in enum")


# ==============================================================================
# Suite 4: StyleAlternative
# ==============================================================================
v_style = get_validator("StyleAlternative")

run_case("StyleAlternative", "Valid StyleAlternative", v_style, {
    "style": "conversational",
    "text": "How's your morning going?",
    "explanation": "More natural phrasing for casual conversation.",
}, True, "Valid StyleAlternative with all required fields")

run_case("StyleAlternative", "Missing explanation in StyleAlternative", v_style, {
    "style": "formal",
    "text": "I hope this correspondence finds you well.",
}, False, "explanation is required")

run_case("StyleAlternative", "Invalid style enum in StyleAlternative", v_style, {
    "style": "poetic",
    "text": "The morning sun greets the waking soul.",
    "explanation": "Poetic flair.",
}, False, "style 'poetic' not in enum")


# ==============================================================================
# Suite 5: LatencyBenchmarkResponse & LatencyBreakdown
# ==============================================================================
v_benchmark = get_validator("LatencyBenchmarkResponse")

run_case("LatencyBenchmarkResponse", "Valid LatencyBenchmarkResponse (compliant)", v_benchmark, {
    "timestamp": "2026-10-17T05:30:00Z",
    "iterations": 5,
    "ttft_ms": {"min": 350.0, "max": 750.0, "avg": 520.0, "p95": 710.0},
    "inference_duration_ms": {"min": 1200.0, "max": 2400.0, "avg": 1800.0, "p95": 2350.0},
    "pipeline_duration_ms": {"min": 1400.0, "max": 2800.0, "avg": 2100.0, "p95": 2750.0},
    "meets_constraint": True,
}, True, "Valid LatencyBenchmarkResponse with all percentiles and meets_constraint flag")

run_case("LatencyBenchmarkResponse", "Missing p95 in percentiles", v_benchmark, {
    "timestamp": "2026-10-17T05:30:00Z",
    "iterations": 5,
    "ttft_ms": {"min": 350.0, "max": 750.0, "avg": 520.0},
    "inference_duration_ms": {"min": 1200.0, "max": 2400.0, "avg": 1800.0, "p95": 2350.0},
    "pipeline_duration_ms": {"min": 1400.0, "max": 2800.0, "avg": 2100.0, "p95": 2750.0},
    "meets_constraint": True,
}, False, "p95 is required in LatencyPercentiles")

run_case("LatencyBenchmarkResponse", "Missing meets_constraint boolean", v_benchmark, {
    "timestamp": "2026-10-17T05:30:00Z",
    "iterations": 5,
    "ttft_ms": {"min": 350.0, "max": 750.0, "avg": 520.0, "p95": 710.0},
    "inference_duration_ms": {"min": 1200.0, "max": 2400.0, "avg": 1800.0, "p95": 2350.0},
    "pipeline_duration_ms": {"min": 1400.0, "max": 2800.0, "avg": 2100.0, "p95": 2750.0},
}, False, "meets_constraint is a required property")


# ==============================================================================
# Suite 6: Prompt & SessionResponse
# ==============================================================================
v_prompt = get_validator("Prompt")
run_case("Prompt", "Valid translation prompt", v_prompt, {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "type": "translation",
    "source_language": "ru",
    "target_language": "en",
    "content": "Сегодня солнечная погода.",
    "difficulty": "easy",
    "target_word_count": 5,
    "margin_buffer": 2,
    "max_word_count": 7,
}, True, "Valid prompt schema")

run_case("Prompt", "Missing required max_word_count", v_prompt, {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "type": "translation",
    "source_language": "ru",
    "target_language": "en",
    "content": "Сегодня солнечная погода.",
    "difficulty": "easy",
    "target_word_count": 5,
    "margin_buffer": 2,
}, False, "max_word_count is required")

v_sess_resp = get_validator("SessionResponse")
run_case("SessionResponse", "Valid SessionResponse", v_sess_resp, {
    "session_id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "active",
    "mode": "translation",
    "prompt": {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "type": "translation",
        "source_language": "ru",
        "target_language": "en",
        "content": "Привет",
        "difficulty": "easy",
        "target_word_count": 1,
        "margin_buffer": 1,
        "max_word_count": 2,
    },
    "timer_seconds": 30,
    "input_mode": "free",
    "preferred_style": "conversational",
    "allow_loose_phrasing": True,
    "created_at": "2026-10-17T05:30:00Z",
    "expires_at": "2026-10-17T05:31:00Z",
}, True, "Valid SessionResponse")


# ==============================================================================
# Suite 7: UserProfile & HistoryListResponse & HealthStatus & ErrorResponse
# ==============================================================================
v_user = get_validator("UserProfile")
run_case("UserProfile", "Valid UserProfile", v_user, {
    "id": "firebase-uid-12345",
    "email": "user@example.com",
    "native_language": "ru",
    "target_language": "en",
    "preferred_style": "conversational",
    "allow_loose_phrasing": True,
    "input_mode": "free",
    "created_at": "2026-10-17T05:00:00Z",
    "updated_at": "2026-10-17T05:00:00Z",
}, True, "Valid user profile")

v_history = get_validator("HistoryListResponse")
run_case("HistoryListResponse", "Valid HistoryListResponse", v_history, {
    "results": [
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "session_id": "123e4567-e89b-12d3-a456-426614174001",
            "mode": "translation",
            "source_language": "ru",
            "target_language": "en",
            "prompt_content": "Привет мир",
            "user_text": "Hello world",
            "time_spent_ms": 1500,
            "wpm": 80.0,
            "accuracy_score": 100.0,
            "semantic_valid": True,
            "error_count": 0,
            "recommended_variant": "Hello world.",
            "preferred_style": "conversational",
            "created_at": "2026-10-17T05:30:00Z",
        }
    ],
    "total": 1,
    "offset": 0,
    "limit": 20,
}, True, "Valid history list")

v_health = get_validator("HealthStatus")
run_case("HealthStatus", "Valid HealthStatus", v_health, {
    "status": "ok",
    "service": "linguatype-backend",
    "version": "1.0.0",
    "llm_connected": True,
    "llm_provider": "google-gemini-flash",
}, True, "Valid health status")

v_err = get_validator("ErrorResponse")
run_case("ErrorResponse", "Valid ErrorResponse", v_err, {
    "code": "VALIDATION_ERROR",
    "message": "Field time_spent_ms cannot be negative",
    "details": {"field": "time_spent_ms"},
}, True, "Valid ErrorResponse")


# ==============================================================================
# Suite 8: SSEStreamEvent & oneOf Schema Ambiguity Stress Testing
# ==============================================================================
v_sse = get_validator("SSEStreamEvent")

sse_events = [
    (
        "session_start",
        {"session_id": "123e4567-e89b-12d3-a456-426614174000", "status": "active"},
    ),
    (
        "token",
        {"text": "Hello ", "index": 0},
    ),
    (
        "grammar_errors",
        [
            {
                "start": 0,
                "end": 4,
                "original_text": "Heey",
                "message": "Misspelled word",
                "suggestion": "Hey",
                "category": "spelling",
                "severity": "warning",
            }
        ],
    ),
    (
        "grammar_errors (wrapped object)",
        {
            "errors": [
                {
                    "start": 0,
                    "end": 4,
                    "original_text": "Heey",
                    "message": "Misspelled word",
                    "suggestion": "Hey",
                    "category": "spelling",
                    "severity": "warning",
                }
            ]
        },
    ),
    (
        "semantic_check",
        {
            "is_valid": True,
            "score": 95.0,
            "explanation": "Accurate",
            "missing_concepts": [],
        },
    ),
    (
        "style_alternative",
        {
            "style": "formal",
            "text": "Good day to you.",
            "explanation": "Formal greeting",
        },
    ),
    (
        "metrics",
        {
            "wpm": 55.0,
            "accuracy_score": 95.0,
            "time_spent_ms": 4000,
            "word_count": 6,
        },
    ),
    (
        "done",
        {
            "latency": {
                "ttft_ms": 350.0,
                "inference_duration_ms": 1200.0,
                "pipeline_duration_ms": 1500.0,
            }
        },
    ),
    (
        "error",
        {
            "code": "LLM_TIMEOUT",
            "message": "Inference exceeded SLA deadline of 3.0 seconds",
        },
    ),
]

for ev_name, data_payload in sse_events:
    event_type = ev_name.split()[0]
    full_event = {"event": event_type, "data": data_payload}
    run_case(
        "SSEStreamEvent (Real-world valid payloads)",
        f"Event '{ev_name}' validation against SSEStreamEvent",
        v_sse,
        full_event,
        True,
        f"Real-world event payload for event='{event_type}'",
    )

run_case(
    "SSEStreamEvent (Invalid events)",
    "Event 'heartbeat' not in enum",
    v_sse,
    {"event": "heartbeat", "data": {"session_id": "123", "status": "active"}},
    False,
    "Event 'heartbeat' should fail enum check",
)

# ==============================================================================
# Summary & Evaluation
# ==============================================================================
print("\n" + "=" * 80)
print("TEST EXECUTION SUMMARY")
print("=" * 80)

total = len(test_results)
passed = sum(1 for r in test_results if r["passed"])
failed = total - passed

print(f"Total test assertions: {total}")
print(f"Passed assertions:     {passed}")
print(f"Failed assertions:     {failed}")

if failed > 0:
    print("\nFAILED TEST CASES (UNEXPECTED VALIDATION OUTCOMES):")
    for r in test_results:
        if not r["passed"]:
            print(f"[-] [{r['category']}] {r['case_name']}")
            print(f"    Expected valid: {r['expected_valid']}, Got: {r['actual_valid']}")
            print(f"    Description: {r['description']}")
            for err in r["errors"]:
                print(f"    Error: {err}")
            print("-" * 60)

with open("test_results.json", "w", encoding="utf-8") as f:
    json.dump(test_results, f, indent=2)

print("\nSaved full test results to test_results.json")
