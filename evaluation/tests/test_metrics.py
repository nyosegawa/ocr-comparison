"""Tests for src/metrics.py — normalization, NLS, BoC-F1, NED/CER, aggregation."""

from __future__ import annotations

import pytest

from src.metrics import (
    EvalResult,
    _nls,
    _partial_nls,
    _try_merge_adjacent,
    aggregate_results,
    bag_of_chars,
    evaluate_image,
    full_text_ned,
    normalize_for_comparison,
    normalize_text,
    region_match_nls,
    split_into_segments,
    strip_markdown,
    strip_vlm_noise,
    strip_whitespace,
)


# ---------------------------------------------------------------------------
# Text normalization
# ---------------------------------------------------------------------------

class TestNormalizeText:
    def test_nfkc_normalization(self):
        # Full-width digits → half-width
        assert normalize_text("１２３") == "123"

    def test_strips_whitespace(self):
        assert normalize_text("  hello  ") == "hello"

    def test_empty_string(self):
        assert normalize_text("") == ""


class TestStripMarkdown:
    def test_removes_headers(self):
        assert strip_markdown("## Title\ncontent").strip() == "Title\ncontent"

    def test_removes_bold(self):
        assert strip_markdown("**bold**") == "bold"

    def test_removes_italic_underscore(self):
        assert strip_markdown("__text__") == "text"

    def test_removes_italic_star(self):
        assert strip_markdown("*italic*") == "italic"

    def test_removes_link_keeps_text(self):
        assert strip_markdown("[link](http://example.com)") == "link"

    def test_removes_image_reference(self):
        assert strip_markdown("![alt](img.png)").strip() == ""

    def test_removes_inline_code(self):
        assert strip_markdown("`code`") == "code"

    def test_removes_code_fences(self):
        result = strip_markdown("```python\nprint('hello')\n```")
        assert "```" not in result

    def test_removes_list_markers(self):
        result = strip_markdown("- item1\n* item2\n+ item3")
        lines = [l.strip() for l in result.strip().splitlines()]
        assert lines == ["item1", "item2", "item3"]

    def test_removes_numbered_list(self):
        result = strip_markdown("1. first\n2. second")
        lines = [l.strip() for l in result.strip().splitlines()]
        assert lines == ["first", "second"]

    def test_removes_html_tags(self):
        assert strip_markdown("<br>hello</br>") == "hello"


class TestStripVlmNoise:
    def test_removes_bullet_symbols(self):
        assert strip_vlm_noise("・テスト") == "テスト"

    def test_removes_trailing_period(self):
        assert strip_vlm_noise("テスト。") == "テスト"

    def test_removes_vlm_meta_descriptions(self):
        result = strip_vlm_noise("テキスト（丸で囲まれている）余り")
        assert "囲" not in result

    def test_preserves_normal_text(self):
        assert strip_vlm_noise("普通のテキスト") == "普通のテキスト"


class TestNormalizeForComparison:
    def test_full_pipeline(self):
        text = "## **Title**\n・テスト。"
        result = normalize_for_comparison(text)
        assert "##" not in result
        assert "**" not in result
        assert "・" not in result


class TestStripWhitespace:
    def test_removes_whitespace(self):
        assert strip_whitespace("a b\tc\nd") == "abcd"

    def test_removes_punctuation(self):
        assert strip_whitespace("テスト。テスト、") == "テストテスト"

    def test_removes_various_punctuation(self):
        assert strip_whitespace("hello!world?") == "helloworld"


# ---------------------------------------------------------------------------
# NLS helpers
# ---------------------------------------------------------------------------

class TestNls:
    def test_identical_strings(self):
        assert _nls("hello", "hello") == 1.0

    def test_completely_different(self):
        assert _nls("abc", "xyz") < 0.5

    def test_both_empty(self):
        assert _nls("", "") == 1.0

    def test_one_empty(self):
        assert _nls("hello", "") == 0.0
        assert _nls("", "hello") == 0.0

    def test_similar_strings(self):
        nls = _nls("hello", "helo")
        assert 0.7 < nls < 1.0


class TestPartialNls:
    def test_exact_match(self):
        assert _partial_nls("hello", "hello") == 1.0

    def test_substring_match(self):
        # "abc" is a substring of "xyzabcdef"
        nls = _partial_nls("abc", "xyzabcdef")
        assert nls == 1.0

    def test_no_match(self):
        nls = _partial_nls("abc", "xyz")
        assert nls < 0.5


# ---------------------------------------------------------------------------
# Segment helpers
# ---------------------------------------------------------------------------

class TestSplitIntoSegments:
    def test_basic(self):
        assert split_into_segments("a\nb\nc") == ["a", "b", "c"]

    def test_empty_lines_removed(self):
        assert split_into_segments("a\n\n\nb") == ["a", "b"]

    def test_whitespace_stripped(self):
        assert split_into_segments("  a  \n  b  ") == ["a", "b"]

    def test_empty_string(self):
        assert split_into_segments("") == []


class TestTryMergeAdjacent:
    def test_no_merge_single(self):
        result = _try_merge_adjacent(["a"])
        assert result == ["a"]

    def test_merge_two(self):
        result = _try_merge_adjacent(["a", "b"])
        assert "a" in result
        assert "b" in result
        assert "ab" in result

    def test_merge_three(self):
        result = _try_merge_adjacent(["a", "b", "c"])
        assert "ab" in result
        assert "bc" in result
        assert "abc" in result

    def test_max_merge_limit(self):
        result = _try_merge_adjacent(["a", "b", "c", "d"], max_merge=2)
        assert "ab" in result
        assert "abc" not in result


