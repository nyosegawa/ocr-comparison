"""Mistral OCR adapter."""

from __future__ import annotations

import asyncio
import os

from PIL import Image

from .base import OCRModel


class MistralOCR(OCRModel):
    name = "mistral-ocr-latest"
    category = "api"
    weights_url = None
    license = None

    def __init__(self, model_id: str = "mistral-ocr-latest"):
        self.model_id = model_id

    def is_available(self) -> bool:
        return bool(os.environ.get("MISTRAL_API_KEY"))

    async def recognize(self, image: Image.Image) -> str:
        from mistralai.client import Mistral

        client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])
        b64 = self.image_to_base64(image)
        media_type = self.image_media_type(image)

        last_err = None
        for attempt in range(5):
            try:
                response = await client.ocr.process_async(
                    model=self.model_id,
                    document={
                        "type": "image_url",
                        "image_url": f"data:{media_type};base64,{b64}",
                    },
                )
                break
            except Exception as e:
                last_err = e
                if attempt < 4:
                    await asyncio.sleep(2 ** attempt)
        else:
            raise last_err  # type: ignore[misc]

        parts = []
        for page in response.pages:
            if page.markdown:
                parts.append(page.markdown)
        return "\n".join(parts).strip()
