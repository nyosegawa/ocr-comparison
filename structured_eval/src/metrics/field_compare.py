"""Level 3 metrics: field-level comparison."""

from __future__ import annotations

import re
import unicodedata
from datetime import date, datetime
from typing import Any

from rapidfuzz.distance import Levenshtein
from scipy.optimize import linear_sum_assignment


def compare_fields(gt: dict, pred: dict, schema: dict) -> dict[str, float]:
    """Compare all fields between ground truth and prediction.

    Returns a dict of {field_name: score (0.0-1.0)}.
    """
    properties = schema.get("properties", {})
    scores: dict[str, float] = {}

    for field_name, field_schema in properties.items():
        gt_val = gt.get(field_name)
        pred_val = pred.get(field_name)
        field_type = _infer_field_type(field_schema)

        if field_type == "array":
            item_schema = field_schema.get("items", {})
            arr_score = compare_array(
                gt_val if gt_val is not None else [],
                pred_val if pred_val is not None else [],
                item_schema,
            )
            scores[field_name] = arr_score
        else:
            scores[field_name] = compare_single(gt_val, pred_val, field_type)

    return scores


def compare_single(gt_val: Any, pred_val: Any, field_type: str) -> float:
    """Compare a single field value."""
    # Null handling
    if gt_val is None and pred_val is None:
        return 1.0
    if gt_val is None or pred_val is None:
        return 0.0

    if field_type == "number":
        return compare_number(gt_val, pred_val)
    elif field_type == "date":
        return compare_date(str(gt_val), str(pred_val))
    else:  # string
        return compare_string(str(gt_val), str(pred_val))


def compare_string(gt: str, pred: str) -> float:
    """Compare strings using Normalized Levenshtein Similarity after NFKC normalization."""
    gt_n = _normalize(gt)
    pred_n = _normalize(pred)
    if not gt_n and not pred_n:
        return 1.0
    if not gt_n or not pred_n:
        return 0.0
    return 1.0 - Levenshtein.normalized_distance(gt_n, pred_n)


def compare_number(gt: Any, pred: Any) -> float:
    """Compare numeric values."""
    try:
        gt_f = float(gt)
        pred_f = float(pred)
    except (ValueError, TypeError):
        # Fall back to string comparison if not parseable
        return compare_string(str(gt), str(pred))

    if gt_f == pred_f:
        return 1.0
    denom = max(abs(gt_f), 1.0)
    return max(0.0, 1.0 - abs(pred_f - gt_f) / denom)


def compare_date(gt: str, pred: str) -> float:
    """Compare date strings.

    Parses various formats, then exact match = 1.0, mismatch = 0.0.
    Falls back to string NLS if parsing fails.
    """
    gt_date = _parse_date(gt)
    pred_date = _parse_date(pred)

    if gt_date is not None and pred_date is not None:
        return 1.0 if gt_date == pred_date else 0.0

    # Fallback to string comparison
    return compare_string(gt, pred)


def compare_array(
    gt_items: list, pred_items: list, item_schema: dict
) -> float:
    """Compare arrays using Hungarian matching for optimal assignment."""
    if not gt_items and not pred_items:
        return 1.0
    if not gt_items or not pred_items:
        return 0.0

    n_gt = len(gt_items)
    n_pred = len(pred_items)
    size = max(n_gt, n_pred)

    # Build cost matrix (1 - similarity for minimization)
    import numpy as np

    cost = np.ones((size, size))
    for i in range(n_gt):
        for j in range(n_pred):
            if isinstance(gt_items[i], dict) and isinstance(pred_items[j], dict):
                item_scores = compare_fields(gt_items[i], pred_items[j], item_schema)
                sim = sum(item_scores.values()) / len(item_scores) if item_scores else 0.0
            else:
                sim = compare_single(gt_items[i], pred_items[j], "string")
            cost[i, j] = 1.0 - sim

    row_ind, col_ind = linear_sum_assignment(cost)

    total_sim = 0.0
    for r, c in zip(row_ind, col_ind):
        total_sim += 1.0 - cost[r, c]

    return total_sim / size


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    """NFKC normalize, strip whitespace."""
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\s+", "", text)
    return text


_DATE_FORMATS = [
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%Y年%m月%d日",
    "%Y.%m.%d",
]

_WAREKI_MAP = {
    "令和": 2018,
    "平成": 1988,
    "昭和": 1925,
    "大正": 1911,
    "明治": 1867,
}

_WAREKI_RE = re.compile(
    r"(令和|平成|昭和|大正|明治)\s*(\d{1,2})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日"
)


def _parse_date(text: str) -> date | None:
    """Try to parse a date string in various Japanese/ISO formats."""
    text = text.strip()

    # Try wareki
    m = _WAREKI_RE.search(text)
    if m:
        era, year_s, month_s, day_s = m.groups()
        year = _WAREKI_MAP[era] + int(year_s)
        try:
            return date(year, int(month_s), int(day_s))
        except ValueError:
            pass

    # Try standard formats
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue

    return None


def _infer_field_type(field_schema: dict) -> str:
    """Infer the logical field type from a JSON Schema property."""
    schema_type = field_schema.get("type", "")

    # Handle anyOf (optional fields)
    if "anyOf" in field_schema:
        non_null = [s for s in field_schema["anyOf"] if s.get("type") != "null"]
        if non_null:
            return _infer_field_type(non_null[0])

    # Handle type: ["string", "null"] array format
    if isinstance(schema_type, list):
        non_null = [t for t in schema_type if t != "null"]
        if non_null:
            schema_type = non_null[0]

    if schema_type == "array":
        return "array"
    if schema_type in ("number", "integer"):
        return "number"
    if schema_type == "string":
        desc = field_schema.get("description", "")
        if "日" in desc and ("YYYY" in desc or "年" in desc):
            return "date"
        return "string"

    return "string"
