"""Dataset loader for structured evaluation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

DATASET_DIR = Path(__file__).resolve().parent.parent / "dataset"


@dataclass
class DocumentSample:
    """A single document sample with image and ground truth."""

    document_id: str
    document_type: str
    image_path: Path
    ground_truth: dict
    schema: dict

    def load_image(self) -> Image.Image:
        return Image.open(self.image_path).convert("RGB")


def _load_type_schema(type_dir: Path) -> dict | None:
    """Load schema.json from a document type directory."""
    schema_path = type_dir / "schema.json"
    if schema_path.exists():
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def _fallback_schema(document_type: str) -> dict:
    """Fall back to Pydantic registry schema if schema.json not found."""
    try:
        from .schemas.base import generate_json_schema, get_schema

        schema_cls = get_schema(document_type)
        return generate_json_schema(schema_cls)
    except (KeyError, ImportError):
        return {}


def load_dataset(
    document_types: list[str] | None = None,
    dataset_dir: Path | None = None,
) -> list[DocumentSample]:
    """Load all document samples from the dataset directory.

    Each document type has its own subdirectory containing:
    - schema.json — the JSON Schema for this document type
    - {id}.png — the document image
    - {id}.json — the ground truth structured data
    - {id}.html — the generated layout (optional, not loaded)
    """
    base = dataset_dir or DATASET_DIR
    samples: list[DocumentSample] = []

    if not base.exists():
        return samples

    for type_dir in sorted(base.iterdir()):
        if not type_dir.is_dir():
            continue

        doc_type = type_dir.name
        if document_types and doc_type not in document_types:
            continue

        # Load schema: prefer schema.json, fall back to Pydantic registry
        schema = _load_type_schema(type_dir) or _fallback_schema(doc_type)

        for img_path in sorted(type_dir.glob("*.png")):
            json_path = img_path.with_suffix(".json")
            if not json_path.exists():
                continue

            with open(json_path, "r", encoding="utf-8") as f:
                gt = json.load(f)

            # Extract just the ground_truth portion if wrapped
            ground_truth = gt.get("ground_truth", gt) if isinstance(gt, dict) else gt

            # Extract just the ground_truth sub-schema if the schema wraps it
            extraction_schema = schema
            if (
                isinstance(schema, dict)
                and "properties" in schema
                and "ground_truth" in schema["properties"]
            ):
                extraction_schema = schema["properties"]["ground_truth"]

            samples.append(
                DocumentSample(
                    document_id=img_path.stem,
                    document_type=doc_type,
                    image_path=img_path,
                    ground_truth=ground_truth,
                    schema=extraction_schema,
                )
            )

    return samples


def load_manifest(dataset_dir: Path | None = None) -> dict:
    """Load the dataset manifest for diversity tracking."""
    base = dataset_dir or DATASET_DIR
    manifest_path = base / "manifest.json"
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"generated": [], "coverage": {}}
