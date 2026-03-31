"""Sarashina2.2-OCR on Modal (3B params, SigLIP2 + Sarashina2.2-3B-Instruct).

Uses transformers directly (not vLLM) because the model architecture
requires trust_remote_code and is not yet natively supported in vLLM.
"""

import modal

app = modal.App("ocr-eval-sarashina-ocr")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch",
        "torchvision",
        "Pillow",
        "accelerate",
        "protobuf",
        "sentencepiece",
        "transformers==4.57.1",
    )
)


@app.function(gpu="L4", image=image, timeout=1800)
def run_ocr(images_b64: list[str]) -> list[str]:
    import base64
    import io

    import torch
    from PIL import Image
    from transformers import AutoModelForCausalLM, AutoProcessor, set_seed

    set_seed(42)

    model_id = "sbintuitions/sarashina2.2-ocr"
    processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map="cuda",
        torch_dtype="auto",
        trust_remote_code=True,
    )

    results = []

    for b64 in images_b64:
        img_bytes = base64.b64decode(b64)
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")

        # モデルカードの推奨通り画像のみ（テキストプロンプトなし）で推論する。
        # OCR_PROMPT_JA を付けても結果は変わらないが、公式の使い方に合わせる。
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": img},
                ],
            },
        ]
        inputs = processor.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_dict=True,
            return_tensors="pt",
        ).to(model.device)

        generated_ids = model.generate(
            **inputs,
            max_new_tokens=6000,
            temperature=0.0,
            top_p=0.95,
            repetition_penalty=1.3,
            use_cache=True,
        )
        output_text = processor.decode(
            generated_ids[0][inputs["input_ids"].shape[-1] :],
            skip_special_tokens=True,
        )
        results.append(output_text.strip())

    return results


@app.local_entrypoint()
def main(input: str, output: str):
    from _common import load_input, save_output

    data = load_input(input)
    results = run_ocr.remote(data["images"])
    save_output(output, results)
