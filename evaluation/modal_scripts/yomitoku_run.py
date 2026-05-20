"""YomiToku on Modal (Japanese-specialized, <8GB VRAM)."""

import modal

app = modal.App("ocr-eval-yomitoku")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("libgl1-mesa-glx", "libglib2.0-0")
    .pip_install(
        "yomitoku>=0.13.0",
        "torch>=2.6.0",
        "torchvision>=0.21.0",
        "Pillow",
        "opencv-python",
    )
)


@app.function(gpu="T4", image=image, timeout=1800)
def run_ocr(images_b64: list[str]) -> list[str]:
    import base64
    import io

    import cv2
    import numpy as np
    from PIL import Image
    from yomitoku import DocumentAnalyzer

    analyzer = DocumentAnalyzer(visualize=False, device="cuda")

    results = []
    for b64 in images_b64:
        try:
            img_bytes = base64.b64decode(b64)
            pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            # YomiToku expects BGR numpy array (OpenCV convention)
            img = np.array(pil_img)[:, :, ::-1].copy()

            result, *_ = analyzer(img)

            # Collect all text elements with their reading order
            elements: list[tuple[int, str]] = []

            # Paragraphs (including role: headings, headers, footers)
            for p in result.paragraphs:
                if p.contents:
                    elements.append((p.order if p.order is not None else 9999, p.contents))

            # Table cells — flatten into text per table, ordered by row/col
            for table in result.tables:
                cell_texts = []
                for cell in sorted(table.cells, key=lambda c: (c.row, c.col)):
                    if cell.contents:
                        cell_texts.append(cell.contents)
                if cell_texts:
                    elements.append((table.order if table.order is not None else 9999, "\n".join(cell_texts)))

            # Figures contain nested paragraphs
            for fig in result.figures:
                fig_texts = []
                for p in fig.paragraphs:
                    if p.contents:
                        fig_texts.append(p.contents)
                if fig_texts:
                    elements.append((fig.order if fig.order is not None else 9999, "\n".join(fig_texts)))

            # Sort by reading order and join
            elements.sort(key=lambda x: x[0])
            results.append("\n".join(text for _, text in elements))
        except Exception as e:
            results.append(f"ERROR: {e}")

    return results


@app.local_entrypoint()
def main(input: str, output: str):
    from _common import load_input, save_output

    data = load_input(input)
    results = run_ocr.remote(data["images"])
    save_output(output, results)
