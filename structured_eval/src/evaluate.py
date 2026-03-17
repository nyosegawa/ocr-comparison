"""Main evaluation runner and CLI."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Load .env from structured_eval/ directory
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _key, _, _val = _line.partition("=")
                _key = _key.strip()
                _val = _val.strip().split("#")[0].strip()
                if _val and _key not in os.environ:
                    os.environ[_key] = _val

# Alias: GEMINI_API_KEY -> GOOGLE_API_KEY
if not os.environ.get("GOOGLE_API_KEY") and os.environ.get("GEMINI_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]

from .data import DocumentSample, load_dataset
from .metrics.field_compare import compare_fields
from .metrics.schema_compliance import check_parse, check_schema_compliance
from .metrics.scoring import DocumentResult, ModelResult, aggregate_document_results
from .models.base import StructuredOCRModel
from .models.registry import get_all_models, get_available_models, get_models_by_name
from .schemas.base import (
    convert_to_claude,
    convert_to_gemini,
    convert_to_openai,
    generate_json_schema,
    get_all_schema_types,
    get_all_schemas,
    get_schema,
    to_claude_schema,
    to_gemini_schema,
    to_openai_schema,
)

# Ensure schemas are registered by importing them
from .schemas import invoice as _invoice_mod  # noqa: F401
from .schemas import receipt as _receipt_mod  # noqa: F401
from .schemas import business_card as _bcard_mod  # noqa: F401

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"


def _get_schema_for_model(
    model: StructuredOCRModel, sample: DocumentSample
) -> dict:
    """Get the provider-appropriate schema for a model.

    Uses the schema stored in the dataset sample (from schema.json).
    Falls back to Pydantic registry if sample has no schema.
    """
    from .models.claude import ClaudeStructured
    from .models.gemini import GeminiStructured
    from .models.openai_gpt import GPTStructured

    schema_dict = sample.schema

    if isinstance(model, ClaudeStructured):
        return schema_dict  # tool_use accepts standard JSON Schema
    elif isinstance(model, GeminiStructured):
        return convert_to_gemini(schema_dict)
    elif isinstance(model, GPTStructured):
        return convert_to_openai(schema_dict)
    else:
        return schema_dict


async def evaluate_model_on_document(
    model: StructuredOCRModel,
    sample: DocumentSample,
) -> DocumentResult:
    """Run extraction on one document and compute metrics."""
    image = sample.load_image()
    schema = _get_schema_for_model(model, sample)

    start = time.monotonic()
    try:
        result = await model.extract(image, schema, sample.document_type)
        elapsed = time.monotonic() - start
    except Exception as e:
        elapsed = time.monotonic() - start
        return DocumentResult(
            document_id=sample.document_id,
            document_type=sample.document_type,
            parse_success=False,
            schema_valid=False,
            elapsed_sec=elapsed,
            error=f"{type(e).__name__}: {e}",
        )

    if result.error:
        return DocumentResult(
            document_id=sample.document_id,
            document_type=sample.document_type,
            parse_success=result.parse_success,
            schema_valid=False,
            elapsed_sec=elapsed,
            error=result.error,
        )

    # Level 1: Parse check
    if result.parse_success and result.parsed_json is not None:
        parsed = result.parsed_json
    else:
        success, parsed = check_parse(result.raw_response)
        if not success or parsed is None:
            return DocumentResult(
                document_id=sample.document_id,
                document_type=sample.document_type,
                parse_success=False,
                schema_valid=False,
                elapsed_sec=elapsed,
            )

    # Level 2: Schema compliance
    is_valid, errors = check_schema_compliance(parsed, sample.schema)

    # Level 3: Field comparison (even if schema not fully valid, compare what we can)
    field_scores = compare_fields(sample.ground_truth, parsed, sample.schema)
    mean_acc = sum(field_scores.values()) / len(field_scores) if field_scores else 0.0

    return DocumentResult(
        document_id=sample.document_id,
        document_type=sample.document_type,
        parse_success=True,
        schema_valid=is_valid,
        validation_errors=errors,
        field_scores=field_scores,
        mean_field_accuracy=mean_acc,
        elapsed_sec=elapsed,
    )


async def evaluate_model(
    model: StructuredOCRModel,
    samples: list[DocumentSample],
) -> ModelResult:
    """Evaluate a model on all document samples."""
    print(f"  Evaluating: {model.name}")

    doc_results: list[DocumentResult] = []
    for sample in samples:
        dr = await evaluate_model_on_document(model, sample)
        doc_results.append(dr)

        status = "OK" if dr.error is None else f"ERR: {dr.error}"
        print(
            f"    [{sample.document_id}] "
            f"acc={dr.mean_field_accuracy:.4f} "
            f"parse={'Y' if dr.parse_success else 'N'} "
            f"schema={'Y' if dr.schema_valid else 'N'} "
            f"({dr.elapsed_sec:.1f}s) {status}"
        )

    return aggregate_document_results(model.name, doc_results)


async def run_evaluation(
    model_names: list[str] | None = None,
    document_types: list[str] | None = None,
    output_path: Path | None = None,
) -> dict:
    """Run evaluation across all selected models and document types."""
    samples = load_dataset(document_types=document_types)
    if not samples:
        print("ERROR: No dataset samples found.")
        print("  Generate data first using /generate-business-doc")
        sys.exit(1)

    type_counts = {}
    for s in samples:
        type_counts[s.document_type] = type_counts.get(s.document_type, 0) + 1
    print(f"Loaded {len(samples)} documents: {type_counts}")
    print()

    if model_names:
        models = get_models_by_name(model_names)
        unavailable = [m for m in models if not m.is_available()]
        if unavailable:
            print("WARNING: Some requested models are not available:")
            for m in unavailable:
                print(f"  - {m.name}")
            print()
        models = [m for m in models if m.is_available()]
    else:
        models = get_available_models()

    if not models:
        print("ERROR: No models available.")
        print()
        for m in get_all_models():
            status = "OK" if m.is_available() else "NOT AVAILABLE"
            print(f"  {m.name:<25s} {status}")
        sys.exit(1)

    print(f"Running with {len(models)} models:")
    for m in models:
        print(f"  - {m.name}")
    print()

    results: list[ModelResult] = []
    for model in models:
        mr = await evaluate_model(model, samples)
        results.append(mr)
        print(
            f"  => {model.name}: "
            f"mean_acc={mr.mean_field_accuracy:.4f} "
            f"parse={mr.parse_success_rate:.2%} "
            f"schema={mr.schema_compliance_rate:.2%}"
        )
        print()

    leaderboard = build_leaderboard(results)
    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "n_documents": len(samples),
        "document_types": list(type_counts.keys()),
        "models": [mr.to_dict() for mr in results],
        "leaderboard": leaderboard,
    }

    if output_path is None:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = RESULTS_DIR / f"structured_eval_{ts}.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Results saved to: {output_path}")
    print()
    print_leaderboard(leaderboard)

    return output


def build_leaderboard(results: list[ModelResult]) -> list[dict]:
    """Build leaderboard sorted by mean_field_accuracy."""
    entries = []
    for r in results:
        entries.append(
            {
                "model": r.model,
                "mean_field_accuracy": round(r.mean_field_accuracy, 6),
                "parse_success_rate": round(r.parse_success_rate, 6),
                "schema_compliance_rate": round(r.schema_compliance_rate, 6),
            }
        )
    entries.sort(key=lambda x: x["mean_field_accuracy"], reverse=True)
    return entries


def print_leaderboard(leaderboard: list[dict]) -> None:
    """Print a formatted leaderboard table."""
    print("=" * 70)
    print(f"{'Rank':<5} {'Model':<25} {'Accuracy':>10} {'Parse':>8} {'Schema':>8}")
    print("-" * 70)
    for i, e in enumerate(leaderboard, 1):
        print(
            f"{i:<5} {e['model']:<25} "
            f"{e['mean_field_accuracy']:>10.4f} "
            f"{e['parse_success_rate']:>7.1%} "
            f"{e['schema_compliance_rate']:>7.1%}"
        )
    print("=" * 70)


def rescore_results(result_path: Path) -> None:
    """Re-compute metrics from saved predictions."""
    with open(result_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Rescoring: {result_path.name}")
    print()

    from .data import DATASET_DIR, _fallback_schema, _load_type_schema

    # Pre-load schemas per type
    _schema_cache: dict[str, dict] = {}

    for model_data in data["models"]:
        doc_results: list[DocumentResult] = []
        for detail in model_data["details"]:
            doc_type = detail["document_type"]
            doc_id = detail["document_id"]

            # Load GT from dataset
            gt_path = DATASET_DIR / doc_type / f"{doc_id}.json"
            if gt_path.exists():
                with open(gt_path, "r", encoding="utf-8") as f:
                    gt = json.load(f)
            else:
                gt = {}

            # Load schema (cached per type)
            if doc_type not in _schema_cache:
                type_dir = DATASET_DIR / doc_type
                _schema_cache[doc_type] = (
                    _load_type_schema(type_dir) or _fallback_schema(doc_type)
                )
            base_schema = _schema_cache[doc_type]

            # Re-parse raw response if needed
            raw = detail.get("raw_response", "")
            parsed = detail.get("parsed_json")
            if parsed is None and raw:
                success, parsed = check_parse(raw)

            if parsed is None:
                doc_results.append(
                    DocumentResult(
                        document_id=doc_id,
                        document_type=doc_type,
                        parse_success=False,
                        schema_valid=False,
                    )
                )
                continue

            is_valid, errors = check_schema_compliance(parsed, base_schema)
            field_scores = compare_fields(gt, parsed, base_schema)
            mean_acc = (
                sum(field_scores.values()) / len(field_scores) if field_scores else 0.0
            )

            doc_results.append(
                DocumentResult(
                    document_id=doc_id,
                    document_type=doc_type,
                    parse_success=True,
                    schema_valid=is_valid,
                    validation_errors=errors,
                    field_scores=field_scores,
                    mean_field_accuracy=mean_acc,
                )
            )

        mr = aggregate_document_results(model_data["model"], doc_results)
        model_data["aggregated"] = mr.to_dict()["aggregated"]
        model_data["details"] = [d.to_dict() for d in doc_results]
        print(
            f"  {mr.model}: acc={mr.mean_field_accuracy:.4f} "
            f"parse={mr.parse_success_rate:.2%}"
        )

    data["leaderboard"] = build_leaderboard(
        [
            ModelResult(
                model=m["model"],
                mean_field_accuracy=m["aggregated"]["mean_field_accuracy"],
                parse_success_rate=m["aggregated"]["parse_success_rate"],
                schema_compliance_rate=m["aggregated"]["schema_compliance_rate"],
            )
            for m in data["models"]
        ]
    )
    data["rescored_at"] = datetime.now(timezone.utc).isoformat()

    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print()
    print(f"Saved to: {result_path}")
    print()
    print_leaderboard(data["leaderboard"])


def inspect_results(result_path: Path, document_id: str | None = None) -> None:
    """Inspect evaluation results: GT vs predictions."""
    with open(result_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Results from: {result_path.name}")
    print(f"Timestamp: {data['timestamp']}")
    print(f"Documents: {data['n_documents']}, Types: {data['document_types']}")
    print()

    for model_data in data["models"]:
        model_name = model_data["model"]
        for detail in model_data["details"]:
            if document_id and detail["document_id"] != document_id:
                continue

            print("=" * 70)
            print(f"Document: {detail['document_id']} ({detail['document_type']})")
            print(f"Model: {model_name}")
            print(
                f"Accuracy: {detail['mean_field_accuracy']:.4f} "
                f"Parse: {'Y' if detail['parse_success'] else 'N'} "
                f"Schema: {'Y' if detail['schema_valid'] else 'N'}"
            )
            if detail.get("error"):
                print(f"Error: {detail['error']}")
            print()

            if detail.get("field_scores"):
                print(f"  {'Field':<30} {'Score':>8}")
                print(f"  {'-'*30} {'-'*8}")
                for field_name, score in sorted(detail["field_scores"].items()):
                    print(f"  {field_name:<30} {score:>8.4f}")
            print()


def _find_latest_result() -> Path | None:
    if not RESULTS_DIR.exists():
        return None
    files = sorted(RESULTS_DIR.glob("structured_eval_*.json"), reverse=True)
    return files[0] if files else None


def main():
    parser = argparse.ArgumentParser(description="Structured Output Evaluation")
    sub = parser.add_subparsers(dest="command")

    # run
    run_parser = sub.add_parser("run", help="Run evaluation")
    run_parser.add_argument(
        "--models", nargs="*",
        help="Specific model names to evaluate (default: all available)",
    )
    run_parser.add_argument(
        "--types", nargs="*",
        help="Document types to evaluate (default: all)",
    )
    run_parser.add_argument("--output", type=Path, help="Output JSON file path")

    # inspect
    inspect_parser = sub.add_parser("inspect", help="Inspect results")
    inspect_parser.add_argument(
        "result_file", nargs="?", type=Path,
        help="Result JSON file (default: latest)",
    )
    inspect_parser.add_argument("--document", type=str, help="Filter by document ID")

    # rescore
    rescore_parser = sub.add_parser("rescore", help="Re-compute metrics")
    rescore_parser.add_argument("result_files", nargs="*", type=Path)

    # list-models
    sub.add_parser("list-models", help="List all models and availability")

    # list-schemas
    sub.add_parser("list-schemas", help="List all document schemas")

    args = parser.parse_args()

    if args.command == "list-models":
        print(f"{'Model':<25} {'Status'}")
        print("-" * 40)
        for m in get_all_models():
            status = "OK" if m.is_available() else "NOT AVAILABLE"
            print(f"{m.name:<25} {status}")

    elif args.command == "list-schemas":
        schemas = get_all_schemas()
        for doc_type, schema_cls in schemas.items():
            print(f"\n{'='*50}")
            print(f"Type: {doc_type} ({schema_cls.document_type_ja()})")
            print(f"{'='*50}")
            schema = generate_json_schema(schema_cls)
            props = schema.get("properties", {})
            required = set(schema.get("required", []))
            for name, prop in props.items():
                req = "*" if name in required else " "
                desc = prop.get("description", "")
                print(f"  {req} {name:<30} {desc}")

    elif args.command == "inspect":
        result_file = args.result_file or _find_latest_result()
        if not result_file or not result_file.exists():
            print("No result file found. Run evaluation first.")
            sys.exit(1)
        inspect_results(result_file, document_id=args.document)

    elif args.command == "rescore":
        files = args.result_files
        if not files:
            files = sorted(RESULTS_DIR.glob("structured_eval_*.json"))
        if not files:
            print("No result files found.")
            sys.exit(1)
        for f in files:
            rescore_results(f)

    else:
        # Default: run
        models = getattr(args, "models", None)
        types_ = getattr(args, "types", None)
        output = getattr(args, "output", None)
        asyncio.run(run_evaluation(
            model_names=models, document_types=types_, output_path=output,
        ))


if __name__ == "__main__":
    main()
