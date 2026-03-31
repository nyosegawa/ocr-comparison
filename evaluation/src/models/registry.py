"""Model registry: all available OCR models."""

from __future__ import annotations

from .azure_vision import AzureVisionOCR
from .base import OCRModel
from .claude import ClaudeOCR
from .gemini import GeminiOCR
from .google_cloud_vision import GoogleCloudVisionOCR
from .modal_runner import (
    ChandraOCRModal,
    DeepSeekOCRModal,
    GLMOCRModal,
    GOTOCRModal,
    HunyuanOCRModal,
    NanonetsOCRModal,
    NDLOCRLiteModal,
    NDLOCRv2Modal,
    OlmOCRModal,
    PaddleOCRModal,
    SarashinaOCRModal,
    YomiTokuModal,
)
from .mistral_ocr import MistralOCR
from .openai_gpt import GPTOCR
from .qwen_vl_ocr import QwenVLOCR


def get_all_models() -> list[OCRModel]:
    """Return all registered OCR models."""
    return [
        # --- API models (direct calls) ---
        ClaudeOCR(),
        ClaudeOCR(
            model_id="claude-sonnet-4-5-20250929",
            name="claude-4.5-sonnet",
            thinking={"type": "enabled", "budget_tokens": 10000},
            output_config=None,
            max_tokens=16000,
        ),
        GeminiOCR(),
        GeminiOCR(model_id="gemini-3-flash-preview"),
        GeminiOCR(model_id="gemini-3.1-flash-lite-preview"),
        GPTOCR(),
        GoogleCloudVisionOCR(),
        AzureVisionOCR(),
        MistralOCR(),
        QwenVLOCR(),
        # --- Modal models (GPU execution) ---
        HunyuanOCRModal(),
        DeepSeekOCRModal(),
        ChandraOCRModal(),
        NanonetsOCRModal(),
        OlmOCRModal(),
        GOTOCRModal(),
        PaddleOCRModal(),
        YomiTokuModal(),
        NDLOCRLiteModal(),
        NDLOCRv2Modal(),
        GLMOCRModal(),
        SarashinaOCRModal(),
    ]


def get_available_models() -> list[OCRModel]:
    """Return only models that are currently available."""
    return [m for m in get_all_models() if m.is_available()]


def get_models_by_name(names: list[str]) -> list[OCRModel]:
    """Return models matching the given names."""
    all_models = {m.name: m for m in get_all_models()}
    result = []
    for name in names:
        if name in all_models:
            result.append(all_models[name])
    return result
