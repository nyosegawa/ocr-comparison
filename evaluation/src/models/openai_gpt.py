"""GPT (OpenAI) OCR adapter."""

from __future__ import annotations

import os

from PIL import Image

from .base import OCR_PROMPT_JA, OCRModel


class GPTOCR(OCRModel):
    name = "gpt-5.4-thinking"
    category = "api"
    weights_url = None
    license = None

    def __init__(self, model_id: str = "gpt-5.4", reasoning_effort: str = "high", name: str | None = None):
        self.model_id = model_id
        self.reasoning_effort = reasoning_effort
        if name is not None:
            self.name = name
        elif model_id != "gpt-5.4":
            self.name = f"{model_id}-thinking" if reasoning_effort else model_id

    def is_available(self) -> bool:
        return bool(os.environ.get("OPENAI_API_KEY"))

    async def recognize(self, image: Image.Image) -> str:
        from openai import AsyncOpenAI

        client = AsyncOpenAI()
        b64 = self.image_to_base64(image)

        response = await client.chat.completions.create(
            model=self.model_id,
            max_completion_tokens=65536,
            reasoning_effort=self.reasoning_effort,
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
                        {"type": "text", "text": OCR_PROMPT_JA},
                    ],
                }
            ],
        )

        content = response.choices[0].message.content
        return content.strip() if content else ""
