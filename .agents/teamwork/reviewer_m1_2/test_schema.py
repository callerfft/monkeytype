import json
import jsonschema

with open('contracts/api_v1.json', 'r', encoding='utf-8') as f:
    schema_doc = json.load(f)

schema = schema_doc['components']['schemas']['SSEStreamEvent']
resolver = jsonschema.RefResolver.from_schema(schema_doc)

test_events = [
    {
        'name': 'session_start',
        'event': {
            'event': 'session_start',
            'data': {'session_id': '123e4567-e89b-12d3-a456-426614174000', 'status': 'active'}
        }
    },
    {
        'name': 'token',
        'event': {
            'event': 'token',
            'data': {'text': 'hello', 'index': 0}
        }
    },
    {
        'name': 'semantic_check',
        'event': {
            'event': 'semantic_check',
            'data': {'is_valid': True, 'score': 95.0, 'explanation': 'good', 'missing_concepts': []}
        }
    },
    {
        'name': 'style_alternative',
        'event': {
            'event': 'style_alternative',
            'data': {'style': 'formal', 'text': 'greetings', 'explanation': 'better'}
        }
    },
    {
        'name': 'metrics',
        'event': {
            'event': 'metrics',
            'data': {'wpm': 60.0, 'accuracy_score': 98.0, 'time_spent_ms': 5000, 'word_count': 10}
        }
    },
    {
        'name': 'done',
        'event': {
            'event': 'done',
            'data': {
                'evaluation_id': '123e4567-e89b-12d3-a456-426614174000',
                'latency': {'ttft_ms': 400.0, 'inference_duration_ms': 1200.0, 'pipeline_duration_ms': 1500.0}
            }
        }
    },
    {
        'name': 'error',
        'event': {
            'event': 'error',
            'data': {'code': 'VALIDATION_ERROR', 'message': 'something failed'}
        }
    }
]

one_of_branches = schema['properties']['data']['oneOf']

for te in test_events:
    data = te['event']['data']
    matching_branches = []
    for idx, branch in enumerate(one_of_branches):
        try:
            jsonschema.validate(instance=data, schema=branch, resolver=resolver)
            matching_branches.append((idx, branch))
        except Exception:
            pass
    print(f"\nEvent '{te['name']}' matched {len(matching_branches)} branches in oneOf:")
    for idx, b in matching_branches:
        ref = b.get('$ref', str(b.get('type')) + ' ' + str(list(b.get('properties', {}).keys())))
        print(f"  - Branch {idx}: {ref}")
