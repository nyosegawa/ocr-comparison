"""Tests for metrics: field comparison, schema compliance, scoring."""

import pytest

from src.metrics.field_compare import (
    compare_array,
    compare_date,
    compare_fields,
    compare_number,
    compare_string,
)
from src.metrics.schema_compliance import check_parse, check_schema_compliance
from src.metrics.scoring import DocumentResult, aggregate_document_results


class TestParsing:
    def test_valid_json(self):
        ok, data = check_parse('{"name": "test"}')
        assert ok is True
        assert data == {"name": "test"}

    def test_invalid_json(self):
        ok, data = check_parse("not json")
        assert ok is False
        assert data is None

    def test_empty_string(self):
        ok, data = check_parse("")
        assert ok is False
        assert data is None


class TestSchemaCompliance:
    def test_valid(self):
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        }
        ok, errors = check_schema_compliance({"name": "test"}, schema)
        assert ok is True
        assert errors == []

    def test_missing_required(self):
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        }
        ok, errors = check_schema_compliance({}, schema)
        assert ok is False
        assert len(errors) > 0


class TestStringComparison:
    def test_identical(self):
        assert compare_string("テスト", "テスト") == 1.0

    def test_empty_both(self):
        assert compare_string("", "") == 1.0

    def test_one_empty(self):
        assert compare_string("テスト", "") == 0.0

    def test_similar(self):
        score = compare_string("テスト株式会社", "テスト株式會社")
        assert 0.5 < score < 1.0

    def test_nfkc_normalization(self):
        # Fullwidth vs halfwidth
        score = compare_string("ABC", "ABC")
        assert score == 1.0


class TestNumberComparison:
    def test_exact(self):
        assert compare_number(10000, 10000) == 1.0

    def test_close(self):
        score = compare_number(10000, 10100)
        assert 0.9 < score < 1.0

    def test_zero_gt(self):
        score = compare_number(0, 0)
        assert score == 1.0

    def test_large_diff(self):
        score = compare_number(100, 0)
        assert score == 0.0


class TestDateComparison:
    def test_same_date(self):
        assert compare_date("2026-03-17", "2026-03-17") == 1.0

    def test_different_format(self):
        assert compare_date("2026-03-17", "2026/03/17") == 1.0

    def test_japanese_format(self):
        assert compare_date("2026-03-17", "2026年3月17日") == 1.0

    def test_wareki(self):
        assert compare_date("2026-03-17", "令和8年3月17日") == 1.0

    def test_different_dates(self):
        assert compare_date("2026-03-17", "2026-03-18") == 0.0


class TestArrayComparison:
    def test_empty_both(self):
        assert compare_array([], [], {}) == 1.0

    def test_one_empty(self):
        assert compare_array([{"a": 1}], [], {}) == 0.0

    def test_matching_items(self):
        item_schema = {
            "type": "object",
            "properties": {
                "description": {"type": "string"},
                "amount": {"type": "number"},
            },
        }
        gt = [{"description": "テスト", "amount": 1000}]
        pred = [{"description": "テスト", "amount": 1000}]
        assert compare_array(gt, pred, item_schema) == 1.0

    def test_partial_match(self):
        item_schema = {
            "type": "object",
            "properties": {
                "description": {"type": "string"},
                "amount": {"type": "number"},
            },
        }
        gt = [
            {"description": "項目A", "amount": 1000},
            {"description": "項目B", "amount": 2000},
        ]
        pred = [
            {"description": "項目A", "amount": 1000},
            {"description": "項目C", "amount": 3000},
        ]
        score = compare_array(gt, pred, item_schema)
        assert 0.3 < score < 0.8  # One exact match, one mismatch


class TestCompareFields:
    def test_all_matching(self):
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "amount": {"type": "number"},
            },
        }
        scores = compare_fields(
            {"name": "テスト", "amount": 100},
            {"name": "テスト", "amount": 100},
            schema,
        )
        assert scores["name"] == 1.0
        assert scores["amount"] == 1.0

    def test_null_handling(self):
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
        }
        # Both null
        scores = compare_fields({"name": None}, {"name": None}, schema)
        assert scores["name"] == 1.0

        # GT has value, pred is null
        scores = compare_fields({"name": "test"}, {"name": None}, schema)
        assert scores["name"] == 0.0


class TestAggregation:
    def test_empty(self):
        result = aggregate_document_results("model", [])
        assert result.mean_field_accuracy == 0.0

    def test_single_result(self):
        dr = DocumentResult(
            document_id="doc1",
            document_type="invoice",
            parse_success=True,
            schema_valid=True,
            field_scores={"name": 1.0, "amount": 0.8},
            mean_field_accuracy=0.9,
        )
        result = aggregate_document_results("model", [dr])
        assert result.mean_field_accuracy == 0.9
        assert result.parse_success_rate == 1.0
        assert result.schema_compliance_rate == 1.0
        assert "invoice" in result.per_type
        assert "name" in result.per_field

    def test_mixed_results(self):
        results = [
            DocumentResult(
                document_id="doc1",
                document_type="invoice",
                parse_success=True,
                schema_valid=True,
                field_scores={"name": 1.0},
                mean_field_accuracy=1.0,
            ),
            DocumentResult(
                document_id="doc2",
                document_type="receipt",
                parse_success=False,
                schema_valid=False,
                mean_field_accuracy=0.0,
            ),
        ]
        result = aggregate_document_results("model", results)
        assert result.parse_success_rate == 0.5
        assert result.schema_compliance_rate == 0.5
        # Only valid results count for accuracy
        assert result.mean_field_accuracy == 1.0
