"""Nanonets-OCR-s on Modal (4B params, Qwen2.5-VL-3B based, ~10GB VRAM)."""

import modal

app = modal.App("ocr-eval-nanonets")

OCR_PROMPT_JA = (
    "この画像に書かれているテキストを正確に読み取ってください。"
    "テキストのみを出力してください。余計な説明は不要です。"
)

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

    from PIL import Image
    from transformers import AutoProcessor
    from vllm import LLM, SamplingParams

    model_id = "nanonets/Nanonets-OCR-s"
    llm = LLM(model=model_id, trust_remote_code=True, max_model_len=32768)
    processor = AutoProcessor.from_pretrained(
        model_id,
        trust_remote_code=True,
        max_pixels=1003520,  # limit image tokens (~1344 tokens)
    )
    sampling = SamplingParams(max_tokens=1024, temperature=0.0, repetition_penalty=1.2)

    results = []

    for b64 in images_b64:
        img_bytes = base64.b64decode(b64)
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
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
        results.append(text)

    return results


@app.local_entrypoint()
def main(input: str, output: str):
    from _common import load_input, save_output

    data = load_input(input)
    results = run_ocr.remote(data["images"])
    save_output(output, results)
