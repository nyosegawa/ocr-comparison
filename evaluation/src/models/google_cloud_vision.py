"""Google Cloud Vision OCR adapter."""

from __future__ import annotations

import os

from PIL import Image

from .base import OCRModel


class GoogleCloudVisionOCR(OCRModel):
    name = "google-cloud-vision"
    category = "api"
    weights_url = None
    license = None

    def is_available(self) -> bool:
        return bool(os.environ.get("GOOGLE_CLOUD_VISION_API_KEY"))

    async def recognize(self, image: Image.Image) -> str:
        import asyncio

        from google.cloud.vision_v1 import ImageAnnotatorClient
        from google.cloud.vision_v1 import types as vision_types

        client = ImageAnnotatorClient(
            client_options={"api_key": os.environ["GOOGLE_CLOUD_VISION_API_KEY"]},
        )
        img_bytes = self.image_to_bytes(image)

        vision_image = vision_types.Image(content=img_bytes)
        response = await asyncio.to_thread(client.document_text_detection, image=vision_image)

        full_text = response.full_text_annotation.text
        return full_text.strip() if full_text else ""
