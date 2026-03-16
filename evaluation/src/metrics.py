"""OCR evaluation metrics.

Three-metric strategy:
1. Hungarian Matching NLS (primary) — reading-order independent region matching
2. Bag-of-Characters F1 (secondary) — pure character recognition quality
3. Full-text NED/CER (tertiary) — overall quality including reading order
"""

from __future__ import annotations

import re
import unicodedata
from collections import Counter
from dataclasses import dataclass

from rapidfuzz.distance import Levenshtein


# ---------------------------------------------------------------------------
# Text normalization
# ---------------------------------------------------------------------------

def normalize_text(text: str) -> str:
    """NFKC normalize and strip."""
    text = unicodedata.normalize("NFKC", text)
    text = text.strip()
    return text


def strip_markdown(text: str) -> str:
    """Remove common markdown syntax from VLM output."""
    # Remove headers
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # Remove bold/italic
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"__(.+?)__", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"_(.+?)_", r"\1", text)
    # Remove image references
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)
    # Remove link syntax but keep text
    text = re.sub(r"\[(.+?)\]\(.*?\)", r"\1", text)
    # Remove code fences
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"`(.+?)`", r"\1", text)
    # Remove list markers
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)
    # Remove HTML tags
    text = re.sub(r"</?[a-zA-Z][^>]*>", "", text)
    return text


def strip_vlm_noise(text: str) -> str:
    """Remove decoration characters commonly added by VLMs."""
    # Bullet/list symbols: ・☆○◎●■□▪▶→↓↳►
    text = re.sub(r"[・☆○◎●■□▪▶►↓↳☑☐]", "", text)
    # Trailing punctuation that VLMs add but GT doesn't have: 。.
    text = re.sub(r"[。．]+$", "", text, flags=re.MULTILINE)
    # VLM meta-descriptions in parentheses (e.g., "（丸で囲まれている）", "（取り消し線）")
    text = re.sub(r"[（(][^）)]*(?:囲|線|注|省略|不明|読めない)[^）)]*[）)]", "", text)
    # Emoji
    text = re.sub(
        r"[\U0001F300-\U0001F9FF\U00002600-\U000027BF\U0000FE00-\U0000FE0F]",
        "", text,
    )
    return text


def normalize_for_comparison(text: str) -> str:
    """Full normalization pipeline for text comparison."""
    text = strip_markdown(text)
    text = strip_vlm_noise(text)
    text = normalize_text(text)
    return text


def strip_whitespace(text: str) -> str:
    """Remove all whitespace and punctuation (for bag-of-chars comparison)."""
    # Remove whitespace
    text = re.sub(r"\s+", "", text)
    # Remove punctuation that shouldn't affect character recognition scoring
    text = re.sub(r"[。、．，.,:;!！？?…\-–—~～\u3000]", "", text)
    return text


# ---------------------------------------------------------------------------
# Metric 1: Hungarian Matching NLS (primary)
# ---------------------------------------------------------------------------

def split_into_segments(text: str) -> list[str]:
    """Split text into line segments for matching."""
    lines = text.split("\n")
    segments = [line.strip() for line in lines if line.strip()]
    return segments


def _try_merge_adjacent(
    segments: list[str], max_merge: int = 3
) -> list[str]:
    """Generate merged candidates from adjacent segments.

    Returns original segments plus merged pairs/triples.
    """
    candidates = list(segments)
    for width in range(2, min(max_merge + 1, len(segments) + 1)):
        for start in range(len(segments) - width + 1):
            merged = "".join(segments[start : start + width])
            candidates.append(merged)
    return candidates


def _nls(a: str, b: str) -> float:
    """Normalized Levenshtein Similarity between two strings."""
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return 1.0 - Levenshtein.normalized_distance(a, b)


def _partial_nls(short: str, long: str) -> float:
    """NLS allowing short to match as a substring of long.

    Returns max(standard NLS, best substring NLS).
    """
    standard = _nls(short, long)
    if standard >= 0.8 or len(short) >= len(long):
        return standard

    # Slide short over long, find best match
    best = standard
    slen = len(short)
    for start in range(len(long) - slen + 1):
        sub = long[start : start + slen]
        nls = _nls(short, sub)
        if nls > best:
            best = nls
    return best


def region_match_nls(
    gt_regions: list[str], pred_text: str
) -> dict:
    """Compute per-region best-match NLS.

    For each GT region, find the best-matching pred line/segment using partial
    substring matching. Multiple GT regions may match the same pred line
    (handles VLM merging multiple GT regions into one line).

    Pred candidates include adjacent-merged lines (handles VLM splitting one
    GT region across lines).
    """
    gt_normalized = [strip_whitespace(normalize_for_comparison(r)) for r in gt_regions]
    gt_normalized = [r for r in gt_normalized if r]

    if not gt_normalized:
        return {"hungarian_nls": 1.0, "matched": 0, "unmatched": 0}

    pred_segments = split_into_segments(normalize_for_comparison(pred_text))
    if not pred_segments:
        return {"hungarian_nls": 0.0, "matched": 0, "unmatched": len(gt_normalized)}

    # Pred candidates: original lines + merged adjacent lines
    pred_candidates = _try_merge_adjacent(pred_segments)
    pred_ws = [strip_whitespace(s) for s in pred_candidates]

    # Also match against full concatenated pred (for extreme merge cases)
    full_pred = strip_whitespace(normalize_for_comparison(pred_text))
    pred_ws.append(full_pred)

    # For each GT region, find best match across all pred candidates
    region_scores = []
    for gt in gt_normalized:
        best = 0.0
        for pred in pred_ws:
            nls = _partial_nls(gt, pred) if len(gt) < len(pred) else _nls(gt, pred)
            if nls > best:
                best = nls
        region_scores.append(best)

    mean_nls = sum(region_scores) / len(region_scores)
    n_matched = sum(1 for s in region_scores if s >= 0.3)

    return {
        "hungarian_nls": round(mean_nls, 6),
        "matched": n_matched,
        "unmatched": len(gt_normalized) - n_matched,
    }