# ---------------------------------------------------------------------------
# Metric 1: Region Match NLS
# ---------------------------------------------------------------------------

class TestRegionMatchNls:
    def test_perfect_match(self):
        gt = ["hello", "world"]
        pred = "hello\nworld"
        result = region_match_nls(gt, pred)
        assert result["hungarian_nls"] > 0.95
        assert result["unmatched"] == 0

    def test_no_prediction(self):
        result = region_match_nls(["hello"], "")
        assert result["hungarian_nls"] == 0.0
        assert result["unmatched"] == 1

    def test_empty_gt(self):
        result = region_match_nls([], "some text")
        assert result["hungarian_nls"] == 1.0

    def test_merged_lines(self):
        """VLM merges two GT regions into one line."""
        gt = ["東京都", "渋谷区"]
        pred = "東京都渋谷区"
        result = region_match_nls(gt, pred)
        assert result["hungarian_nls"] > 0.8

    def test_split_lines(self):
        """VLM splits one GT region across two lines."""
        gt = ["東京都渋谷区"]
        pred = "東京都\n渋谷区"
        result = region_match_nls(gt, pred)
        assert result["hungarian_nls"] > 0.8


# ---------------------------------------------------------------------------
# Metric 2: Bag-of-Characters F1
# ---------------------------------------------------------------------------

class TestBagOfChars:
    def test_perfect_match(self):
        result = bag_of_chars("hello", "hello")
        assert result["boc_f1"] == 1.0
        assert result["boc_precision"] == 1.0
        assert result["boc_recall"] == 1.0

    def test_partial_match(self):
        result = bag_of_chars("abc", "abx")
        assert 0.0 < result["boc_f1"] < 1.0

    def test_empty_pred(self):
        result = bag_of_chars("hello", "")
        assert result["boc_f1"] == 0.0
        assert result["boc_recall"] == 0.0

    def test_empty_gt(self):
        result = bag_of_chars("", "hello")
        assert result["boc_recall"] == 0.0

    def test_order_independent(self):
        result1 = bag_of_chars("abc", "cba")
        assert result1["boc_f1"] == 1.0

    def test_japanese_text(self):
        result = bag_of_chars("東京都渋谷区", "東京都渋谷区")
        assert result["boc_f1"] == 1.0


# ---------------------------------------------------------------------------
# Metric 3: Full-text NED/CER
# ---------------------------------------------------------------------------

class TestFullTextNed:
    def test_identical(self):
        result = full_text_ned("hello", "hello")
        assert result["ned"] == 1.0
        assert result["cer"] == 0.0
        assert result["edit_distance"] == 0

    def test_completely_different(self):
        result = full_text_ned("abc", "xyz")
        assert result["ned"] < 0.5
        assert result["cer"] > 0.5

    def test_both_empty(self):
        result = full_text_ned("", "")
        assert result["ned"] == 1.0
        assert result["cer"] == 0.0

    def test_gt_empty_pred_nonempty(self):
        result = full_text_ned("", "hello")
        assert result["cer"] == 1.0

    def test_one_char_difference(self):
        result = full_text_ned("hello", "helo")
        assert result["ned"] > 0.7
        assert result["edit_distance"] == 1
        assert result["gt_length"] == 5


# ---------------------------------------------------------------------------
# Combined evaluation
# ---------------------------------------------------------------------------

class TestEvaluateImage:
    def test_returns_eval_result(self):
        result = evaluate_image(["hello"], "hello")
        assert isinstance(result, EvalResult)
        assert result.hungarian_nls > 0.9
        assert result.boc_f1 > 0.9
        assert result.ned > 0.9

    def test_empty_prediction(self):
        result = evaluate_image(["hello"], "")
        assert result.hungarian_nls == 0.0
        assert result.boc_f1 == 0.0


class TestAggregateResults:
    def test_empty(self):
        result = aggregate_results([])
        assert result["n_images"] == 0

    def test_single_result(self):
        er = EvalResult(
            hungarian_nls=0.9,
            hungarian_matched=1,
            hungarian_unmatched=0,
            boc_precision=0.95,
            boc_recall=0.85,
            boc_f1=0.9,
            ned=0.88,
            cer=0.05,
            edit_distance=5,
            gt_length=100,
        )
        result = aggregate_results([er])
        assert result["n_images"] == 1
        assert result["hungarian_nls"] == 0.9
        assert result["boc_f1"] == 0.9

    def test_weighted_cer(self):
        """CER should be weighted by GT length."""
        r1 = EvalResult(
            hungarian_nls=0.9, hungarian_matched=1, hungarian_unmatched=0,
            boc_precision=0.9, boc_recall=0.9, boc_f1=0.9,
            ned=0.9, cer=0.1,
            edit_distance=10, gt_length=100,
        )
        r2 = EvalResult(
            hungarian_nls=0.9, hungarian_matched=1, hungarian_unmatched=0,
            boc_precision=0.9, boc_recall=0.9, boc_f1=0.9,
            ned=0.9, cer=0.5,
            edit_distance=5, gt_length=10,
        )
        result = aggregate_results([r1, r2])
        # Weighted CER: (10 + 5) / (100 + 10) ≈ 0.136
        expected_cer = 15 / 110
        assert abs(result["cer"] - expected_cer) < 0.001
