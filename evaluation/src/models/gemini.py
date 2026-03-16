"""Gemini (Google) OCR adapter."""

from __future__ import annotations

import os

from PIL import Image

from .base import OCR_PROMPT_JA, OCRModel


class GeminiOCR(OCRModel):
    name = "gemini-3.1-pro-preview"
    category = "api"
    weights_url = None
    license = None

    def __init__(self, model_id: str = "gemini-3.1-pro-preview", *, thinking_level: str = "high"):
        self.model_id = model_id
        self.name = model_id
        self.thinking_level = thinking_level

    def is_available(self) -> bool:
        return bool(os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY"))

    async def recognize(self, image: Image.Image) -> str:
        from google import genai
        from google.genai import types

        client = genai.Client()
        img_bytes = self.image_to_bytes(image)

        response = await client.aio.models.generate_content(
            model=self.model_id,
            contents=[
                genai.types.Part.from_bytes(data=img_bytes, mime_type="image/png"),
                OCR_PROMPT_JA,
            ],
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    thinking_level=self.thinking_level,
                ),
            ),
        )

        return response.text.strip()