# ---------------------------------------------------------------------------
# Metric 2: Bag-of-Characters F1 (secondary)
# ---------------------------------------------------------------------------

def bag_of_chars(gt_text: str, pred_text: str) -> dict:
    """Compute Bag-of-Characters Precision, Recall, F1.

    CC-OCR style: treat text as a multiset of characters, ignoring order.
    """
    gt_clean = strip_whitespace(normalize_for_comparison(gt_text))
    pred_clean = strip_whitespace(normalize_for_comparison(pred_text))

    gt_counts = Counter(gt_clean)
    pred_counts = Counter(pred_clean)

    matched = sum((gt_counts & pred_counts).values())
    total_gt = sum(gt_counts.values())
    total_pred = sum(pred_counts.values())

    precision = matched / total_pred if total_pred > 0 else 0.0
    recall = matched / total_gt if total_gt > 0 else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )

    return {
        "boc_precision": round(precision, 6),
        "boc_recall": round(recall, 6),
        "boc_f1": round(f1, 6),
    }


# ---------------------------------------------------------------------------
# Metric 3: Full-text NED/CER (tertiary)
# ---------------------------------------------------------------------------

def full_text_ned(gt_text: str, pred_text: str) -> dict:
    """Compute full-text Normalized Edit Distance and CER."""
    gt_norm = strip_whitespace(normalize_for_comparison(gt_text))
    pred_norm = strip_whitespace(normalize_for_comparison(pred_text))

    if not gt_norm and not pred_norm:
        return {"ned": 1.0, "cer": 0.0, "edit_distance": 0, "gt_length": 0}

    ed = Levenshtein.distance(gt_norm, pred_norm)
    max_len = max(len(gt_norm), len(pred_norm))
    ned = 1.0 - (ed / max_len) if max_len > 0 else 1.0
    cer = min(ed / len(gt_norm), 1.0) if len(gt_norm) > 0 else (1.0 if pred_norm else 0.0)

    return {
        "ned": round(ned, 6),
        "cer": round(cer, 6),
        "edit_distance": ed,
        "gt_length": len(gt_norm),
    }


# ---------------------------------------------------------------------------
# Combined evaluation
# ---------------------------------------------------------------------------

@dataclass
class EvalResult:
    """Combined evaluation result for one image."""

    # Primary: Hungarian Matching NLS
    hungarian_nls: float
    hungarian_matched: int
    hungarian_unmatched: int
    # Secondary: Bag-of-Characters
    boc_precision: float
    boc_recall: float
    boc_f1: float
    # Tertiary: Full-text
    ned: float
    cer: float
    edit_distance: int
    gt_length: int


def evaluate_image(gt_regions: list[str], pred_text: str) -> EvalResult:
    """Evaluate OCR output for one image using all three metrics."""
    gt_full = "\n".join(gt_regions)

    hungarian = region_match_nls(gt_regions, pred_text)
    boc = bag_of_chars(gt_full, pred_text)
    ned = full_text_ned(gt_full, pred_text)

    return EvalResult(
        hungarian_nls=hungarian["hungarian_nls"],
        hungarian_matched=hungarian["matched"],
        hungarian_unmatched=hungarian["unmatched"],
        boc_precision=boc["boc_precision"],
        boc_recall=boc["boc_recall"],
        boc_f1=boc["boc_f1"],
        ned=ned["ned"],
        cer=ned["cer"],
        edit_distance=ned["edit_distance"],
        gt_length=ned["gt_length"],
    )


def aggregate_results(results: list[EvalResult]) -> dict:
    """Aggregate evaluation results across multiple images."""
    if not results:
        return {
            "n_images": 0,
            "hungarian_nls": 0.0,
            "boc_f1": 0.0,
            "cer": 0.0,
            "ned": 0.0,
        }

    n = len(results)

    # Weighted CER (weight by GT length, capped at 1.0 per image)
    total_gt = sum(r.gt_length for r in results)
    total_ed = sum(min(r.edit_distance, r.gt_length) for r in results)
    weighted_cer = total_ed / total_gt if total_gt > 0 else 0.0

    return {
        "n_images": n,
        # Primary
        "hungarian_nls": round(sum(r.hungarian_nls for r in results) / n, 6),
        # Secondary
        "boc_precision": round(sum(r.boc_precision for r in results) / n, 6),
        "boc_recall": round(sum(r.boc_recall for r in results) / n, 6),
        "boc_f1": round(sum(r.boc_f1 for r in results) / n, 6),
        # Tertiary
        "ned": round(sum(r.ned for r in results) / n, 6),
        "cer": round(weighted_cer, 6),
        "total_gt_chars": total_gt,
        "total_edit_distance": total_ed,
    }
