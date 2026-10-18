import json
import jsonschema

with open('contracts/api_v1.json', 'r', encoding='utf-8') as f:
    schema_doc = json.load(f)

schemas = schema_doc['components']['schemas']
resolver = jsonschema.RefResolver.from_schema(schema_doc)

test_cases = {
    "SessionCreateRequest": [
        # Valid standard
        ({"mode": "translation", "source_language": "ru", "target_language": "en"}, True),
        # Valid with all options
        ({
            "mode": "situation_image",
            "source_language": "ru",
            "target_language": "en-US",
            "timer_seconds": 15,
            "target_word_count": 25,
            "margin_buffer": 5,
            "difficulty": "hard",
            "input_mode": "scaffolding",
            "preferred_style": "academic",
            "allow_loose_phrasing": False
        }, True),
        # Valid untimed (timer_seconds null)
        ({"mode": "translation", "source_language": "ru", "target_language": "en", "timer_seconds": None}, True),
        # Invalid timer_seconds (45 not in [15, 30, 60, null])
        ({"mode": "translation", "source_language": "ru", "target_language": "en", "timer_seconds": 45}, False),
        # Invalid target_word_count (< 3)
        ({"mode": "translation", "source_language": "ru", "target_language": "en", "target_word_count": 2}, False),
        # Invalid target_word_count (> 50)
        ({"mode": "translation", "source_language": "ru", "target_language": "en", "target_word_count": 51}, False),
        # Invalid margin_buffer (< 0)
        ({"mode": "translation", "source_language": "ru", "target_language": "en", "margin_buffer": -1}, False),
        # Invalid margin_buffer (> 15)
        ({"mode": "translation", "source_language": "ru", "target_language": "en", "margin_buffer": 16}, False),
        # Missing required mode
        ({"source_language": "ru", "target_language": "en"}, False),
    ],
    "EvaluationRequest": [
        # Valid
        ({"user_text": "I went to the store today.", "time_spent_ms": 12000, "words_typed": 6}, True),
        # Valid with optional fields
        ({"user_text": "Hello world", "time_spent_ms": 1500, "words_typed": 2, "character_count": 11, "keystroke_count": 13}, True),
        # Empty user_text (minLength 1)
        ({"user_text": "", "time_spent_ms": 12000, "words_typed": 0}, False),
        # Negative time_spent_ms
        ({"user_text": "Test", "time_spent_ms": -1, "words_typed": 1}, False),
        # Negative words_typed
        ({"user_text": "Test", "time_spent_ms": 1000, "words_typed": -1}, False),
        # Exceeds maxLength 1000
        ({"user_text": "a" * 1001, "time_spent_ms": 1000, "words_typed": 1}, False),
    ],
    "GrammarErrorSpan": [
        # Valid
        ({
            "start": 0, "end": 4, "original_text": "Thay", "message": "Misspelled word",
            "suggestion": "They", "category": "spelling", "severity": "error"
        }, True),
        # Invalid category
        ({
            "start": 0, "end": 4, "original_text": "Thay", "message": "Misspelled word",
            "suggestion": "They", "category": "non_existent_cat", "severity": "error"
        }, False),
        # Invalid severity
        ({
            "start": 0, "end": 4, "original_text": "Thay", "message": "Misspelled word",
            "suggestion": "They", "category": "spelling", "severity": "critical"
        }, False),
        # Negative start
        ({
            "start": -1, "end": 4, "original_text": "Thay", "message": "Misspelled word",
            "suggestion": "They", "category": "spelling", "severity": "error"
        }, False),
    ],
    "SemanticValidation": [
        # Valid
        ({"is_valid": True, "score": 92.5, "explanation": "Accurate meaning", "missing_concepts": []}, True),
        # Valid with missing concepts
        ({"is_valid": False, "score": 40.0, "explanation": "Missed urgency", "missing_concepts": ["urgency", "deadline"]}, True),
        # Score > 100
        ({"is_valid": True, "score": 101.0, "explanation": "Too high", "missing_concepts": []}, False),
        # Score < 0
        ({"is_valid": True, "score": -1.0, "explanation": "Too low", "missing_concepts": []}, False),
    ],
    "StyleAlternative": [
        # Valid
        ({"style": "academic", "text": "The empirical findings demonstrate...", "explanation": "Scholarly vocabulary"}, True),
        # Invalid style
        ({"style": "poetic", "text": "Roses are red...", "explanation": "Poetry"}, False),
        # Missing explanation
        ({"style": "formal", "text": "Good morning"}, False),
    ],
    "SessionMetrics": [
        # Valid
        ({"wpm": 72.4, "accuracy_score": 95.0, "time_spent_ms": 15000, "word_count": 18, "target_met": True}, True),
        # Negative WPM
        ({"wpm": -5.0, "accuracy_score": 95.0, "time_spent_ms": 15000, "word_count": 18}, False),
        # Accuracy > 100
        ({"wpm": 60.0, "accuracy_score": 105.0, "time_spent_ms": 15000, "word_count": 18}, False),
    ],
    "ErrorResponse": [
        # Valid standard
        ({"code": "VALIDATION_ERROR", "message": "Field required"}, True),
        # Valid with details object
        ({"code": "VALIDATION_ERROR", "message": "Field required", "details": {"field": "user_text"}}, True),
        # Valid with details array
        ({"code": "VALIDATION_ERROR", "message": "Field required", "details": ["err1", "err2"]}, True),
        # Valid with details null
        ({"code": "VALIDATION_ERROR", "message": "Field required", "details": None}, True),
        # Missing message
        ({"code": "VALIDATION_ERROR"}, False),
        # Missing code
        ({"message": "Something happened"}, False),
    ]
}

print("=== Running Comprehensive Schema Boundary Tests ===")
passed_total = 0
failed_total = 0

for schema_name, cases in test_cases.items():
    s = schemas[schema_name]
    for idx, (instance, should_pass) in enumerate(cases):
        try:
            jsonschema.validate(instance=instance, schema=s, resolver=resolver)
            actual_pass = True
        except jsonschema.ValidationError:
            actual_pass = False
        
        if actual_pass == should_pass:
            passed_total += 1
        else:
            failed_total += 1
            print(f"FAILED TEST: {schema_name}[{idx}] expected {should_pass}, got {actual_pass}")
            print(f"  Instance: {instance}")

print(f"\nTotal tests run: {passed_total + failed_total}")
print(f"Passed: {passed_total}")
print(f"Failed: {failed_total}")
