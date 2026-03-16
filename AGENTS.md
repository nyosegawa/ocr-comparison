# 開発ガイド

## 新しい OCR モデルの追加方法

### API モデル

1. `evaluation/src/models/` にアダプタを作成（`base.OCRModel` を継承）
2. `async recognize(image: Image) -> str` を実装
3. `evaluation/src/models/registry.py` の `get_all_models()` に登録

### Modal GPU モデル

1. `evaluation/modal_scripts/` にスクリプトを作成
   - `run_ocr(images_b64: list[str]) -> list[str]` を実装
   - `@app.local_entrypoint()` で `_common.load_input` / `save_output` を使用
2. `evaluation/src/models/modal_runner.py` に `ModalOCRModel` のサブクラスを追加
3. `evaluation/src/models/registry.py` に登録

VLM ベースのモデルは `modal_scripts/_common.py` の `OCR_PROMPT_JA` を使用してプロンプトを統一すること。

## Modal 開発の既知の注意点

- **PaddlePaddle**: CPU 版は oneDNN エラーで動かない。GPU 版を `run_commands` で `--index-url` 指定してインストールする
- **CUDA バージョン**: Modal 上は cu126
- **OpenCV 依存**: `libgl1` の `apt_install` が必要
- **PaddleOCR 3.x**: `predict()` / `res.json["res"]` のネスト構造に注意
- **結果が空になる場合**: 画像サイズ・フォーマット（RGB 変換）を確認

## テスト実行

```bash
# Python (evaluation)
cd evaluation && uv run python -m pytest tests/ -v

# TypeScript (viewer)
cd evaluation/viewer && npx vitest run

# TypeScript (annotation)
cd annotation && npx vitest run
```
