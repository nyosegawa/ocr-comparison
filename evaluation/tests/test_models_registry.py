"""Tests for src/models/registry.py — model registration and lookup."""

from __future__ import annotations

from src.models.base import OCRModel
from src.models.registry import get_all_models, get_models_by_name


class TestGetAllModels:
    def test_returns_list(self):
        models = get_all_models()
        assert isinstance(models, list)
        assert len(models) > 0

    def test_all_are_ocr_models(self):
        for m in get_all_models():
            assert isinstance(m, OCRModel)

    def test_unique_names(self):
        names = [m.name for m in get_all_models()]
        assert len(names) == len(set(names)), f"Duplicate names: {names}"

    def test_has_api_and_modal_categories(self):
        categories = {m.category for m in get_all_models()}
        assert "api" in categories
        assert "modal" in categories

    def test_known_models_present(self):
        names = {m.name for m in get_all_models()}
        for expected in [
            "hunyuan-ocr",
            "deepseek-ocr",
            "paddleocr",
            "yomitoku",
        ]:
            assert expected in names, f"{expected} not found in registry"


class TestGetModelsByName:
    def test_finds_existing_model(self):
        models = get_models_by_name(["hunyuan-ocr"])
        assert len(models) == 1
        assert models[0].name == "hunyuan-ocr"

    def test_ignores_unknown_name(self):
        models = get_models_by_name(["nonexistent-model"])
        assert len(models) == 0

    def test_multiple_names(self):
        models = get_models_by_name(["hunyuan-ocr", "paddleocr"])
        assert len(models) == 2

    def test_empty_list(self):
        models = get_models_by_name([])
        assert len(models) == 0
