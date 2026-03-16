"""olmOCR-2 on Modal (7B FP8, Qwen2.5-VL based, ~14GB VRAM)."""

import modal

from _common import OCR_PROMPT_JA

app = modal.App("ocr-eval-olmocr")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch",
        "transformers",
        "accelerate",
        "Pillow",
        "vllm>=0.12.0",
        "qwen-vl-utils",
    )
)


@app.function(gpu="L4", image=image, timeout=1800)
def run_ocr(images_b64: list[str]) -> list[str]:
    import base64
    import io
    import re

    from PIL import Image
    from transformers import AutoProcessor
    from vllm import LLM, SamplingParams

    model_id = "allenai/olmOCR-2-7B-1025-FP8"
    processor_id = "Qwen/Qwen2.5-VL-7B-Instruct"

    llm = LLM(model=model_id, trust_remote_code=True, max_model_len=16384)
    processor = AutoProcessor.from_pretrained(processor_id, trust_remote_code=True)
    sampling = SamplingParams(max_tokens=4096, temperature=0.0)

    results = []

    for b64 in images_b64:
        img_bytes = base64.b64decode(b64)
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")

        # Resize to max 1288px on longest side (olmOCR-2 recommendation)
        max_dim = 1288
        w, h = img.size
        if max(w, h) > max_dim:
            scale = max_dim / max(w, h)
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": img},
                    {"type": "text", "text": OCR_PROMPT_JA},
                ],
            },
        ]
        prompt = processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        output = llm.generate(
            [{"prompt": prompt, "multi_modal_data": {"image": [img]}}],
            sampling_params=sampling,
        )
        text = output[0].outputs[0].text.strip()
        text = _strip_yaml_frontmatter(text)
        results.append(text)

    return results


def _strip_yaml_frontmatter(text: str) -> str:
    """Remove YAML front matter that olmOCR-2 may prepend to its output."""
    import re

    stripped = re.sub(r"^---\s*\n.*?\n---\s*\n?", "", text, count=1, flags=re.DOTALL)
    return stripped.strip()


@app.local_entrypoint()
def main(input: str, output: str):
    from _common import load_input, save_output

    data = load_input(input)
    results = run_ocr.remote(data["images"])
    save_output(output, results)
