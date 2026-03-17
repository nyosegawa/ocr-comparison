"""Model registry for structured output evaluation."""

from __future__ import annotations

from .base import StructuredOCRModel
from .claude import ClaudeStructured
from .gemini import GeminiStructured
from .openai_gpt import GPTStructured


def get_all_models() -> list[StructuredOCRModel]:
    """Return all registered structured OCR models."""
    return [
        ClaudeStructured(),
        ClaudeStructured(model_id="claude-sonnet-4-5-20250929", name="claude-4.5-sonnet"),
        GeminiStructured(),
        GeminiStructured(model_id="gemini-3-flash-preview", name="gemini-3-flash-preview"),
        GPTStructured(),
    ]


def get_available_models() -> list[StructuredOCRModel]:
    """Return only models that are currently available."""
    return [m for m in get_all_models() if m.is_available()]


def get_models_by_name(names: list[str]) -> list[StructuredOCRModel]:
    """Return models matching the given names."""
    all_models = {m.name: m for m in get_all_models()}
    return [all_models[n] for n in names if n in all_models]
