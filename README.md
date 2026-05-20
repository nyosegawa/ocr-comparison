# ocr-comparison

日本語手書き OCR モデルの比較評価フレームワーク。

API ベースの商用モデルから OSS の GPU モデルまで 26 以上の OCR モデルを、3 つの評価指標で統一的に比較できます。アノテーションツール・評価ランナー・結果ビューアの 3 コンポーネントで構成されています。

## 対応モデル

### API モデル（直接呼び出し）

| モデル | name | 備考 |
|--------|------|------|
| Claude 4.7 Opus | `claude-4.7-opus` | Adaptive thinking |
| Claude 4.6 Opus | `claude-4.6-opus` | Adaptive thinking |
| Claude 4.5 Sonnet | `claude-4.5-sonnet` | Extended thinking |
| Gemini 3.1 Pro Preview | `gemini-3.1-pro-preview` | Deep thinking |
| Gemini 3 Flash Preview | `gemini-3-flash-preview` | |
| Gemini 3.1 Flash Lite Preview | `gemini-3.1-flash-lite-preview` | |
| Gemini 3.5 Flash | `gemini-3.5-flash` | |
| GPT-5.5 | `gpt-5.5` | Reasoning effort: high |
| GPT-5.4 | `gpt-5.4` | Reasoning effort: high |
| Google Cloud Vision | `google-cloud-vision` | |
| Azure AI Vision | `azure-vision` | |
| Mistral OCR | `mistral-ocr-latest` | mistral-ocr-latest |
| Qwen VL OCR | `qwen-vl-ocr` | DashScope API |

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
| [GLM-OCR](https://huggingface.co/zai-org/GLM-OCR) | `glm-ocr` | T4 | MIT |
| [NDLOCR v2](https://github.com/ndl-lab/ndlocr_cli) | `ndlocr-v2` | A10G | CC-BY-4.0 |
| [Sarashina2.2-OCR](https://huggingface.co/sbintuitions/sarashina2.2-ocr) | `sarashina-2.2-ocr` | L4 | MIT |
| [Nemotron-OCR-v2](https://huggingface.co/nvidia/nemotron-ocr-v2) | `nemotron-ocr-v2` | L4 | NVIDIA Open Model License |

## 評価結果（日本語手書きメモ 6 枚）

手書きメモ画像 6 枚に対する評価結果です（Hungarian NLS 降順）。詳細な分析と各モデルの出力例は[ブログ記事](https://nyosegawa.github.io/posts/japanese-handwriting-ocr-comparison/)を参照してください。

| Rank | モデル | カテゴリ | NLS | BoC-F1 | CER | Avg Time |
|------|--------|----------|-----|--------|-----|----------|
| 1 | Gemini 3.5 Flash | API | 0.927 | 0.928 | 0.192 | 14.8s |
| 2 | Gemini 3.1 Pro Preview | API | 0.924 | 0.929 | 0.205 | 67.9s |
| 3 | Gemini 3 Flash Preview | API | 0.918 | 0.910 | 0.221 | 18.7s |
| 4 | Gemini 3.1 Flash Lite Preview | API | 0.899 | 0.917 | 0.207 | 13.7s |
| 5 | Claude 4.6 Opus | API | 0.897 | 0.896 | 0.225 | 74.9s |
| 6 | Claude 4.7 Opus | API | 0.858 | 0.883 | 0.276 | 9.5s |
| 7 | YomiToku v0.13.0 | Modal | 0.842 | 0.807 | 0.384 | 20.5s |
| 8 | Azure AI Vision | API | 0.830 | 0.845 | 0.332 | 4.2s |
| 9 | Google Cloud Vision | API | 0.820 | 0.783 | 0.509 | 2.2s |
| 10 | GPT-5.5 | API | 0.755 | 0.830 | 0.301 | 98.1s |
| 11 | GLM-OCR | Modal | 0.738 | 0.792 | 0.387 | 29.7s |
| 12 | Chandra | Modal | 0.734 | 0.780 | 0.361 | 29.2s |
| 13 | olmOCR-2 | Modal | 0.723 | 0.786 | 0.370 | 45.4s |
| 14 | Sarashina2.2-OCR | Modal | 0.717 | 0.727 | 0.450 | 24.7s |
| 15 | GPT-5.4 | API | 0.714 | 0.814 | 0.331 | 123.4s |
| 16 | Qwen VL OCR | API | 0.706 | 0.713 | 0.491 | 17.7s |
| 17 | HunyuanOCR | Modal | 0.698 | 0.754 | 0.367 | 30.3s |
| 18 | Claude 4.5 Sonnet | API | 0.640 | 0.709 | 0.465 | 16.4s |
| 19 | Mistral OCR | API | 0.589 | 0.645 | 0.563 | 7.3s |
| 20 | Nanonets-OCR-s | Modal | 0.557 | 0.597 | 0.615 | 69.1s |
| 21 | DeepSeek-OCR | Modal | 0.446 | 0.530 | 0.671 | 35.4s |
| 22 | NDLOCR-Lite v1.2.1 | Modal | 0.443 | 0.511 | 0.728 | 18.9s |
| 23 | Nemotron-OCR-v2 | Modal | 0.413 | 0.562 | 0.705 | 13.0s |
| 24 | PaddleOCR | Modal | 0.353 | 0.394 | 0.784 | 12.8s |
| 25 | GOT-OCR 2.0 | Modal | 0.194 | 0.250 | 0.888 | 10.2s |
| 26 | NDLOCR v2 | Modal | 0.064 | 0.087 | 0.958 | 28.7s |

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

## 構造化抽出評価 (structured_eval)

活字ビジネス文書（請求書・レシート・名刺）から構造化 JSON を抽出するタスクの評価フレームワークです。詳細は[ブログ記事](https://nyosegawa.github.io/posts/structured-ocr-evaluation/)を参照してください。

### 評価結果（合成データ 30 枚）

| Rank | モデル | Accuracy | Parse | Schema | Avg Time |
|------|--------|----------|-------|--------|----------|
| 1 | claude-4.6-opus | 0.9931 | 100% | 100% | 10.4s |
| 2 | gemini-3-flash-preview | 0.9925 | 100% | 100% | 9.9s |
| 3 | gemini-3.1-pro-preview | 0.9909 | 100% | 100% | 19.4s |
| 4 | gpt-5.4 | 0.9900 | 100% | 100% | 6.9s |
| 5 | claude-4.5-sonnet | 0.9733 | 100% | 100% | 10.0s |

### 使い方

```bash
cd structured_eval

# 環境変数を設定
cp .env.example .env  # ANTHROPIC_API_KEY, GOOGLE_API_KEY, OPENAI_API_KEY

# 利用可能なモデル一覧
uv run python -m src.evaluate list-models

# 全モデルで評価
uv run python -m src.evaluate run

# 特定モデルのみ
uv run python -m src.evaluate run --models claude-4.6-opus gpt-5.4

# 特定の文書タイプのみ
uv run python -m src.evaluate run --types invoice receipt

# 結果の確認
uv run python -m src.evaluate inspect

# 指標の再計算
uv run python -m src.evaluate rescore
```

### データセット生成

Agent Skill `generate-business-doc` で合成データを生成できます。

```bash
# Claude Code で実行
/generate-business-doc              # 各タイプ 3 枚ずつ
/generate-business-doc invoice 5    # 請求書を 5 枚
```

## ライセンス

MIT License - 詳細は [LICENSE](LICENSE) を参照してください。

各 OCR モデルにはそれぞれ固有のライセンスがあります。利用時は対応モデル一覧のライセンス列を確認してください。
