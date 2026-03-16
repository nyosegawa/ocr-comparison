"""Main evaluation runner."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

# Load .env from evaluation/ directory
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _key, _, _val = _line.partition("=")
                _key = _key.strip()
                _val = _val.strip().split("#")[0].strip()  # remove inline comments
                if _val and _key not in os.environ:  # don't override existing env
                    os.environ[_key] = _val

# Alias: GEMINI_API_KEY -> GOOGLE_API_KEY (google-genai SDK expects GOOGLE_API_KEY)
if not os.environ.get("GOOGLE_API_KEY") and os.environ.get("GEMINI_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]

from .data import ImageAnnotation, load_annotations, load_image
from .metrics import EvalResult, aggregate_results, evaluate_image
from .models.base import OCRModel
from .models.modal_runner import ModalOCRModel
from .models.registry import get_all_models, get_available_models, get_models_by_name

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"


async def evaluate_model_on_image(
    model: OCRModel,
    img_ann: ImageAnnotation,
) -> dict:
    """Run a model on the full image and evaluate against GT regions."""
    image = load_image(img_ann.image_path)
    gt_regions = [a.text for a in img_ann.annotations]

    start = time.monotonic()
    try:
        predicted = await model.recognize(image)
        elapsed = time.monotonic() - start
        error = None
    except Exception as e:
        elapsed = time.monotonic() - start
        predicted = ""
        error = f"{type(e).__name__}: {e}"

    metrics = evaluate_image(gt_regions, predicted)

    return {
        "image_id": img_ann.image_id,
        "gt_regions": gt_regions,
        "prediction": predicted,
        "error": error,
        "elapsed_sec": round(elapsed, 3),
        "metrics": asdict(metrics),
    }


async def evaluate_modal_model(
    model: ModalOCRModel,
    annotations: list[ImageAnnotation],
) -> dict:
    """Evaluate a Modal model using batch processing."""
    print(f"  Evaluating: {model.name} ({model.category}) [Modal batch]")

    images = [load_image(a.image_path) for a in annotations]

    start = time.monotonic()
    try:
        predictions = await model.recognize_batch(images)
        elapsed = time.monotonic() - start
        batch_error = None
    except Exception as e:
        elapsed = time.monotonic() - start
        predictions = [""] * len(images)
        batch_error = f"{type(e).__name__}: {e}"
        print(f"    BATCH ERROR: {batch_error}")

    print(f"    Batch completed in {elapsed:.1f}s ({len(images)} images)")

    all_results = []
    all_metrics: list[EvalResult] = []

    for i, img_ann in enumerate(annotations):
        gt_regions = [a.text for a in img_ann.annotations]
        predicted = predictions[i] if i < len(predictions) else ""
        error = batch_error

        metrics = evaluate_image(gt_regions, predicted)
        result = {
            "image_id": img_ann.image_id,
            "gt_regions": gt_regions,
            "prediction": predicted,
            "error": error,
            "elapsed_sec": round(elapsed / len(images), 3),
            "metrics": asdict(metrics),
        }
        all_results.append(result)

        if error is None:
            all_metrics.append(metrics)

        print(
            f"    [{img_ann.image_id}] "
            f"NLS={metrics.hungarian_nls:.4f} "
            f"BoC-F1={metrics.boc_f1:.4f} "
            f"CER={metrics.cer:.4f} "
            f"{'OK' if error is None else 'ERR'}"
        )

    aggregated = aggregate_results(all_metrics)

    return {
        "model": model.name,
        "category": model.category,
        "aggregated": aggregated,
        "details": all_results,
    }


async def evaluate_model(
    model: OCRModel,
    annotations: list[ImageAnnotation],
) -> dict:
    """Evaluate a model on all images."""
    if isinstance(model, ModalOCRModel):
        return await evaluate_modal_model(model, annotations)

    print(f"  Evaluating: {model.name} ({model.category})")

    all_results = []
    all_metrics: list[EvalResult] = []

    for img_ann in annotations:
        result = await evaluate_model_on_image(model, img_ann)
        all_results.append(result)

        metrics = EvalResult(**result["metrics"])
        if result["error"] is None:
            all_metrics.append(metrics)

        status = "OK" if result["error"] is None else f"ERR: {result['error']}"
        print(
            f"    [{img_ann.image_id}] "
            f"NLS={metrics.hungarian_nls:.4f} "
            f"BoC-F1={metrics.boc_f1:.4f} "
            f"CER={metrics.cer:.4f} "
            f"({result['elapsed_sec']:.1f}s) {status}"
        )

    aggregated = aggregate_results(all_metrics)

    return {
        "model": model.name,
        "category": model.category,
        "aggregated": aggregated,
        "details": all_results,
    }


async def run_evaluation(
    model_names: list[str] | None = None,
    output_path: Path | None = None,
) -> dict:
    """Run evaluation across all selected models."""
    annotations = load_annotations()
    if not annotations:
        print("ERROR: No annotations with ground truth text found.")
        print("  Please add text to annotations using the annotation tool first.")
        sys.exit(1)

    total_gt_chars = sum(
        sum(len(a.text) for a in img.annotations) for img in annotations
    )
    print(f"Loaded {len(annotations)} images ({total_gt_chars} GT chars total)")
    print()

    if model_names:
        models = get_models_by_name(model_names)
        unavailable = [m for m in models if not m.is_available()]
        if unavailable:
            print("WARNING: Some requested models are not available:")
            for m in unavailable:
                print(f"  - {m.name}: check configuration")
            print()
        models = [m for m in models if m.is_available()]
    else:
        models = get_available_models()

    if not models:
        print("ERROR: No models available.")
        print()
        for m in get_all_models():
            status = "OK" if m.is_available() else "NOT AVAILABLE"
            print(f"  {m.name:25s} [{m.category:5s}] {status}")
        sys.exit(1)

    print(f"Running evaluation with {len(models)} models:")
    for m in models:
        print(f"  - {m.name} ({m.category})")
    print()

    results = []
    for model in models:
        result = await evaluate_model(model, annotations)
        results.append(result)
        agg = result["aggregated"]
        print(
            f"  => {model.name}: "
            f"NLS={agg.get('hungarian_nls', 0):.4f} "
            f"BoC-F1={agg.get('boc_f1', 0):.4f} "
            f"CER={agg.get('cer', 0):.4f}"
        )
        print()

    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "n_images": len(annotations),
        "total_gt_chars": total_gt_chars,
        "models": results,
        "leaderboard": build_leaderboard(results),
    }

    if output_path is None:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = RESULTS_DIR / f"eval_{ts}.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Results saved to: {output_path}")
    print()
    print_leaderboard(output["leaderboard"])

    return output


def build_leaderboard(results: list[dict]) -> list[dict]:
    """Build leaderboard sorted by Hungarian NLS (primary metric)."""
    entries = []
    for r in results:
        agg = r["aggregated"]
        entries.append(
            {
                "model": r["model"],
                "category": r["category"],
                "hungarian_nls": agg.get("hungarian_nls", 0),
                "boc_f1": agg.get("boc_f1", 0),
                "cer": agg.get("cer", 0),
                "ned": agg.get("ned", 0),
                "n_images": agg.get("n_images", 0),
            }
        )
    # Sort by Hungarian NLS descending (higher is better)
    entries.sort(key=lambda x: x["hungarian_nls"], reverse=True)
    return entries


def print_leaderboard(leaderboard: list[dict]) -> None:
    """Print a formatted leaderboard table."""
    print("=" * 80)
    print(
        f"{'Rank':<5} {'Model':<25} "
        f"{'NLS':>7} {'BoC-F1':>8} {'CER':>7} {'NED':>7} {'Cat'}"
    )
    print("-" * 80)
    for i, e in enumerate(leaderboard, 1):
        print(
            f"{i:<5} {e['model']:<25} "
            f"{e['hungarian_nls']:>7.4f} "
            f"{e['boc_f1']:>8.4f} "
            f"{e['cer']:>7.4f} "
            f"{e['ned']:>7.4f} "
            f"{e['category']}"
        )
    print("=" * 80)
    print()
    print("NLS  = Hungarian Matching NLS (primary, reading-order independent)")
    print("BoC  = Bag-of-Characters F1 (character recognition quality)")
    print("CER  = Character Error Rate (lower is better)")
    print("NED  = Normalized Edit Distance (higher is better)")


def rescore_results(result_path: Path) -> None:
    """Re-compute metrics from saved predictions using current scoring logic."""
    with open(result_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Rescoring: {result_path.name}")
    print(f"Original timestamp: {data['timestamp']}")
    print()

    for model_result in data["models"]:
        all_metrics: list[EvalResult] = []

        for detail in model_result["details"]:
            gt_regions = detail.get("gt_regions")
            if gt_regions is None:
                # Fallback: old format stored "ground_truth" as single string
                gt_text = detail.get("ground_truth", "")
                gt_regions = [gt_text] if gt_text else []

            pred = detail.get("prediction", "")
            error = detail.get("error")

            metrics = evaluate_image(gt_regions, pred)
            detail["metrics"] = asdict(metrics)

            if error is None:
                all_metrics.append(metrics)

        model_result["aggregated"] = aggregate_results(all_metrics)

        agg = model_result["aggregated"]
        print(
            f"  {model_result['model']}: "
            f"NLS={agg.get('hungarian_nls', 0):.4f} "
            f"BoC-F1={agg.get('boc_f1', 0):.4f} "
            f"CER={agg.get('cer', 0):.4f}"
        )

    data["leaderboard"] = build_leaderboard(data["models"])
    data["rescored_at"] = datetime.now(timezone.utc).isoformat()

    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print()
    print(f"Saved to: {result_path}")
    print()
    print_leaderboard(data["leaderboard"])


def inspect_results(result_path: Path, image_id: str | None = None) -> None:
    """Inspect evaluation results: show GT vs each model's prediction side-by-side."""
    with open(result_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Results from: {result_path.name}")
    print(f"Timestamp: {data['timestamp']}")
    print(f"Images: {data['n_images']}, GT chars: {data['total_gt_chars']}")
    print()

    # Collect all image IDs
    all_image_ids: list[str] = []
    for model_result in data["models"]:
        for detail in model_result["details"]:
            iid = detail["image_id"]
            if iid not in all_image_ids:
                all_image_ids.append(iid)

    if image_id:
        all_image_ids = [iid for iid in all_image_ids if iid == image_id]
        if not all_image_ids:
            print(f"Image '{image_id}' not found. Available:")
            for model_result in data["models"]:
                for detail in model_result["details"]:
                    print(f"  - {detail['image_id']}")
            return

    for iid in all_image_ids:
        print("=" * 80)
        print(f"IMAGE: {iid}")
        print("=" * 80)

        # Find GT from first model's detail
        gt_text = None
        for model_result in data["models"]:
            for detail in model_result["details"]:
                if detail["image_id"] == iid:
                    gt_regions = detail.get("gt_regions", [])
                    gt_text = "\n".join(gt_regions) if gt_regions else detail.get("ground_truth", "")
                    break
            if gt_text is not None:
                break

        print()
        print("--- Ground Truth ---")
        print(gt_text or "(empty)")
        print()

        for model_result in data["models"]:
            model_name = model_result["model"]

            for detail in model_result["details"]:
                if detail["image_id"] != iid:
                    continue

                m = detail["metrics"]
                pred = detail.get("prediction", "")
                error = detail.get("error")

                print(f"--- {model_name} ---")
                if error:
                    print(f"  ERROR: {error}")
                else:
                    print(
                        f"  NLS={m['hungarian_nls']:.4f}  "
                        f"BoC-F1={m['boc_f1']:.4f}  "
                        f"CER={m['cer']:.4f}"
                    )
                print()
                print(_indent(pred or "(empty)", "  "))
                print()

        print()


def _indent(text: str, prefix: str) -> str:
    """Indent each line of text."""
    return "\n".join(prefix + line for line in text.splitlines())


def _find_latest_result() -> Path | None:
    """Find the most recent result file."""
    if not RESULTS_DIR.exists():
        return None
    files = sorted(RESULTS_DIR.glob("eval_*.json"), reverse=True)
    return files[0] if files else None


def main():
    parser = argparse.ArgumentParser(description="OCR Model Evaluation")
    sub = parser.add_subparsers(dest="command")

    # run (default)
    run_parser = sub.add_parser("run", help="Run evaluation")
    run_parser.add_argument(
        "--models", nargs="*",
        help="Specific model names to evaluate (default: all available)",
    )
    run_parser.add_argument("--output", type=Path, help="Output JSON file path")

    # inspect
    inspect_parser = sub.add_parser("inspect", help="Inspect results: GT vs predictions")
    inspect_parser.add_argument(
        "result_file", nargs="?", type=Path,
        help="Result JSON file (default: latest)",
    )
    inspect_parser.add_argument(
        "--image", type=str,
        help="Show only this image ID",
    )

    # rescore
    rescore_parser = sub.add_parser("rescore", help="Re-compute metrics from saved predictions")
    rescore_parser.add_argument(
        "result_files", nargs="*", type=Path,
        help="Result JSON files to rescore (default: all)",
    )

    # list-models
    sub.add_parser("list-models", help="List all models and availability")

    args = parser.parse_args()

    if args.command == "list-models":
        print(f"{'Model':<25} {'Category':<8} {'Status'}")
        print("-" * 50)
        for m in get_all_models():
            status = "OK" if m.is_available() else "NOT AVAILABLE"
            print(f"{m.name:<25} {m.category:<8} {status}")

    elif args.command == "inspect":
        result_file = args.result_file or _find_latest_result()
        if not result_file or not result_file.exists():
            print("No result file found. Run evaluation first.")
            sys.exit(1)
        inspect_results(result_file, image_id=args.image)

    elif args.command == "rescore":
        files = args.result_files
        if not files:
            files = sorted(RESULTS_DIR.glob("eval_*.json"))
        if not files:
            print("No result files found.")
            sys.exit(1)
        for f in files:
            rescore_results(f)
            print()

    else:
        # Default: run evaluation
        models = getattr(args, "models", None)
        output = getattr(args, "output", None)
        asyncio.run(run_evaluation(model_names=models, output_path=output))


if __name__ == "__main__":
    main()
