"""Common utilities for Modal OCR scripts."""

OCR_PROMPT_JA = (
    "この画像に書かれているテキストを正確に読み取ってください。"
    "テキストのみを出力してください。余計な説明は不要です。"
)


def decode_images(images_b64: list[str]):
    """Decode base64 images to PIL Image objects."""
    import base64
    import io

    from PIL import Image

    results = []
    for b64 in images_b64:
        img_bytes = base64.b64decode(b64)
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        results.append(img)
    return results


def load_input(input_path: str) -> dict:
    """Load input JSON file."""
    import json

    with open(input_path) as f:
        return json.load(f)


def save_output(output_path: str, results: list[str]):
    """Save output JSON file."""
    import json

    with open(output_path, "w") as f:
        json.dump({"results": results}, f, ensure_ascii=False, indent=2)
