# ocr-comparison

日本語手書き OCR モデルの比較評価フレームワーク。

API ベースの商用モデルから OSS の GPU モデルまで 18 以上の OCR モデルを、3 つの評価指標で統一的に比較できます。アノテーションツール・評価ランナー・結果ビューアの 3 コンポーネントで構成されています。

## 対応モデル

### API モデル（直接呼び出し）

| モデル | name | 備考 |
|--------|------|------|
| Claude 4.6 Opus | `claude-4.6-opus` | Adaptive thinking |
| Claude 4.5 Sonnet | `claude-4.5-sonnet` | Extended thinking |
| Gemini 3.1 Pro Preview | `gemini-3.1-pro-preview` | Deep thinking |
| Gemini 3 Flash Preview | `gemini-3-flash-preview` | |
| Gemini 3.1 Flash Lite Preview | `gemini-3.1-flash-lite-preview` | |
| GPT-5.4 | `gpt-5.4` | Reasoning effort: high |
| Google Cloud Vision | `google-cloud-vision` | |
| Azure AI Vision | `azure-vision` | |

### Modal GPU モデル（[Modal](https://modal.com) 上で実行）

| モデル | name | GPU | ライセンス |
|--------|------|-----|-----------|
| [HunyuanOCR](https://huggingface.co/tencent/HunyuanOCR) | `hunyuan-ocr` | L4 | Apache-2.0 |
| [DeepSeek-OCR](https://huggingface.co/deepseek-ai/DeepSeek-OCR) | `deepseek-ocr` | L4 | MIT |
| [Chandra](https://pypi.org/project/chandra-ocr/) | `chandra` | A100-40GB | Apache-2.0 |
| [Nanonets-OCR-s](https://huggingface.co/nanonets/Nanonets-OCR-s) | `nanonets-ocr-s` | L4 | Apache-2.0 |
| [olmOCR-2](https://huggingface.co/allenai/olmOCR-2-7B-1025-FP8) | `olmocr-2` | L4 | Apache-2.0 |
| [GOT-OCR 2.0](https://huggingface.co/stepfun-ai/GOT-OCR2_0) | `got-ocr-2.0` | T4 | Apache-2.0 |
| [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) | `paddleocr` | T4 | Apache-2.0 |
| [YomiToku](https://github.com/kotaro-kinoshita/yomitoku) | `yomitoku` | T4 | CC-BY-NC-SA-4.0 |
| [NDLOCR-Lite](https://github.com/ndl-lab/ndlocr-lite) | `ndlocr-lite` | CPU | CC-BY-4.0 |
| [NDLOCR v2](https://github.com/ndl-lab/ndlocr_cli) | `ndlocr-v2` | A10G | CC-BY-4.0 |

## 評価指標

3 つの相補的な指標でモデルを評価します。

| 指標 | 説明 | 特性 |
|------|------|------|
| **Hungarian NLS** (primary) | GT 領域ごとに最適な予測行をマッチングし、Normalized Levenshtein Similarity を計算 | 読み順に依存しない |
| **Bag-of-Characters F1** (secondary) | 文字の多重集合で比較。語順・改行を無視 | 純粋な文字認識精度 |
| **NED / CER** (tertiary) | 全文の Normalized Edit Distance と Character Error Rate | 読み順を含む総合品質 |

## ディレクトリ構成

```
ocr-comparison/
├── annotation/              # アノテーションツール (React + Hono)
│   ├── src/client/          #   React フロントエンド
│   ├── src/server/          #   Hono API サーバー
│   ├── scripts/             #   画像前処理 (deskew, shadow removal)
│   └── data/                #   GT アノテーション (JSON)
├── evaluation/              # 評価フレームワーク (Python)
│   ├── src/
│   │   ├── models/          #   OCR モデルアダプタ
│   │   ├── metrics.py       #   3 指標の実装
│   │   ├── evaluate.py      #   CLI ランナー
│   │   └── data.py          #   GT データローダー
│   ├── modal_scripts/       #   Modal GPU スクリプト
│   ├── viewer/              #   結果ビューア (React + Hono)
│   └── tests/               #   テスト
└── research/                # OCR サーベイ資料
```

## セットアップ

### 前提条件

- Python 3.10+
- Node.js 20+
- [uv](https://docs.astral.sh/uv/) (Python パッケージマネージャ)
- [Modal CLI](https://modal.com/docs/guide) (GPU モデルを使う場合)

### インストール

```bash
# アノテーションツール
cd annotation && npm install

# 評価フレームワーク
cd evaluation && uv sync

# 結果ビューア
cd evaluation/viewer && npm install
```

### 環境変数

```bash
cp evaluation/.env.example evaluation/.env
# .env にAPIキーを設定
```

Modal を使う場合:

```bash
modal token new
```

## 使い方

### 1. アノテーション（正解データ作成）

```bash
cd annotation && npm run dev
# http://localhost:5190 でアノテーションツールが起動
```

画像をアップロードし、バウンディングボックスを描いて正解テキストを入力します。

### 2. 評価実行

```bash
cd evaluation

# 利用可能なモデル一覧
ocr-eval list-models

# 全モデルで評価
ocr-eval run

# 特定モデルのみ
ocr-eval run --models claude-4.6-opus gemini-3.1-pro-preview hunyuan-ocr

# 結果の確認
ocr-eval inspect

# 指標の再計算（指標ロジック変更後）
ocr-eval rescore
```

### 3. 結果ビューア

```bash
cd evaluation/viewer && npm run dev
# http://localhost:5191 でリーダーボードが表示
```

## テスト

```bash
# Python
cd evaluation && uv run python -m pytest tests/ -v

# TypeScript (viewer)
cd evaluation/viewer && npx vitest run

# TypeScript (annotation)
cd annotation && npx vitest run
```

## ライセンス

MIT License - 詳細は [LICENSE](LICENSE) を参照してください。

各 OCR モデルにはそれぞれ固有のライセンスがあります。利用時は対応モデル一覧のライセンス列を確認してください。
