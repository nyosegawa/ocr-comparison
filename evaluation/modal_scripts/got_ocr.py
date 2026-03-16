"""GOT-OCR 2.0 on Modal (580M params, ~4GB VRAM)."""

import modal

app = modal.App("ocr-eval-got-ocr")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch",
        "torchvision",
        "transformers==4.45.2",
        "accelerate",
        "Pillow",
        "tiktoken",
        "verovio",
    )
)


@app.function(gpu="T4", image=image, timeout=1800)
def run_ocr(images_b64: list[str]) -> list[str]:
    import base64
    import io

    import torch
    from PIL import Image
    from transformers import AutoModel, AutoTokenizer

    model_id = "stepfun-ai/GOT-OCR2_0"
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    model = AutoModel.from_pretrained(
        model_id,
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )
    model.eval()

    results = []
    for b64 in images_b64:
        img_bytes = base64.b64decode(b64)
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")

        # Save temp image (GOT-OCR expects file path)
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            img.save(f, format="PNG")
            tmp_path = f.name

        try:
            text = model.chat(tokenizer, tmp_path, ocr_type="ocr")
            results.append(text.strip())
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
