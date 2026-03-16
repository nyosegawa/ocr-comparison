"""Azure AI Vision OCR adapter (Read API)."""

from __future__ import annotations

import asyncio
import os

from PIL import Image

from .base import OCRModel


class AzureVisionOCR(OCRModel):
    name = "azure-ai-vision"
    category = "api"
    weights_url = None
    license = None

    def is_available(self) -> bool:
        return bool(
            os.environ.get("AZURE_VISION_ENDPOINT")
            and os.environ.get("AZURE_VISION_KEY")
        )

    async def recognize(self, image: Image.Image) -> str:
        from azure.ai.vision.imageanalysis import ImageAnalysisClient
        from azure.ai.vision.imageanalysis.models import VisualFeatures
        from azure.core.credentials import AzureKeyCredential

        client = ImageAnalysisClient(
            endpoint=os.environ["AZURE_VISION_ENDPOINT"],
            credential=AzureKeyCredential(os.environ["AZURE_VISION_KEY"]),
        )
        img_bytes = self.image_to_bytes(image)

        result = await asyncio.to_thread(
            client.analyze,
            image_data=img_bytes,
            visual_features=[VisualFeatures.READ],
        )

        lines = []
        if result.read and result.read.blocks:
            for block in result.read.blocks:
                for line in block.lines:
                    lines.append(line.text)
        return "\n".join(lines)
