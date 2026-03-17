"""Gemini structured output adapter using response_schema."""

from __future__ import annotations

import json
import os

from PIL import Image

from .base import EXTRACTION_PROMPT_JA, ExtractResult, StructuredOCRModel


class GeminiStructured(StructuredOCRModel):
    name = "gemini-3.1-pro-preview"
    category = "api"

    def __init__(self, model_id: str = "gemini-3.1-pro-preview", name: str | None = None):
        self.model_id = model_id
        if name is not None:
            self.name = name

    def is_available(self) -> bool:
        return bool(os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY"))

    async def extract(
        self, image: Image.Image, schema: dict, document_type: str
    ) -> ExtractResult:
        from google import genai
        from google.genai import types

        client = genai.Client()
        img_bytes = self.image_to_bytes(image)

        from ..schemas.base import get_schema
        schema_cls = get_schema(document_type)
        prompt = EXTRACTION_PROMPT_JA.format(
            document_type_ja=schema_cls.document_type_ja()
        )

        try:
            response = await client.aio.models.generate_content(
                model=self.model_id,
                contents=[
                    genai.types.Part.from_bytes(data=img_bytes, mime_type="image/png"),
                    prompt,
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=schema,
                ),
            )
        except Exception as e:
            return ExtractResult(error=f"{type(e).__name__}: {e}")

        raw = response.text.strip() if response.text else ""
        try:
            parsed = json.loads(raw)
            return ExtractResult(
                raw_response=raw,
                parsed_json=parsed,
                parse_success=True,
            )
        except (json.JSONDecodeError, TypeError):
            return ExtractResult(raw_response=raw)
