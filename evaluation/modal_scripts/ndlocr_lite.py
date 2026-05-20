"""NDLOCR-Lite on Modal (NDL lightweight OCR, ONNX Runtime, CPU)."""

import modal

app = modal.App("ocr-eval-ndlocr-lite")

image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("git", "git-lfs")
    .run_commands(
        "git lfs install"
        " && git clone --branch 1.2.1 --depth 1 https://github.com/ndl-lab/ndlocr-lite.git /opt/ndlocr-lite"
        " && cd /opt/ndlocr-lite && pip install .",
    )
)


@app.function(image=image, timeout=1800)
def run_ocr(images_b64: list[str]) -> list[str]:
    import base64
    import os
    import subprocess
    import tempfile
    from pathlib import Path

    results = []
    for b64 in images_b64:
        img_bytes = base64.b64decode(b64)

        with tempfile.TemporaryDirectory() as tmpdir:
            img_path = os.path.join(tmpdir, "input.png")
            out_dir = os.path.join(tmpdir, "output")
            os.makedirs(out_dir)

            with open(img_path, "wb") as f:
                f.write(img_bytes)

            try:
                proc = subprocess.run(
                    [
                        "ndlocr-lite",
                        "--sourceimg", img_path,
                        "--output", out_dir,
                    ],
                    capture_output=True,
                    text=True,
                    timeout=300,
                )

                if proc.returncode != 0:
                    results.append(
                        f"ERROR: exit {proc.returncode}: {proc.stderr[:500]}"
                    )
                    continue

                # Prefer .txt output (already in reading order)
                txt_file = Path(out_dir) / "input.txt"
                if txt_file.exists():
                    text = txt_file.read_text("utf-8").strip()
                    results.append(text)
                else:
                    # Fallback: parse XML STRING attributes
                    xml_file = Path(out_dir) / "input.xml"
                    if xml_file.exists():
                        import xml.etree.ElementTree as ET

                        tree = ET.parse(str(xml_file))
                        texts = []
                        for elem in tree.iter("LINE"):
                            s = elem.get("STRING", "")
                            if s:
                                texts.append(s)
                        results.append("\n".join(texts))
                    else:
                        results.append("")
            except subprocess.TimeoutExpired:
                results.append("ERROR: timeout (300s)")
            except Exception as e:
                results.append(f"ERROR: {e}")

    return results


@app.local_entrypoint()
def main(input: str, output: str):
    from _common import load_input, save_output

    data = load_input(input)
    results = run_ocr.remote(data["images"])
    save_output(output, results)
