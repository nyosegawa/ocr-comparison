"""Nemotron OCR v2 multilingual on Modal (84M params, ~2GB VRAM).

Traditional detector-recognizer pipeline (not a VLM).
RegNetX-8GF detector + Transformer recognizer + relational model.
Supports EN, CN, JA, KO, RU at line-level granularity.
"""

import modal

app = modal.App("ocr-eval-nemotron-ocr-v2")

image = (
    modal.Image.from_registry(
        "nvidia/cuda:12.8.0-devel-ubuntu22.04",
        add_python="3.12",
    )
    .apt_install(
        "git",
        "git-lfs",
        "g++",
        "libgomp1",  # OpenMP runtime
    )
    .env({
        "TORCH_CUDA_ARCH_LIST": "8.9+PTX",
        "CC": "gcc",
        "CXX": "g++",
    })
    .run_commands("git lfs install")
    .run_commands(
        "pip install torch torchvision"
        " --index-url https://download.pytorch.org/whl/cu128",
    )
    .pip_install("setuptools", "hatchling", "editables", "ninja")
    .run_commands(
        "git clone https://huggingface.co/nvidia/nemotron-ocr-v2 /root/nemotron-ocr",
    )
    .pip_install("shapely>=2.1.2", "huggingface_hub>=0.20.0")
    # Build C++ CUDA extension, then install via PYTHONPATH
    .run_commands(
        "cd /root/nemotron-ocr/nemotron-ocr && python scripts/build-extension.py",
    )
    .env({"PYTHONPATH": "/root/nemotron-ocr/nemotron-ocr/src"})
    .run_commands(
        "python -c 'from nemotron_ocr_cpp import calc_poly_min_rrect; print(\"C++ ext OK\")'",
    )
)


@app.function(gpu="L4", image=image, timeout=1800)
def run_ocr(images_b64: list[str]) -> list[str]:
    import base64
    import os
    import tempfile

    from nemotron_ocr.inference.pipeline_v2 import NemotronOCRV2

    ocr = NemotronOCRV2(model_dir="/root/nemotron-ocr/v2_multilingual")

    results = []
    for b64 in images_b64:
        img_bytes = base64.b64decode(b64)

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(img_bytes)
            tmp_path = f.name

        try:
            predictions = ocr(tmp_path)
            text = "\n".join(
                pred["text"] for pred in predictions if pred.get("text")
            )
            results.append(text)
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
