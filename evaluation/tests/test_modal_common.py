"""Tests for modal_scripts/_common.py — shared Modal utilities."""

from __future__ import annotations

import base64
import io
import json
import tempfile
from pathlib import Path

import pytest
from PIL import Image

import sys

# Add modal_scripts to path so we can import _common
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "modal_scripts"))

from _common import OCR_PROMPT_JA, decode_images, load_input, save_output


class TestOcrPromptJa:
    def test_prompt_matches_base(self):
        from src.models.base import OCR_PROMPT_JA as BASE_PROMPT
        assert OCR_PROMPT_JA == BASE_PROMPT

    def test_prompt_content(self):
        assert "テキスト" in OCR_PROMPT_JA


class TestDecodeImages:
    def _make_b64_image(self, width: int = 10, height: int = 10) -> str:
        img = Image.new("RGB", (width, height), color=(255, 0, 0))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")

    def test_single_image(self):
        b64 = self._make_b64_image()
        images = decode_images([b64])
        assert len(images) == 1
        assert isinstance(images[0], Image.Image)
        assert images[0].mode == "RGB"

    def test_multiple_images(self):
        images_b64 = [self._make_b64_image(w, w) for w in [10, 20, 30]]
        images = decode_images(images_b64)
        assert len(images) == 3
        assert images[0].size == (10, 10)
        assert images[1].size == (20, 20)
        assert images[2].size == (30, 30)

    def test_empty_list(self):
        assert decode_images([]) == []


class TestLoadInput:
    def test_loads_json(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"images": ["abc", "def"]}, f)
            f.flush()
            data = load_input(f.name)
        assert data == {"images": ["abc", "def"]}


class TestSaveOutput:
    def test_saves_json(self):
        with tempfile.NamedTemporaryFile(mode="r", suffix=".json", delete=False) as f:
            save_output(f.name, ["result1", "result2"])
            data = json.load(open(f.name))
        assert data == {"results": ["result1", "result2"]}

    def test_unicode_preserved(self):
        with tempfile.NamedTemporaryFile(mode="r", suffix=".json", delete=False) as f:
            save_output(f.name, ["日本語テキスト"])
            raw = open(f.name).read()
        assert "日本語テキスト" in raw  # ensure_ascii=False
