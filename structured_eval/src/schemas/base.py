"""Base schema utilities and provider-specific JSON Schema conversion."""

from __future__ import annotations

import copy
from typing import Any

from pydantic import BaseModel


class DocumentSchema(BaseModel):
    """Base class for document extraction schemas."""

    @classmethod
    def document_type(cls) -> str:
        raise NotImplementedError

    @classmethod
    def document_type_ja(cls) -> str:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_SCHEMA_REGISTRY: dict[str, type[DocumentSchema]] = {}


def register_schema(cls: type[DocumentSchema]) -> type[DocumentSchema]:
    """Decorator to register a document schema."""
    _SCHEMA_REGISTRY[cls.document_type()] = cls
    return cls


def get_schema(document_type: str) -> type[DocumentSchema]:
    return _SCHEMA_REGISTRY[document_type]


def get_all_schema_types() -> list[str]:
    return list(_SCHEMA_REGISTRY.keys())


def get_all_schemas() -> dict[str, type[DocumentSchema]]:
    return dict(_SCHEMA_REGISTRY)


# ---------------------------------------------------------------------------
# JSON Schema generation
# ---------------------------------------------------------------------------

def generate_json_schema(schema_cls: type[DocumentSchema]) -> dict[str, Any]:
    """Generate a plain JSON Schema from a Pydantic model (dereferenced)."""
    raw = schema_cls.model_json_schema()
    return _deref_schema(raw)


