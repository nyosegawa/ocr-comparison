"""Base class for structured OCR model adapters."""

from __future__ import annotations

import base64
import io
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from PIL import Image

MAX_BASE64_BYTES = 4 * 1024 * 1024

EXTRACTION_PROMPT_JA = (
    "この{document_type_ja}の画像から情報を正確に読み取り、"
    "指定されたスキーマに従って構造化データとして出力してください。"
    "画像に含まれていない情報のフィールドにはnullを設定してください。"
)


@dataclass
class ExtractResult:
    """Result of a structured extraction attempt."""

    raw_response: str = ""
    parsed_json: dict[str, Any] | None = None
    parse_success: bool = False
    schema_valid: bool = False
    validation_errors: list[str] = field(default_factory=list)
    elapsed_sec: float = 0.0
    error: str | None = None


class StructuredOCRModel(ABC):
    """Abstract base class for structured output OCR model adapters."""

    name: str
    category: str = "api"

    @abstractmethod
    async def extract(
        self, image: Image.Image, schema: dict, document_type: str
    ) -> ExtractResult:
        """Extract structured data from an image according to a JSON schema."""
        ...

    def is_available(self) -> bool:
        return True

    @staticmethod
    def image_to_base64(image: Image.Image, format: str = "PNG") -> str:
        """Convert PIL Image to base64, resizing if too large for API limits."""
        b64 = _encode_b64(image, format)
        if len(b64) <= MAX_BASE64_BYTES:
            return b64

        if format == "PNG":
            b64 = _encode_b64(image, "JPEG", quality=90)
            if len(b64) <= MAX_BASE64_BYTES:
                return b64

        for scale in [0.75, 0.5, 0.35, 0.25]:
            new_size = (int(image.width * scale), int(image.height * scale))
            resized = image.resize(new_size, Image.LANCZOS)
            b64 = _encode_b64(resized, "JPEG", quality=85)
            if len(b64) <= MAX_BASE64_BYTES:
                return b64

        return b64

    @staticmethod
    def image_to_bytes(image: Image.Image, format: str = "PNG") -> bytes:
        buf = io.BytesIO()
        image.save(buf, format=format)
        return buf.getvalue()

    @staticmethod
    def image_media_type(image: Image.Image) -> str:
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        size = buf.tell()
        return "image/png" if size <= MAX_BASE64_BYTES * 0.75 else "image/jpeg"


def _encode_b64(image: Image.Image, fmt: str, **kwargs) -> str:
    buf = io.BytesIO()
    save_img = image
    if fmt == "JPEG" and image.mode == "RGBA":
        save_img = image.convert("RGB")
    save_img.save(buf, format=fmt, **kwargs)
    return base64.standard_b64encode(buf.getvalue()).decode("utf-8")
