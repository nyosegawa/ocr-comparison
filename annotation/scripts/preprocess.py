"""
画像前処理パイプライン (ML版)

1. 紙面検出・切り出し (OpenCV Otsu + morphology + perspective transform)
2. 向き補正 - 粗い回転 (docTR MobileNetV3, 0/90/180/270)
3. 向き補正 - 細かい傾き (jdeskew)
4. コントラスト正規化 (CLAHE)
5. ノイズ除去 (fastNlMeansDenoising)
6. 二値化 (適応的閾値)

Usage: python preprocess.py <input_path> <output_path>
"""

import sys
import json
import cv2
import numpy as np


# ── Step 1: 紙面検出・切り出し ──────────────────────────────

def detect_paper_boundary(img: np.ndarray) -> np.ndarray | None:
    """Otsu二値化 + モルフォロジーで紙面領域を検出し4点を返す"""
    h, w = img.shape[:2]
    img_area = h * w

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    blurred = cv2.GaussianBlur(gray, (51, 51), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 30))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=3)

    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    cnt = contours[0]

    if cv2.contourArea(cnt) < img_area * 0.15:
        return None

    # minAreaRect: 切れるリスクがないため approxPolyDP より安全
    rect = cv2.minAreaRect(cnt)
    box = np.int32(cv2.boxPoints(rect))
    return box


def order_points(pts: np.ndarray) -> np.ndarray:
    """4点を [左上, 右上, 右下, 左下] の順に並べ替え"""
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    d = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(d)]
    rect[3] = pts[np.argmax(d)]
    return rect


def crop_paper(img: np.ndarray) -> np.ndarray:
    """紙面を検出して透視変換で切り出す"""
    pts = detect_paper_boundary(img)
    if pts is None:
        print("[paper] no boundary detected, using full image", file=sys.stderr)
        return img

    ordered = order_points(pts.astype("float32"))
    tl, tr, br, bl = ordered

    max_w = int(max(np.linalg.norm(br - bl), np.linalg.norm(tr - tl)))
    max_h = int(max(np.linalg.norm(tr - br), np.linalg.norm(tl - bl)))

    dst = np.array(
        [[0, 0], [max_w - 1, 0], [max_w - 1, max_h - 1], [0, max_h - 1]],
        dtype="float32",
    )
    M = cv2.getPerspectiveTransform(ordered, dst)
    warped = cv2.warpPerspective(img, M, (max_w, max_h))
    print(f"[paper] cropped to {max_w}x{max_h}", file=sys.stderr)
    return warped


# ── Step 2: 粗い向き補正 (docTR) ─────────────────────────

def correct_coarse_orientation(img: np.ndarray) -> np.ndarray:
    """docTR MobileNetV3で0/90/180/270の粗い向き補正"""
    try:
        from doctr.models import page_orientation_predictor

        predictor = page_orientation_predictor(
            arch="mobilenet_v3_small_page_orientation", pretrained=True
        )

        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w = rgb.shape[:2]
        max_dim = 512
        if max(h, w) > max_dim:
            scale = max_dim / max(h, w)
            rgb = cv2.resize(rgb, (int(w * scale), int(h * scale)))

        # docTR returns [[class_indices], [page_indices], [confidences]]
        result = predictor([rgb])
        class_idx = result[0][0]
        confidence = result[2][0]
        rotation = class_idx * 90

        print(
            f"[orientation] detected: {rotation}° (confidence: {confidence:.2f})",
            file=sys.stderr,
        )

        # 低confidence（<0.7）のときは回転しない
        if confidence < 0.7:
            print(f"[orientation] low confidence, skipping rotation", file=sys.stderr)
            return img

        if rotation == 90:
            return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        elif rotation == 180:
            return cv2.rotate(img, cv2.ROTATE_180)
        elif rotation == 270:
            return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    except Exception as e:
        print(f"[orientation] docTR failed, skipping: {e}", file=sys.stderr)

    return img


# ── Step 3: 細かい傾き補正 (jdeskew) ─────────────────────

def correct_fine_skew(img: np.ndarray) -> np.ndarray:
    """jdeskewで微小な傾きを補正"""
    try:
        from jdeskew.estimator import get_angle

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        angle = get_angle(gray)

        print(f"[deskew] detected angle: {angle:.2f}°", file=sys.stderr)

        if abs(angle) < 0.3 or abs(angle) > 15:
            return img

        h, w = img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
    except Exception as e:
        print(f"[deskew] jdeskew failed, skipping: {e}", file=sys.stderr)

    return img


# ── Step 4: 影除去 → 二値化 ───────────────────────────

def remove_shadow_and_enhance(img: np.ndarray) -> np.ndarray:
    """medianBlurで背景推定 → 除算で影除去 → CLAHE コントラスト強調"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img.copy()

    # 背景推定: 大きなmedianBlurでテキストを消し、照明ムラだけ残す
    bg = cv2.medianBlur(gray, 255)

    # 除算で照明正規化 (影やムラが消え、テキストだけ残る)
    flat = cv2.divide(gray, bg, scale=255)

    # CLAHE でコントラスト強調（薄い筆跡も読みやすくなる）
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(flat)

    print("[enhance] shadow removal + CLAHE", file=sys.stderr)
    return cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)


# ── Main ──────────────────────────────────────────────

def preprocess(input_path: str, output_path: str) -> None:
    img = cv2.imread(input_path)
    if img is None:
        print(f"Error: Cannot read image: {input_path}", file=sys.stderr)
        sys.exit(1)

    original_h, original_w = img.shape[:2]
    print(f"[input] {original_w}x{original_h}", file=sys.stderr)

    img = crop_paper(img)
    img = correct_coarse_orientation(img)
    img = correct_fine_skew(img)
    img = remove_shadow_and_enhance(img)

    final_h, final_w = img.shape[:2]
    print(f"[output] {final_w}x{final_h}", file=sys.stderr)

    cv2.imwrite(output_path, img, [cv2.IMWRITE_PNG_COMPRESSION, 6])

    print(
        json.dumps(
            {
                "original_width": original_w,
                "original_height": original_h,
                "width": final_w,
                "height": final_h,
            }
        )
    )


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input_path> <output_path>", file=sys.stderr)
        sys.exit(1)

    preprocess(sys.argv[1], sys.argv[2])
