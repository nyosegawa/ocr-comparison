"""Claude (Anthropic) OCR adapter."""

from __future__ import annotations

import os

from PIL import Image

from .base import OCR_PROMPT_JA, OCRModel


class ClaudeOCR(OCRModel):
    name = "claude-4.6-opus"
    category = "api"
    weights_url = None
    license = None

    _UNSET = object()

    def __init__(
        self,
        model_id: str = "claude-opus-4-6",
        name: str | None = None,
        *,
        thinking: dict | None = None,
        output_config: dict | None | object = _UNSET,
        max_tokens: int = 65536,
    ):
        self.model_id = model_id
        if name is not None:
            self.name = name
        self.thinking = thinking or {"type": "adaptive"}
        self.output_config = {"effort": "high"} if output_config is self._UNSET else output_config
        self.max_tokens = max_tokens

    def is_available(self) -> bool:
        return bool(os.environ.get("ANTHROPIC_API_KEY"))

    async def recognize(self, image: Image.Image) -> str:
        import anthropic

        client = anthropic.AsyncAnthropic()
        media_type = self.image_media_type(image)
        b64 = self.image_to_base64(image)

        kwargs: dict = {}
        if self.output_config:
            kwargs["output_config"] = self.output_config

        async with client.messages.stream(
            model=self.model_id,
            max_tokens=self.max_tokens,
            thinking=self.thinking,
            **kwargs,
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
                        {"type": "text", "text": OCR_PROMPT_JA},
                    ],
                }
            ],
        ) as stream:
            response = await stream.get_final_message()

        # adaptive thinking may prepend thinking blocks; extract the text block
        for block in response.content:
            if block.type == "text":
                return block.text.strip()
        return ""
