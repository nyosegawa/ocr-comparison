---
name: modal-ocr-script
description: >
  Modal上でOCRモデルを動かすスクリプトの新規作成・デバッグ・動作確認を行う。
  このプロジェクトのmodal_scripts/パターンに準拠したスクリプトを生成し、
  既知のハマりどころを事前回避する。
  Use when: "Modal", "modal_scripts", "Modalスクリプト", "Modalで動かす",
  "GPUで実行", "新しいOCRモデルを追加", "Modalモデル追加", "modal run".
compatibility: Requires Modal CLI (modal token new), Python 3.11, evaluation/ directory with modal_scripts/
---

# Modal OCR Script Builder

## このスキルの目的

`evaluation/modal_scripts/` 配下に新しいOCRモデル用のModalスクリプトを作成し、
動作確認まで完了させる。過去の実装で得られたハマりどころを事前に回避する。

## Instructions

### Step 1: 既存パターンの確認

新しいスクリプトを書く前に、必ず既存のスクリプトを1つ読んで構造を把握する。

```bash
cat evaluation/modal_scripts/paddleocr_run.py  # 非VLMモデルの参考
cat evaluation/modal_scripts/nanonets_ocr.py    # VLM (vLLM) モデルの参考
cat evaluation/modal_scripts/_common.py          # 共通ユーティリティ
```

全スクリプトは以下の構造に従う:

```python
"""Model Name on Modal (params, ~VRAM)."""
import modal

app = modal.App("ocr-eval-{model-name}")

image = (
    modal.Image.debian_slim(python_version="3.11")
    # ... 依存パッケージ
)

@app.function(gpu="T4", image=image, timeout=1800)
def run_ocr(images_b64: list[str]) -> list[str]:
    # モデルロード → 推論 → テキスト返却
    ...

@app.local_entrypoint()
def main(input: str, output: str):
    from _common import load_input, save_output
    data = load_input(input)
    results = run_ocr.remote(data["images"])
    save_output(output, results)
```

### Step 2: スクリプト作成

モデルの種類に応じてテンプレートを選択:

**A. VLMモデル (transformers/vLLM)** — HunyuanOCR, DeepSeek, Nanonets等

```python
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("torch", "transformers", "accelerate", "Pillow", "vllm")
)

@app.function(gpu="L4", image=image, timeout=1800)  # VLMはL4以上推奨
def run_ocr(images_b64: list[str]) -> list[str]:
    from _common import OCR_PROMPT_JA, decode_images
    from vllm import LLM, SamplingParams

    llm = LLM(model=MODEL_ID, trust_remote_code=True, max_model_len=4096)
    sampling = SamplingParams(max_tokens=4096, temperature=0.0)
    images = decode_images(images_b64)
    results = []
    for img in images:
        prompt = f"<image>\n{OCR_PROMPT_JA}"
        output = llm.generate(
            [{"prompt": prompt, "multi_modal_data": {"image": img}}],
            sampling_params=sampling,
        )
        results.append(output[0].outputs[0].text.strip())
    return results
```

**B. 専用OCRライブラリ** — PaddleOCR, YomiToku等

```python
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("libgl1-mesa-glx", "libglib2.0-0")  # OpenCV系が必要な場合
    .pip_install("model-specific-package", "Pillow")
)

@app.function(gpu="T4", image=image, timeout=1800)
def run_ocr(images_b64: list[str]) -> list[str]:
    # ファイルパス入力が必要なモデルはtempfileを使う
    import base64, os, tempfile
    ...
```

### Step 3: 動作確認

**テスト入力の作成:**

```bash
python3 -c "
import base64, json
with open('../annotation/uploads/$(ls ../annotation/uploads/ | head -1)', 'rb') as f:
    b64 = base64.b64encode(f.read()).decode()
with open('/tmp/test_input.json', 'w') as f:
    json.dump({'images': [b64]}, f)
"
```

**Modal実行:**

```bash
cd evaluation
modal run modal_scripts/{script_name}.py --input /tmp/test_input.json --output /tmp/test_output.json
```

注意: `--` は不要。Modalの引数はそのまま渡す。

**結果確認:**

```bash
cat /tmp/test_output.json | python3 -m json.tool
```

- `"results": ["テキスト..."]` が返ればOK
- `"results": ["ERROR: ..."]` ならエラー内容を確認して修正
- `"results": [""]` なら結果のパース方法が間違っている（後述のトラブルシューティング参照）

