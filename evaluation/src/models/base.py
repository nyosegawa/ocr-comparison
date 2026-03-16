"""Base class for OCR model adapters."""

from __future__ import annotations

import base64
import io
from abc import ABC, abstractmethod

from PIL import Image

# Max base64 size: 4MB (safe for all APIs; Claude limit is 5MB)
MAX_BASE64_BYTES = 4 * 1024 * 1024


class OCRModel(ABC):
    """Abstract base class for OCR model adapters."""

    name: str
    category: str  # "api", "modal"
    weights_url: str | None = None  # URL to model weights (HuggingFace, GitHub, etc.)
    license: str | None = None  # SPDX license identifier or short name

    @abstractmethod
    async def recognize(self, image: Image.Image) -> str:
        """Run OCR on an image and return recognized text."""
        ...

    def is_available(self) -> bool:
        """Check if this model is available."""
        return True

    @staticmethod
    def image_to_base64(image: Image.Image, format: str = "PNG") -> str:
        """Convert PIL Image to base64, resizing if too large for API limits."""
        b64 = _encode_b64(image, format)
        if len(b64) <= MAX_BASE64_BYTES:
            return b64

        # Try JPEG compression first (much smaller than PNG)
        if format == "PNG":
            b64 = _encode_b64(image, "JPEG", quality=90)
            if len(b64) <= MAX_BASE64_BYTES:
                return b64

        # Progressively downscale
        img = image.copy()
        for scale in [0.75, 0.5, 0.35, 0.25]:
            new_size = (int(img.width * scale), int(img.height * scale))
            resized = image.resize(new_size, Image.LANCZOS)
            b64 = _encode_b64(resized, "JPEG", quality=85)
            if len(b64) <= MAX_BASE64_BYTES:
                return b64

        return b64  # Return smallest attempt even if still over

    @staticmethod
    def image_to_bytes(image: Image.Image, format: str = "PNG") -> bytes:
        """Convert PIL Image to bytes."""
        buf = io.BytesIO()
        image.save(buf, format=format)
        return buf.getvalue()

    @staticmethod
    def image_media_type(image: Image.Image) -> str:
        """Determine the media type to use for this image after encoding."""
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        size = buf.tell()
        # If PNG is too large, we'll use JPEG
        return "image/png" if size <= MAX_BASE64_BYTES * 0.75 else "image/jpeg"


def _encode_b64(image: Image.Image, fmt: str, **kwargs) -> str:
    buf = io.BytesIO()
    save_img = image
    if fmt == "JPEG" and image.mode == "RGBA":
        save_img = image.convert("RGB")
    save_img.save(buf, format=fmt, **kwargs)
    return base64.standard_b64encode(buf.getvalue()).decode("utf-8")


OCR_PROMPT_JA = (
    "この画像に書かれているテキストを正確に読み取ってください。"
    "テキストのみを出力してください。余計な説明は不要です。"
)
