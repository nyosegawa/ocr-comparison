"""DeepSeek-OCR on Modal (3B MoE, ~8GB VRAM)."""

import modal

app = modal.App("ocr-eval-deepseek-ocr")

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


def _clean_repeated_substrings(text: str, threshold: int = 3) -> str:
    """Remove repeated substrings (common issue with OCR models)."""
    import re

    if len(text) < 100:
        return text
    for length in range(len(text) // threshold, 10, -1):
        pattern = re.compile(
            r"(.{" + str(length) + r",}?)" + r"\1{" + str(threshold - 1) + r",}"
        )
        match = pattern.search(text)
        if match:
            text = text[: match.start()] + match.group(1)
    return text


@app.function(gpu="L4", image=image, timeout=1800)
def run_ocr(images_b64: list[str]) -> list[str]:
    import base64
    import io

    from PIL import Image
    from vllm import LLM, SamplingParams

    model_id = "deepseek-ai/DeepSeek-OCR"

    # DeepSeek-OCR is natively supported in vLLM >= 0.11.1
    # Use NGramPerReqLogitsProcessor for repetition control
    logits_processors = None
    try:
        from vllm.model_executor.models.deepseek_ocr import (
            NGramPerReqLogitsProcessor,
        )

        logits_processors = [NGramPerReqLogitsProcessor]
    except ImportError:
        pass

    llm_kwargs = {
        "model": model_id,
        "trust_remote_code": True,
        "max_model_len": 8192,
        "enable_prefix_caching": False,
        "mm_processor_cache_gb": 0,
    }
    if logits_processors:
        llm_kwargs["logits_processors"] = logits_processors

    llm = LLM(**llm_kwargs)

    sampling_kwargs = {
        "max_tokens": 8192,
        "temperature": 0.0,
    }
    # extra_args configures the NGram logits processor
    try:
        sampling = SamplingParams(
            **sampling_kwargs,
            extra_args={
                "ngram_size": 30,
                "window_size": 90,
                "whitelist_token_ids": {128821, 128822},
            },
            skip_special_tokens=False,
        )
    except TypeError:
        # Fallback if extra_args is not supported in this vLLM version
        sampling = SamplingParams(**sampling_kwargs)

    # Base mode: plain text OCR
    prompt = "<image>\nFree OCR. "

    results = []
    for b64 in images_b64:
        img_bytes = base64.b64decode(b64)
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")

        try:
            output = llm.generate(
                [{"prompt": prompt, "multi_modal_data": {"image": img}}],
                sampling_params=sampling,
            )
            text = output[0].outputs[0].text.strip()
            text = _clean_repeated_substrings(text)
            results.append(text)
        except Exception as e:
            results.append(f"ERROR: {e}")

    return results


@app.local_entrypoint()
def main(input: str, output: str):
    from _common import load_input, save_output

    data = load_input(input)
    results = run_ocr.remote(data["images"])
    save_output(output, results)
