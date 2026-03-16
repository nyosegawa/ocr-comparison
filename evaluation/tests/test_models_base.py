"""Tests for src/models/base.py — OCRModel base class utilities."""

from __future__ import annotations

import base64

from PIL import Image

from src.models.base import MAX_BASE64_BYTES, OCR_PROMPT_JA, OCRModel, _encode_b64


class TestEncodeB64:
    def test_png_encoding(self, small_rgb_image):
        b64 = _encode_b64(small_rgb_image, "PNG")
        decoded = base64.standard_b64decode(b64)
        # PNG magic bytes
        assert decoded[:4] == b"\x89PNG"

    def test_jpeg_encoding(self, small_rgb_image):
        b64 = _encode_b64(small_rgb_image, "JPEG")
        decoded = base64.standard_b64decode(b64)
        # JPEG magic bytes
        assert decoded[:2] == b"\xff\xd8"

    def test_rgba_to_jpeg_converts_to_rgb(self, small_rgba_image):
        """RGBA images should be converted to RGB for JPEG."""
        b64 = _encode_b64(small_rgba_image, "JPEG")
        decoded = base64.standard_b64decode(b64)
        assert decoded[:2] == b"\xff\xd8"


class TestImageToBase64:
    def test_small_image_returns_png(self, small_rgb_image):
        b64 = OCRModel.image_to_base64(small_rgb_image, format="PNG")
        assert len(b64) <= MAX_BASE64_BYTES

    def test_returns_valid_base64(self, small_rgb_image):
        b64 = OCRModel.image_to_base64(small_rgb_image)
        # Should not raise
        base64.standard_b64decode(b64)

    def test_large_image_gets_compressed(self):
        """A very large image should be downscaled or JPEG compressed."""
        # 4000x4000 random-ish image (PNG will be large)
        img = Image.new("RGB", (4000, 4000), color=(128, 64, 32))
        b64 = OCRModel.image_to_base64(img)
        assert len(b64) <= MAX_BASE64_BYTES


class TestImageToBytes:
    def test_returns_bytes(self, small_rgb_image):
        data = OCRModel.image_to_bytes(small_rgb_image)
        assert isinstance(data, bytes)
        assert len(data) > 0

    def test_png_format(self, small_rgb_image):
        data = OCRModel.image_to_bytes(small_rgb_image, format="PNG")
        assert data[:4] == b"\x89PNG"


class TestImageMediaType:
    def test_small_image_returns_png(self, small_rgb_image):
        mt = OCRModel.image_media_type(small_rgb_image)
        assert mt == "image/png"

    def test_large_image_returns_jpeg(self):
        """Solid-color images compress well as PNG, so need a larger/noisier image."""
        import numpy as np
        arr = np.random.randint(0, 256, (6000, 6000, 3), dtype=np.uint8)
        img = Image.fromarray(arr)
        mt = OCRModel.image_media_type(img)
        assert mt == "image/jpeg"


class TestOcrPrompt:
    def test_prompt_is_japanese(self):
        assert "テキスト" in OCR_PROMPT_JA
        assert "画像" in OCR_PROMPT_JA
