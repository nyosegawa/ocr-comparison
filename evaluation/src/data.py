"""Load ground truth data from annotation tool."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

ANNOTATION_ROOT = Path(__file__).resolve().parent.parent.parent / "annotation"
ANNOTATIONS_DIR = ANNOTATION_ROOT / "data" / "annotations"
IMAGES_MANIFEST = ANNOTATION_ROOT / "data" / "images.json"
UPLOADS_DIR = ANNOTATION_ROOT / "uploads"


@dataclass
class AnnotationEntry:
    id: str
    text: str


@dataclass
class ImageAnnotation:
    image_id: str
    image_path: Path
    width: int
    height: int
    annotations: list[AnnotationEntry]

    @property
    def ground_truth(self) -> str:
        """Concatenate all annotation texts as the full ground truth for this image."""
        return "\n".join(a.text for a in self.annotations)


def load_annotations() -> list[ImageAnnotation]:
    """Load all annotations that have non-empty text (valid ground truth)."""
    results = []

    if not ANNOTATIONS_DIR.exists():
        return results

    for json_path in sorted(ANNOTATIONS_DIR.glob("*.json")):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Resolve image path
        rel_path = data.get("imagePath", "")
        if rel_path.startswith("/uploads/"):
            image_path = UPLOADS_DIR / rel_path.removeprefix("/uploads/")
        else:
            image_path = ANNOTATION_ROOT / rel_path.lstrip("/")

        entries = []
        for ann in data.get("annotations", []):
            text = ann.get("text", "").strip()
            if not text:
                continue
            entries.append(AnnotationEntry(id=ann["id"], text=text))

        if not entries:
            continue

        results.append(
            ImageAnnotation(
                image_id=data["imageId"],
                image_path=image_path,
                width=data.get("width", 0),
                height=data.get("height", 0),
                annotations=entries,
            )
        )

    return results


def load_image(image_path: Path) -> Image.Image:
    """Load full image."""
    return Image.open(image_path).convert("RGB")
