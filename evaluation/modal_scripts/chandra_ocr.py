"""Chandra on Modal (9B params, Qwen3 VL based, ~20GB VRAM)."""

import modal

app = modal.App("ocr-eval-chandra")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("libgl1-mesa-glx", "libglib2.0-0")
    .pip_install(
        "chandra-ocr",
        "torch",
        "transformers>=4.57.1",
        "accelerate",
        "Pillow",
        "qwen-vl-utils",
    )
)


@app.function(gpu="A100-40GB", image=image, timeout=1800)
def run_ocr(images_b64: list[str]) -> list[str]:
    import base64
    import io

    from bs4 import BeautifulSoup
    from PIL import Image
    from chandra.model import InferenceManager
    from chandra.model.schema import BatchInputItem

    manager = InferenceManager(method="hf")

    results = []
    for b64 in images_b64:
        img_bytes = base64.b64decode(b64)
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")

        batch = [BatchInputItem(image=img, prompt_type="ocr")]
        output = manager.generate(batch)
        raw_html = output[0].raw
        text = BeautifulSoup(raw_html, "html.parser").get_text(separator="\n").strip()
        results.append(text)

    return results


@app.local_entrypoint()
def main(input: str, output: str):
    from _common import load_input, save_output

    data = load_input(input)
    results = run_ocr.remote(data["images"])
    save_output(output, results)
