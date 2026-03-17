"""Level 1 & 2 metrics: JSON parse success and schema compliance."""

from __future__ import annotations

import json
from typing import Any

import jsonschema


def check_parse(raw: str) -> tuple[bool, Any | None]:
    """Level 1: Try to parse raw string as JSON.

    Returns (success, parsed_dict_or_None).
    """
    try:
        parsed = json.loads(raw)
        return True, parsed
    except (json.JSONDecodeError, TypeError):
        return False, None


def check_schema_compliance(data: Any, schema: dict) -> tuple[bool, list[str]]:
    """Level 2: Validate parsed data against JSON Schema.

    Returns (is_valid, list_of_error_messages).
    """
    validator = jsonschema.Draft202012Validator(schema)
    errors = list(validator.iter_errors(data))
    if not errors:
        return True, []
    return False, [e.message for e in errors]
