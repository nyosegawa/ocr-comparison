"""Generic Modal runner for GPU-based OCR models."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

from .base import OCRModel

MODAL_SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "modal_scripts"


class ModalOCRModel(OCRModel):
    """OCR model that runs on Modal GPU."""

    name: str
    category = "modal"
    script_name: str  # e.g., "hunyuan_ocr.py"
    gpu: str = "T4"

    def is_available(self) -> bool:
        """Check if Modal CLI is available and authenticated."""
        try:
            result = subprocess.run(
                ["modal", "token", "info"],
                capture_output=True,
                timeout=10,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    async def recognize(self, image: Image.Image) -> str:
        """Run OCR via Modal. This method processes a single image."""
        results = await self.recognize_batch([image])
        return results[0] if results else ""

    async def recognize_batch(self, images: list[Image.Image]) -> list[str]:
        """Run OCR on a batch of images via Modal."""
        images_b64 = [self.image_to_base64(img) for img in images]

        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "input.json"
            output_path = Path(tmpdir) / "output.json"

            with open(input_path, "w") as f:
                json.dump({"images": images_b64}, f)

            script_path = MODAL_SCRIPTS_DIR / self.script_name

            result = subprocess.run(
                [
                    "modal", "run", str(script_path),
                    "--input", str(input_path),
                    "--output", str(output_path),
                ],
                capture_output=True,
                text=True,
                timeout=1800,
            )

            if result.returncode != 0:
                raise RuntimeError(
                    f"Modal run failed for {self.name}:\n"
                    f"stdout: {result.stdout}\n"
                    f"stderr: {result.stderr}"
                )

            with open(output_path) as f:
                data = json.load(f)

            return data.get("results", [])


class HunyuanOCRModal(ModalOCRModel):
    name = "hunyuan-ocr"
    script_name = "hunyuan_ocr.py"
    gpu = "L4"
    weights_url = "https://huggingface.co/tencent/HunyuanOCR"
    license = "Apache-2.0"


class DeepSeekOCRModal(ModalOCRModel):
    name = "deepseek-ocr"
    script_name = "deepseek_ocr.py"
    gpu = "L4"
    weights_url = "https://huggingface.co/deepseek-ai/DeepSeek-OCR"
    license = "MIT"


class ChandraOCRModal(ModalOCRModel):
    name = "chandra"
    script_name = "chandra_ocr.py"
    gpu = "A100-40GB"
    weights_url = "https://pypi.org/project/chandra-ocr/"
    license = "Apache-2.0"


class NanonetsOCRModal(ModalOCRModel):
    name = "nanonets-ocr-s"
    script_name = "nanonets_ocr.py"
    gpu = "L4"
    weights_url = "https://huggingface.co/nanonets/Nanonets-OCR-s"
    license = "Apache-2.0"


class OlmOCRModal(ModalOCRModel):
    name = "olmocr-2"
    script_name = "olmocr.py"
    gpu = "L4"
    weights_url = "https://huggingface.co/allenai/olmOCR-2-7B-1025-FP8"
    license = "Apache-2.0"


class GOTOCRModal(ModalOCRModel):
    name = "got-ocr-2.0"
    script_name = "got_ocr.py"
    gpu = "T4"
    weights_url = "https://huggingface.co/stepfun-ai/GOT-OCR2_0"
    license = "Apache-2.0"


class PaddleOCRModal(ModalOCRModel):
    name = "paddleocr"
    script_name = "paddleocr_run.py"
    gpu = "T4"
    weights_url = "https://github.com/PaddlePaddle/PaddleOCR"
    license = "Apache-2.0"


class YomiTokuModal(ModalOCRModel):
    name = "yomitoku"
    script_name = "yomitoku_run.py"
    gpu = "T4"
    weights_url = "https://github.com/kotaro-kinoshita/yomitoku"
    license = "CC-BY-NC-SA-4.0"


class NDLOCRLiteModal(ModalOCRModel):
    name = "ndlocr-lite"
    script_name = "ndlocr_lite.py"
    gpu = ""  # CPU-only (ONNX Runtime)
    weights_url = "https://github.com/ndl-lab/ndlocr-lite"
    license = "CC-BY-4.0"


class NDLOCRv2Modal(ModalOCRModel):
    name = "ndlocr-v2"
    script_name = "ndlocr.py"
    gpu = "A10G"
    weights_url = "https://github.com/ndl-lab/ndlocr_cli"
    license = "CC-BY-4.0"


class GLMOCRModal(ModalOCRModel):
    name = "glm-ocr"
    script_name = "glm_ocr.py"
    gpu = "T4"
    weights_url = "https://huggingface.co/zai-org/GLM-OCR"
    license = "MIT"


class SarashinaOCRModal(ModalOCRModel):
    name = "sarashina-2.2-ocr"
    script_name = "sarashina_ocr.py"
    gpu = "L4"
    weights_url = "https://huggingface.co/sbintuitions/sarashina2.2-ocr"
    license = "MIT"


class NemotronOCRModal(ModalOCRModel):
    name = "nemotron-ocr-v2"
    script_name = "nemotron_ocr_run.py"
    gpu = "L4"
    weights_url = "https://huggingface.co/nvidia/nemotron-ocr-v2"
    license = "NVIDIA Open Model License"
