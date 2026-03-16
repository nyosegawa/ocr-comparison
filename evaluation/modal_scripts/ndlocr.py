"""NDLOCR v2 (国立国会図書館OCR フル版) on Modal (mmdet + ResNet, ~6GB VRAM)."""

import modal

app = modal.App("ocr-eval-ndlocr-v2")

image = (
    modal.Image.from_registry(
        "nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04",
        add_python="3.10",
    )
    .apt_install(
        "libgl1-mesa-dev", "libglib2.0-0", "zip", "git", "wget",
        "locales",
        # KYTEA build deps
        "g++", "make", "autoconf", "automake", "libtool",
    )
    .run_commands("locale-gen ja_JP.UTF-8")
    .env({
        "LANG": "ja_JP.UTF-8",
        "LANGUAGE": "ja_JP:ja",
        "LC_ALL": "ja_JP.UTF-8",
        "PROJECT_DIR": "/root/ocr_cli",
        "FORCE_CUDA": "1",
        "TORCH_CUDA_ARCH_LIST": "7.5+PTX",
        "TORCH_NVCC_FLAGS": "-Xfatbin -compress-all",
    })
    # PyTorch 2.1.1 with CUDA 12.1
    .run_commands(
        "pip install torch==2.1.1 torchvision==0.16.1 torchaudio==2.1.1"
        " --index-url https://download.pytorch.org/whl/cu121",
    )
    # Build KYTEA (Japanese morphological analyzer) from source
    .run_commands(
        "wget http://www.phontron.com/kytea/download/kytea-0.4.7.tar.gz"
        " && tar xzf kytea-0.4.7.tar.gz"
        " && cd kytea-0.4.7 && ./configure && make && make install && ldconfig"
        " && cd / && rm -rf kytea-0.4.7*",
    )
    # Clone ndlocr_cli with all 7 submodules
    .run_commands(
        "git clone --recursive https://github.com/ndl-lab/ndlocr_cli /root/ocr_cli",
    )
    # Install Python dependencies
    .run_commands("pip install -r /root/ocr_cli/requirements.txt")
    .run_commands("pip install mmdet==3.3.0")
    # Pre-compiled mmcv wheel for cu121/torch2.1
    .run_commands(
        "pip install mmcv==2.1.0"
        " -f https://download.openmmlab.com/mmcv/dist/cu121/torch2.1/index.html",
    )
    .run_commands(
        "pip install -r /root/ocr_cli/submodules/ruby_prediction/requirements.txt",
    )
    # Download 5 model weight files
    .run_commands(
        "cd /root/ocr_cli"
        " && mkdir -p submodules/text_recognition_lightning/models/rf_author"
        " && mkdir -p submodules/text_recognition_lightning/models/rf_title"
        " && mkdir -p submodules/ndl_layout/models"
        " && mkdir -p submodules/separate_pages_mmdet/models"
        " && wget -nc https://lab.ndl.go.jp/dataset/ndlocr_v2/text_recognition_lightning/resnet-orient2.ckpt"
        "    -P submodules/text_recognition_lightning/models/"
        " && wget -nc https://lab.ndl.go.jp/dataset/ndlocr_v2/text_recognition_lightning/rf_author/model.pkl"
        "    -P submodules/text_recognition_lightning/models/rf_author/"
        " && wget -nc https://lab.ndl.go.jp/dataset/ndlocr_v2/text_recognition_lightning/rf_title/model.pkl"
        "    -P submodules/text_recognition_lightning/models/rf_title/"
        " && wget -nc https://lab.ndl.go.jp/dataset/ndlocr_v2/ndl_layout/ndl_retrainmodel.pth"
        "    -P submodules/ndl_layout/models/"
        " && wget -nc https://lab.ndl.go.jp/dataset/ndlocr_v2/separate_pages_mmdet/epoch_180.pth"
        "    -P submodules/separate_pages_mmdet/models/",
    )
)


@app.function(gpu="A10G", image=image, timeout=1800)
def run_ocr(images_b64: list[str]) -> list[str]:
    import base64
    import glob
    import os
    import subprocess
    import tempfile

    results = []
    for b64 in images_b64:
        img_bytes = base64.b64decode(b64)

        with tempfile.TemporaryDirectory() as tmpdir:
            img_path = os.path.join(tmpdir, "input.png")
            # Do NOT pre-create out_dir — ndlocr_cli creates it and
            # renames to a timestamped dir if it already exists.
            out_dir = os.path.join(tmpdir, "output")

            with open(img_path, "wb") as f:
                f.write(img_bytes)

            try:
                proc = subprocess.run(
                    [
                        "python", "/root/ocr_cli/main.py", "infer",
                        img_path, out_dir,
                        "-s", "f",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=600,
                    cwd="/root/ocr_cli",
                )

                if proc.returncode != 0:
                    results.append(
                        f"ERROR: exit {proc.returncode}: {proc.stderr[:500]}"
                    )
                    continue

                # Find _main.txt output files (primary output)
                main_txts = glob.glob(
                    os.path.join(out_dir, "**", "*_main.txt"), recursive=True
                )
                if main_txts:
                    texts = []
                    for txt_path in sorted(main_txts):
                        with open(txt_path, encoding="utf-8") as f:
                            text = f.read().strip()
                            if text:
                                texts.append(text)
                    results.append("\n".join(texts))
                else:
                    # Fallback: parse XML LINE[@STRING] attributes
                    xml_files = glob.glob(
                        os.path.join(out_dir, "**", "*.xml"), recursive=True
                    )
                    if xml_files:
                        import xml.etree.ElementTree as ET

                        texts = []
                        for xml_path in sorted(xml_files):
                            tree = ET.parse(xml_path)
                            for line in tree.iter("LINE"):
                                s = line.get("STRING", "")
                                if s:
                                    texts.append(s)
                        results.append("\n".join(texts))
                    else:
                        results.append("")

            except subprocess.TimeoutExpired:
                results.append("ERROR: timeout (600s)")
            except Exception as e:
                results.append(f"ERROR: {e}")

    return results


@app.local_entrypoint()
def main(input: str, output: str):
    from _common import load_input, save_output

    data = load_input(input)
    results = run_ocr.remote(data["images"])
    save_output(output, results)
