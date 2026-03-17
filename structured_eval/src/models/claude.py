"""Claude structured output adapter.

Uses tool_use because Claude's json_schema mode has a limit of 16
union-typed (nullable) parameters, which our document schemas exceed.
"""

from __future__ import annotations

import json
import os

from PIL import Image

from .base import EXTRACTION_PROMPT_JA, ExtractResult, StructuredOCRModel


class ClaudeStructured(StructuredOCRModel):
    name = "claude-4.6-opus"
    category = "api"

    def __init__(self, model_id: str = "claude-opus-4-6", name: str | None = None):
        self.model_id = model_id
        if name is not None:
            self.name = name

    def is_available(self) -> bool:
        return bool(os.environ.get("ANTHROPIC_API_KEY"))

    async def extract(
        self, image: Image.Image, schema: dict, document_type: str
    ) -> ExtractResult:
        import anthropic

        client = anthropic.AsyncAnthropic()
        media_type = self.image_media_type(image)
        b64 = self.image_to_base64(image)

        tool_name = f"extract_{document_type}"
        tool = {
            "name": tool_name,
            "description": f"Extract structured data from a {document_type} image.",
            "input_schema": schema,
        }

        from ..schemas.base import get_schema
        schema_cls = get_schema(document_type)
        prompt = EXTRACTION_PROMPT_JA.format(
            document_type_ja=schema_cls.document_type_ja()
        )

        try:
            response = await client.messages.create(
                model=self.model_id,
                max_tokens=8192,
                tools=[tool],
                tool_choice={"type": "tool", "name": tool_name},
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": b64,
                                },
                            },
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
            )
        except Exception as e:
            return ExtractResult(error=f"{type(e).__name__}: {e}")

        for block in response.content:
            if block.type == "tool_use":
                raw = json.dumps(block.input, ensure_ascii=False)
                return ExtractResult(
                    raw_response=raw,
                    parsed_json=block.input,
                    parse_success=True,
                )

        return ExtractResult(
            raw_response=str(response.content),
            error="No tool_use block in response",
        )
