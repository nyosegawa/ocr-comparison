"""Tests for src/evaluate.py — leaderboard, rescore, helpers."""

from __future__ import annotations

import json
import tempfile
from dataclasses import asdict
from pathlib import Path

import pytest

from src.evaluate import _indent, build_leaderboard
from src.metrics import EvalResult, evaluate_image


class TestBuildLeaderboard:
    def test_sorts_by_nls_descending(self):
        results = [
            {
                "model": "model_a",
                "category": "api",
                "aggregated": {"hungarian_nls": 0.7, "boc_f1": 0.8, "cer": 0.1, "ned": 0.85, "n_images": 5},
            },
            {
                "model": "model_b",
                "category": "modal",
                "aggregated": {"hungarian_nls": 0.9, "boc_f1": 0.6, "cer": 0.2, "ned": 0.75, "n_images": 5},
            },
        ]
        lb = build_leaderboard(results)
        assert lb[0]["model"] == "model_b"  # higher NLS
        assert lb[1]["model"] == "model_a"

    def test_empty_results(self):
        assert build_leaderboard([]) == []

    def test_leaderboard_fields(self):
        results = [
            {
                "model": "test",
                "category": "api",
                "aggregated": {"hungarian_nls": 0.8, "boc_f1": 0.7, "cer": 0.1, "ned": 0.9, "n_images": 3},
            },
        ]
        lb = build_leaderboard(results)
        entry = lb[0]
        assert "model" in entry
        assert "category" in entry
        assert "hungarian_nls" in entry
        assert "boc_f1" in entry
        assert "cer" in entry
        assert "ned" in entry


class TestIndent:
    def test_single_line(self):
        assert _indent("hello", "  ") == "  hello"

    def test_multi_line(self):
        result = _indent("a\nb\nc", "> ")
        assert result == "> a\n> b\n> c"

    def test_empty_string(self):
        # splitlines() on empty string returns [], so join produces ""
        assert _indent("", "  ") == ""


class TestRescoreIntegration:
    """Test rescore by simulating the data flow without calling rescore_results directly."""

    def test_rescore_recomputes_metrics(self):
        """Verify that evaluate_image produces consistent results for rescoring."""
        gt_regions = ["東京都", "渋谷区"]
        pred = "東京都\n渋谷区"

        result1 = evaluate_image(gt_regions, pred)
        result2 = evaluate_image(gt_regions, pred)

        assert asdict(result1) == asdict(result2)
