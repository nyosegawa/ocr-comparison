"""Level 4: Aggregation and scoring data classes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DocumentResult:
    """Result for one document extraction by one model."""

    document_id: str
    document_type: str
    parse_success: bool
    schema_valid: bool
    validation_errors: list[str] = field(default_factory=list)
    field_scores: dict[str, float] = field(default_factory=dict)
    mean_field_accuracy: float = 0.0
    elapsed_sec: float = 0.0
    error: str | None = None
    raw_response: str = ""
    parsed_json: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "document_id": self.document_id,
            "document_type": self.document_type,
            "parse_success": self.parse_success,
            "schema_valid": self.schema_valid,
            "validation_errors": self.validation_errors,
            "field_scores": self.field_scores,
            "mean_field_accuracy": round(self.mean_field_accuracy, 6),
            "elapsed_sec": round(self.elapsed_sec, 3),
            "error": self.error,
        }
        if self.raw_response:
            d["raw_response"] = self.raw_response
        if self.parsed_json is not None:
            d["parsed_json"] = self.parsed_json
        return d


@dataclass
class ModelResult:
    """Aggregated result for one model across all documents."""

    model: str
    mean_field_accuracy: float = 0.0
    parse_success_rate: float = 0.0
    schema_compliance_rate: float = 0.0
    per_type: dict[str, float] = field(default_factory=dict)
    per_field: dict[str, float] = field(default_factory=dict)
    details: list[DocumentResult] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "model": self.model,
            "aggregated": {
                "mean_field_accuracy": round(self.mean_field_accuracy, 6),
                "parse_success_rate": round(self.parse_success_rate, 6),
                "schema_compliance_rate": round(self.schema_compliance_rate, 6),
                "per_type": {k: round(v, 6) for k, v in self.per_type.items()},
                "per_field": {k: round(v, 6) for k, v in self.per_field.items()},
            },
            "details": [d.to_dict() for d in self.details],
        }


def aggregate_document_results(
    model_name: str, results: list[DocumentResult]
) -> ModelResult:
    """Aggregate per-document results into a model-level summary."""
    if not results:
        return ModelResult(model=model_name)

    n = len(results)
    parse_success_rate = sum(1 for r in results if r.parse_success) / n
    schema_compliance_rate = sum(1 for r in results if r.schema_valid) / n

    # Mean field accuracy (only for successfully parsed + valid docs)
    valid_results = [r for r in results if r.parse_success and r.schema_valid]
    if valid_results:
        mean_field_accuracy = (
            sum(r.mean_field_accuracy for r in valid_results) / len(valid_results)
        )
    else:
        mean_field_accuracy = 0.0

    # Per-type accuracy
    per_type: dict[str, list[float]] = {}
    for r in valid_results:
        per_type.setdefault(r.document_type, []).append(r.mean_field_accuracy)
    per_type_avg = {k: sum(v) / len(v) for k, v in per_type.items()}

    # Per-field accuracy
    per_field: dict[str, list[float]] = {}
    for r in valid_results:
        for field_name, score in r.field_scores.items():
            per_field.setdefault(field_name, []).append(score)
    per_field_avg = {k: sum(v) / len(v) for k, v in per_field.items()}

    return ModelResult(
        model=model_name,
        mean_field_accuracy=mean_field_accuracy,
        parse_success_rate=parse_success_rate,
        schema_compliance_rate=schema_compliance_rate,
        per_type=per_type_avg,
        per_field=per_field_avg,
        details=results,
    )
