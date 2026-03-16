"""HunyuanOCR on Modal (1B params, ~20GB VRAM)."""

import modal

from _common import OCR_PROMPT_JA

app = modal.App("ocr-eval-hunyuan")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch",
        "transformers",
        "accelerate",
        "Pillow",
        "vllm>=0.12.0",
    )
    .env({"TRANSFORMERS_CACHE": "/cache"})
)


@app.function(gpu="L4", image=image, timeout=1800)
def run_ocr(images_b64: list[str]) -> list[str]:
    import base64
    import io
    import re

    from PIL import Image
    from transformers import AutoProcessor
    from vllm import LLM, SamplingParams

    model_id = "tencent/HunyuanOCR"
    llm = LLM(model=model_id, trust_remote_code=True, max_model_len=8192)
    processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
    sampling = SamplingParams(max_tokens=4096, temperature=0.0)

    results = []

    for b64 in images_b64:
        img_bytes = base64.b64decode(b64)
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")

        messages = [
            {"role": "system", "content": ""},
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
        text = _clean_repeated_substrings(text)
        results.append(text)

    return results


def _clean_repeated_substrings(text: str, threshold: int = 3) -> str:
    """Remove repeated substrings (known HunyuanOCR issue with long outputs)."""
    import re

    if len(text) < 100:
        return text
    for length in range(len(text) // threshold, 10, -1):
        pattern = re.compile(r"(.{" + str(length) + r",}?)" + r"\1{" + str(threshold - 1) + r",}")
        match = pattern.search(text)
        if match:
            text = text[: match.start()] + match.group(1)
    return text


@app.local_entrypoint()
def main(input: str, output: str):
    from _common import load_input, save_output

    data = load_input(input)
    results = run_ocr.remote(data["images"])
    save_output(output, results)
