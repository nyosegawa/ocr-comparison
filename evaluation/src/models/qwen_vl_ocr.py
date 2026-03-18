"""Qwen VL OCR (Alibaba Cloud DashScope) adapter."""

from __future__ import annotations

import os

from PIL import Image

from .base import OCR_PROMPT_JA, OCRModel


class QwenVLOCR(OCRModel):
    name = "qwen-vl-ocr"
    category = "api"
    weights_url = None
    license = None

    def __init__(self, model_id: str = "qwen-vl-ocr"):
        self.model_id = model_id

    def is_available(self) -> bool:
        return bool(os.environ.get("DASHSCOPE_API_KEY"))

    async def recognize(self, image: Image.Image) -> str:
        from openai import AsyncOpenAI

        base_url = os.environ.get(
            "DASHSCOPE_BASE_URL",
            "https://dashscope-us.aliyuncs.com/compatible-mode/v1",
        )
        client = AsyncOpenAI(
            api_key=os.environ["DASHSCOPE_API_KEY"],
            base_url=base_url,
        )
        b64 = self.image_to_base64(image)
        media_type = self.image_media_type(image)

        response = await client.chat.completions.create(
            model=self.model_id,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{b64}",
                            },
                        },
                        {"type": "text", "text": OCR_PROMPT_JA},
                    ],
                }
            ],
        )

        content = response.choices[0].message.content
        return content.strip() if content else ""
