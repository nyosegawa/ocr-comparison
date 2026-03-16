"""Tests for src/data.py — annotation data loading."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.data import AnnotationEntry, ImageAnnotation, load_annotations


class TestAnnotationEntry:
    def test_attributes(self):
        entry = AnnotationEntry(id="ann_1", text="hello")
        assert entry.id == "ann_1"
        assert entry.text == "hello"


class TestImageAnnotation:
    def test_ground_truth(self):
        entries = [
            AnnotationEntry(id="1", text="line 1"),
            AnnotationEntry(id="2", text="line 2"),
        ]
        ann = ImageAnnotation(
            image_id="img_1",
            image_path=Path("/tmp/test.png"),
            width=100,
            height=200,
            annotations=entries,
        )
        assert ann.ground_truth == "line 1\nline 2"

    def test_ground_truth_single(self):
        entries = [AnnotationEntry(id="1", text="only line")]
        ann = ImageAnnotation(
            image_id="img_1",
            image_path=Path("/tmp/test.png"),
            width=100,
            height=200,
            annotations=entries,
        )
        assert ann.ground_truth == "only line"


class TestLoadAnnotations:
    def test_loads_from_directory(self, tmp_path):
        annotations_dir = tmp_path / "data" / "annotations"
        annotations_dir.mkdir(parents=True)
        uploads_dir = tmp_path / "uploads"
        uploads_dir.mkdir()

        ann_data = {
            "imageId": "img_001",
            "imagePath": "/uploads/img_001.png",
            "width": 800,
            "height": 600,
            "annotations": [
                {"id": "a1", "text": "テスト", "rect": {"x": 0, "y": 0, "w": 100, "h": 50}},
            ],
        }
        with open(annotations_dir / "img_001.json", "w") as f:
            json.dump(ann_data, f)

        with patch("src.data.ANNOTATIONS_DIR", annotations_dir), \
             patch("src.data.UPLOADS_DIR", uploads_dir), \
             patch("src.data.ANNOTATION_ROOT", tmp_path):
            results = load_annotations()

        assert len(results) == 1
        assert results[0].image_id == "img_001"
        assert results[0].width == 800
        assert results[0].annotations[0].text == "テスト"

    def test_skips_empty_annotations(self, tmp_path):
        annotations_dir = tmp_path / "data" / "annotations"
        annotations_dir.mkdir(parents=True)

        ann_data = {
            "imageId": "img_002",
            "imagePath": "/uploads/img_002.png",
            "width": 100,
            "height": 100,
            "annotations": [
                {"id": "a1", "text": "", "rect": {}},  # empty text
            ],
        }
        with open(annotations_dir / "img_002.json", "w") as f:
            json.dump(ann_data, f)

        with patch("src.data.ANNOTATIONS_DIR", annotations_dir), \
             patch("src.data.ANNOTATION_ROOT", tmp_path):
            results = load_annotations()

        assert len(results) == 0  # no valid annotations

    def test_missing_directory(self, tmp_path):
        nonexistent = tmp_path / "nonexistent"
        with patch("src.data.ANNOTATIONS_DIR", nonexistent):
            results = load_annotations()
        assert results == []
