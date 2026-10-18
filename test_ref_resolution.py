import json
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

with open("contracts/api_v1.json", "r", encoding="utf-8") as f:
    doc = json.load(f)

# The root document itself can be the schema or we reference from the root
resource = Resource.from_contents(doc, default_specification=DRAFT202012)
# Register the base URI
registry = Registry().with_resource("http://example.com/api_v1.json", resource)

# When validating against a component schema, construct a reference from root:
target_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$ref": "http://example.com/api_v1.json#/components/schemas/SSEStreamEvent"
}
validator = Draft202012Validator(target_schema, registry=registry)

sample_event = {
    "event": "session_start",
    "data": {
        "session_id": "123e4567-e89b-12d3-a456-426614174000",
        "status": "active"
    }
}

errors = list(validator.iter_errors(sample_event))
print("Errors for sample event:", len(errors))
for e in errors:
    print(" - Error:", e.message)
    print(" - Schema path:", e.schema_path)
