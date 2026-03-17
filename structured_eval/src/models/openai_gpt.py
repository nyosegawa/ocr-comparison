"""OpenAI GPT structured output adapter."""

from __future__ import annotations

import json
import os

from PIL import Image

from .base import EXTRACTION_PROMPT_JA, ExtractResult, StructuredOCRModel


class GPTStructured(StructuredOCRModel):
    name = "gpt-5.4"
    category = "api"

    def __init__(self, model_id: str = "gpt-5.4", name: str | None = None):
        self.model_id = model_id
        if name is not None:
            self.name = name

    def is_available(self) -> bool:
        return bool(os.environ.get("OPENAI_API_KEY"))

    async def extract(
        self, image: Image.Image, schema: dict, document_type: str
    ) -> ExtractResult:
        from openai import AsyncOpenAI

        client = AsyncOpenAI()
        b64 = self.image_to_base64(image)

        from ..schemas.base import get_schema
        schema_cls = get_schema(document_type)
        prompt = EXTRACTION_PROMPT_JA.format(
            document_type_ja=schema_cls.document_type_ja()
        )

        try:
            response = await client.chat.completions.create(
                model=self.model_id,
                max_completion_tokens=8192,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": f"extract_{document_type}",
                        "strict": True,
                        "schema": schema,
                    },
                },
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{b64}",
                                    "detail": "high",
                                },
                            },
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
            )
        except Exception as e:
            return ExtractResult(error=f"{type(e).__name__}: {e}")

        content = response.choices[0].message.content or ""
        try:
            parsed = json.loads(content)
            return ExtractResult(
                raw_response=content,
                parsed_json=parsed,
                parse_success=True,
            )
        except (json.JSONDecodeError, TypeError):
            return ExtractResult(raw_response=content)