def _deref_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Inline all $ref / $defs references for a flat JSON Schema."""
    defs = schema.pop("$defs", {})
    return _resolve_refs(schema, defs)


def _resolve_refs(node: Any, defs: dict[str, Any]) -> Any:
    if isinstance(node, dict):
        if "$ref" in node:
            ref_name = node["$ref"].split("/")[-1]
            resolved = copy.deepcopy(defs[ref_name])
            return _resolve_refs(resolved, defs)
        return {k: _resolve_refs(v, defs) for k, v in node.items()}
    if isinstance(node, list):
        return [_resolve_refs(item, defs) for item in node]
    return node


# ---------------------------------------------------------------------------
# Provider-specific schema conversion
# ---------------------------------------------------------------------------

def to_claude_schema(schema_cls: type[DocumentSchema]) -> dict[str, Any]:
    """Convert to Claude tool input_schema format.

    Claude tool_use accepts standard JSON Schema directly.
    """
    return generate_json_schema(schema_cls)


def to_openai_schema(schema_cls: type[DocumentSchema]) -> dict[str, Any]:
    """Convert to OpenAI strict structured output format.

    OpenAI strict mode requires:
    - additionalProperties: false on all objects
    - Optional fields as anyOf: [{type: T}, {type: "null"}]
    """
    schema = generate_json_schema(schema_cls)
    return _openai_strict_transform(schema)


def _openai_strict_transform(node: Any) -> Any:
    """Recursively apply OpenAI strict mode requirements."""
    if not isinstance(node, dict):
        return node

    result = {}
    for k, v in node.items():
        result[k] = _openai_strict_transform(v)

    if result.get("type") == "object" and "properties" in result:
        result["additionalProperties"] = False
        # All properties must be required in strict mode;
        # optional fields use anyOf with null
        if "properties" in result:
            all_props = list(result["properties"].keys())
            required = set(result.get("required", []))
            for prop_name in all_props:
                if prop_name not in required:
                    prop_schema = result["properties"][prop_name]
                    # Wrap in anyOf with null if not already
                    if not _has_null_type(prop_schema):
                        result["properties"][prop_name] = {
                            "anyOf": [prop_schema, {"type": "null"}]
                        }
            result["required"] = all_props

    return result


def _has_null_type(schema: dict) -> bool:
    """Check if schema already allows null."""
    if schema.get("type") == "null":
        return True
    if "anyOf" in schema:
        return any(s.get("type") == "null" for s in schema["anyOf"])
    return False


def to_gemini_schema(schema_cls: type[DocumentSchema]) -> dict[str, Any]:
    """Convert to Gemini response_schema format.

    Gemini uses a subset of OpenAPI 3.0 schema. Key differences:
    - Optional fields use nullable: true
    - No $ref support (already handled by dereferencing)
    """
    schema = generate_json_schema(schema_cls)
    return _gemini_transform(schema)


# ---------------------------------------------------------------------------
# Dict-based provider conversion (for dataset-stored JSON Schemas)
# ---------------------------------------------------------------------------

def convert_to_claude(schema_dict: dict[str, Any]) -> dict[str, Any]:
    """Convert a JSON Schema dict to Claude json_schema format.

    Claude requires additionalProperties: false on all objects
    and uses anyOf for nullable fields (same as OpenAI).
    """
    schema = copy.deepcopy(schema_dict)
    schema.pop("$schema", None)
    schema = _normalize_nullable(schema)
    return _claude_transform(schema)


def convert_to_openai(schema_dict: dict[str, Any]) -> dict[str, Any]:
    """Convert a JSON Schema dict to OpenAI strict format."""
    schema = copy.deepcopy(schema_dict)
    schema.pop("$schema", None)
    schema = _normalize_nullable(schema)
    return _openai_strict_transform(schema)


def convert_to_gemini(schema_dict: dict[str, Any]) -> dict[str, Any]:
    """Convert a JSON Schema dict to Gemini format."""
    schema = copy.deepcopy(schema_dict)
    schema.pop("$schema", None)
    schema = _normalize_nullable(schema)
    return _gemini_transform(schema)


def _normalize_nullable(node: Any) -> Any:
    """Convert type: ["string", "null"] to anyOf format for consistency."""
    if not isinstance(node, dict):
        return node

    result = {}
    for k, v in node.items():
        result[k] = _normalize_nullable(v)

    # Convert type: ["string", "null"] -> anyOf: [{type: "string"}, {type: "null"}]
    if isinstance(result.get("type"), list):
        types = result.pop("type")
        non_null = [t for t in types if t != "null"]
        has_null = "null" in types
        if has_null and len(non_null) == 1:
            base = {"type": non_null[0]}
            # Preserve description only; drop format/pattern (unsupported by most providers)
            if "description" in result:
                base["description"] = result.pop("description")
            result.pop("format", None)
            result.pop("pattern", None)
            result["anyOf"] = [base, {"type": "null"}]
        elif non_null:
            result["type"] = non_null[0] if len(non_null) == 1 else non_null

    # Remove unsupported constraints
    for drop_key in ("minItems", "minimum", "maximum", "minLength", "maxLength", "format", "pattern"):
        result.pop(drop_key, None)

    return result


def _claude_transform(node: Any) -> Any:
    """Apply Claude json_schema requirements: additionalProperties false on all objects."""
    if not isinstance(node, dict):
        return node

    result = {}
    for k, v in node.items():
        result[k] = _claude_transform(v)

    if result.get("type") == "object" and "properties" in result:
        result["additionalProperties"] = False
        # All properties must be required; optional fields use anyOf with null
        all_props = list(result["properties"].keys())
        required = set(result.get("required", []))
        for prop_name in all_props:
            if prop_name not in required:
                prop_schema = result["properties"][prop_name]
                if not _has_null_type(prop_schema):
                    result["properties"][prop_name] = {
                        "anyOf": [prop_schema, {"type": "null"}]
                    }
        result["required"] = all_props

    return result


def _gemini_transform(node: Any) -> Any:
    """Recursively apply Gemini schema requirements."""
    if not isinstance(node, dict):
        return node

    result = {}
    for k, v in node.items():
        if k == "anyOf":
            # Convert anyOf with null to nullable
            non_null = [s for s in v if s.get("type") != "null"]
            has_null = any(s.get("type") == "null" for s in v)
            if has_null and len(non_null) == 1:
                inner = _gemini_transform(non_null[0])
                inner["nullable"] = True
                return inner
            # For complex anyOf, keep as-is
            result[k] = [_gemini_transform(s) for s in v]
        else:
            result[k] = _gemini_transform(v)

    # Remove fields not supported by Gemini's OpenAPI subset
    # Only pop "title" when it's a string (schema metadata), not a dict (actual property)
    if isinstance(result.get("title"), str):
        result.pop("title", None)
    result.pop("additionalProperties", None)
    result.pop("$schema", None)

    return result
