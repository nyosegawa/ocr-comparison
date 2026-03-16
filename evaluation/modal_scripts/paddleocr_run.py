"""PaddleOCR on Modal (PP-OCRv5, lightweight)."""

import modal

app = modal.App("ocr-eval-paddleocr")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("libgl1-mesa-glx", "libglib2.0-0")
    .run_commands(
        "pip install paddlepaddle-gpu"
        " -i https://www.paddlepaddle.org.cn/packages/stable/cu126/"
    )
    .pip_install(
        "paddleocr>=3.0",
        "Pillow",
    )
)


@app.function(gpu="T4", image=image, timeout=1800)
def run_ocr(images_b64: list[str]) -> list[str]:
    import base64
    import os
    import tempfile

    from paddleocr import PaddleOCR

    engine = PaddleOCR(
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
        device="gpu:0",
    )

    results = []
    for b64 in images_b64:
        img_bytes = base64.b64decode(b64)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(img_bytes)
            tmp_path = f.name

        try:
            output = engine.predict(input=tmp_path)
            texts = []
            for res in output:
                inner = res.json.get("res", res.json)
                rec_texts = inner.get("rec_texts", [])
                texts.extend(rec_texts)
            results.append("\n".join(texts))
        except Exception as e:
            results.append(f"ERROR: {e}")
        finally:
            os.unlink(tmp_path)

    return results


@app.local_entrypoint()
def main(input: str, output: str):
    from _common import load_input, save_output

    data = load_input(input)
    results = run_ocr.remote(data["images"])
    save_output(output, results)