### Step 4: 評価フレームワークへの統合

1. `evaluation/src/models/modal_runner.py` にクラス追加:

```python
class NewModelModal(ModalOCRModel):
    name = "model-name"
    script_name = "script_name.py"
    gpu = "T4"  # or "L4", "A100-40GB"
```

2. `evaluation/src/models/registry.py` の `get_all_models()` に追加

3. 評価実行:

```bash
cd evaluation
uv run python -m src.evaluate run --models model-name
```

4. TODO.md のチェックリストを更新 (`- [ ]` → `- [x]` + スコア記載)

## 既知のハマりどころと対策

### PaddlePaddle: CPU版はoneDNNエラーで動かない

**症状:** `ConvertPirAttribute2RuntimeAttribute not support [pir::ArrayAttribute]`

**原因:** `paddlepaddle` (CPU版) のoneDNNバックエンドがPP-OCRv5のserver modelに非対応

**対策:** `paddlepaddle-gpu` をPaddlePaddle公式インデックスからインストール:
```python
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("libgl1-mesa-glx", "libglib2.0-0")
    .run_commands(
        "pip install paddlepaddle-gpu"
        " -i https://www.paddlepaddle.org.cn/packages/stable/cu126/"
    )
    .pip_install("paddleocr>=3.0", "Pillow")
)
```

`FLAGS_enable_pir_api=0` では解決しない。

### PaddleOCR 3.x: APIが2.xから変更されている

**症状:** `PaddleOCR.predict() got an unexpected keyword argument 'cls'`

**対策:**
- `engine.ocr(path, cls=True)` → `engine.predict(input=path)` に変更
- 結果は `res.json["res"]["rec_texts"]` にネスト（`res.json["rec_texts"]` ではない）
- コンストラクタ: `PaddleOCR(use_angle_cls=True, lang="japan")` →
  `PaddleOCR(use_doc_orientation_classify=False, use_doc_unwarping=False, use_textline_orientation=False, device="gpu:0")`

### pip install の順序とカスタムインデックス

**問題:** `pip_install()` はPyPIのみ。カスタムインデックスが必要な場合は使えない。

**対策:** `run_commands()` で先にインストールしてから、残りを `pip_install()` で:
```python
image = (
    modal.Image.debian_slim(python_version="3.11")
    .run_commands("pip install some-pkg -i https://custom-index/")
    .pip_install("other-pkg")  # PyPIからの通常パッケージ
)
```

### OpenCV依存パッケージ (libgl1)

**症状:** `ImportError: libGL.so.1: cannot open shared object file`

**対策:** `.apt_install("libgl1-mesa-glx", "libglib2.0-0")` を追加。
画像処理系ライブラリ（PaddleOCR, YomiToku等）で必要。

### GPU版パッケージのCUDAバージョン

Modal T4/L4/A100は CUDA 12.x 環境。`cu126` (CUDA 12.6) パッケージを選択すれば動作する。

### 結果が空文字列になる

**原因:** ライブラリのレスポンス構造が想定と異なる

**対策:** デバッグ時に一時的にJSON構造をダンプして確認:
```python
import json as _json
print(f"DEBUG keys: {list(res_json.keys())}")
print(f"DEBUG: {_json.dumps(res_json, ensure_ascii=False, default=str)[:2000]}")
```

### `_common.py` のインポート

`_common.py` は `@app.local_entrypoint()` (ローカル側) でのみimport可能。
`@app.function()` (リモート側) では `_common.py` は存在しないため、
リモート関数内で `decode_images` や `OCR_PROMPT_JA` を使う場合は
`from _common import ...` をリモート関数の先頭に書く（Modalが自動マウントする）。

## Examples

### Example 1: 新しいVLMモデルを追加

User: 「InternVLをModalで評価に追加して」

1. `modal_scripts/internvl_ocr.py` を VLMテンプレートで作成
2. テスト入力で `modal run` 確認
3. `modal_runner.py` と `registry.py` に登録
4. `uv run python -m src.evaluate run --models internvl` で評価
5. TODO.md を更新

### Example 2: 既存スクリプトがエラーで動かない

User: 「YomiTokuのModalスクリプトがエラーになる」

1. エラーメッセージを確認
2. 上記の「既知のハマりどころ」に該当するか確認
3. 該当しない場合はライブラリのドキュメント/PyPIで最新APIを調査
4. 修正して `modal run` で再テスト
