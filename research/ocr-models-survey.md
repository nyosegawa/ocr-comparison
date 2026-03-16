# OCR モデル・ツール調査レポート

> 調査日: 2026-03-16
> 対象: MEMO.md に記載された既存OCRモデル群 + 追加調査分

---

## 目次

1. [専用OCRモデル（軽量・特化型）](#1-専用ocrモデル軽量特化型)
   - [1.1 NDLOCR](#11-ndlocr)
   - [1.2 NDLOCR-Lite](#12-ndlocr-lite)
   - [1.3 YomiToku](#13-yomitoku)
   - [1.4 PaddleOCR](#14-paddleocr)
   - [1.5 GLM-OCR](#15-glm-ocr)
   - [1.6 HunyuanOCR](#16-hunyuanocr)
   - [1.7 Chandra](#17-chandra)
   - [1.8 DeepSeek-OCR](#18-deepseek-ocr)
   - [1.9 Nanonets-OCR-s](#19-nanonets-ocr-s)
   - [1.10 olmOCR-2](#110-olmocr-2)
   - [1.11 GOT-OCR 2.0](#111-got-ocr-20)
   - [1.12 Mistral OCR 3](#112-mistral-ocr-3)
2. [汎用VLMのOCR活用](#2-汎用vlmのocr活用)
   - [2.1 Qwen3.5-397B-A17B](#21-qwen35-397b-a17b)
   - [2.2 Gemini 3.1 Pro Preview](#22-gemini-31-pro-preview)
   - [2.3 Claude 4.6 Opus](#23-claude-46-opus)
   - [2.4 GPT-5.4 Thinking](#24-gpt-54-thinking)
3. [ベンチマーク横断比較](#3-ベンチマーク横断比較)
4. [参考文献](#4-参考文献)

---

## 1. 専用OCRモデル（軽量・特化型）

### 1.1 NDLOCR

| 項目 | 内容 |
|------|------|
| 開発元 | 国立国会図書館（NDL）/ Morpho AI Solutions（受託開発, FY2021） |
| 最新バージョン | ver.2.1 |
| ライセンス | CC BY 4.0 |
| GPU要件 | **必須**（CUDA 11.1, NVIDIA A10G で検証） |
| 対応言語 | 日本語（活字） |
| リポジトリ | https://github.com/ndl-lab/ndlocr_cli |

#### アーキテクチャ

7つのサブモジュールで構成されるパイプライン型:

1. **ページ分割** (`separate_pages_mmdet`) — MMDetection ベースの見開き分割
2. **傾き補正** (`deskew_HT`) — Hough Transform による回転補正
3. **レイアウト抽出** (`ndl_layout`) — テキスト領域・文書構造の検出
4. **文字認識** (`text_recognition_lightning`) — OCR 本体
5. **読み順認識** (`reading_order`) — テキストの論理的読み順推定
6. **ルビ推定** (`ruby_prediction`) — 漢字のふりがな予測（オプション）
7. **見出し・著者検出** — 文書メタデータ抽出（オプション）

Docker コンテナでデプロイし、各ステージは `-p` オプションで個別実行可能。出力形式は TXT / XML / アノテーション付き画像。

#### 学習データ

パブリックドメインの古典籍2,713画像を含む学習データセットが公開されている [^1]。

#### 備考

- デジタル化資料の全文テキスト化を主目的として開発
- ver.2 ではテキスト音声変換（視覚障害者支援）向けに文字認識精度を改善
- 英語・手書きへの対応は弱い（後継の NDLOCR-Lite で試行的に対応）

[^1]: https://github.com/ndl-lab/pdmocrdataset-part1

> **出典:**
> - [OCR処理プログラム及び学習用データセットの公開について | NDLラボ](https://lab.ndl.go.jp/news/2022/2022-04-25/)
> - [GitHub - ndl-lab/ndlocr_cli](https://github.com/ndl-lab/ndlocr_cli)
> - [国立国会図書館（NDL）、OCR処理プログラム「NDLOCR」ver.2を公開](https://current.ndl.go.jp/car/185098)

---

### 1.2 NDLOCR-Lite

| 項目 | 内容 |
|------|------|
| 開発元 | 国立国会図書館（NDL Lab） |
| 公開日 | 2026-02-24 |
| ライセンス | CC BY 4.0 |
| GPU要件 | **不要**（CPU のみで高速動作、CUDA オプション対応） |
| 対応言語 | 日本語（活字）、英語（試行的）、手書き（試行的） |
| 対応OS | Windows 11, macOS Sequoia (Apple M4), Ubuntu 22.04 |
| リポジトリ | https://github.com/ndl-lab/ndlocr-lite |

#### アーキテクチャ

3つの機能モジュールの組み合わせ:

1. **レイアウト認識** — DEIMv2（"Real-Time Object Detection Meets DINOv3"）
2. **文字列認識** — PARSeq（"Scene text recognition with permuted autoregressive sequence models"）
3. **読み順整列** — NDLOCR 同等の読み順推定

学習は PyTorch で行い、推論は **ONNX 形式**に変換して実行。これによりGPU不要の軽量動作を実現。

#### 機能

- **単一画像処理**: `--sourceimg` で1枚ずつ処理
- **バッチ処理**: `--sourcedir` でディレクトリ内一括処理
- **切り抜きOCR**: 画像内の特定領域を指定してOCR
- **キャプチャモード**: PC画面の任意領域を直接読み取り
- **可視化出力**: 文字検出箇所を青枠で表示（`--viz`）
- 入力: JPG, JPEG, PNG, TIFF, TIF, JP2, BMP
- 出力: XML（座標付き構造化結果）、可視化画像

#### NDLOCR との差分

| 比較項目 | NDLOCR | NDLOCR-Lite |
|----------|--------|-------------|
| GPU | 必須 | 不要 |
| 英語対応 | × | △（試行的） |
| 手書き対応 | × | △（試行的） |
| デスクトップアプリ | × | ○（Windows/Mac） |
| デプロイ | Docker | pip / スタンドアロン |

#### 備考

- 古典籍・くずし字の本格的なデジタル化には「NDL古典籍OCR」または「NDL古典籍OCR-Lite」の使用が推奨されている
- インターネット接続不要でオフライン動作可能

> **出典:**
> - [NDLOCR-Liteの公開について | NDLラボ](https://lab.ndl.go.jp/news/2025/2026-02-24/)
> - [GitHub - ndl-lab/ndlocr-lite](https://github.com/ndl-lab/ndlocr-lite)
> - [NDLOCR-Liteの使い方 | NDLラボ](https://lab.ndl.go.jp/data_set/ndlocrlite-usage/)
> - [GPUなしで動作する軽量なAI OCRツール「NDLOCR-Lite」、国会図書館のラボから無償公開 - 窓の杜](https://forest.watch.impress.co.jp/docs/news/2088188.html)

---

### 1.3 YomiToku

| 項目 | 内容 |
|------|------|
| 開発元 | Kotaro Kinoshita（個人開発） |
| 最新バージョン | v0.10.1（2025-11） |
| ライセンス | CC BY-NC-SA 4.0（非商用無料、商用は別途ライセンス） |
| GPU要件 | 推奨（VRAM 8GB以内）、CPU版あり（v0.10.1〜） |
| 対応言語 | 日本語（特化）、英語 |
| Python | 3.10〜3.13 |
| リポジトリ | https://github.com/kotaro-kinoshita/yomitoku |

#### アーキテクチャ

日本語データセットで学習した4つの専用AIモデルで構成:

1. **テキスト検出** — 文字位置の特定
2. **テキスト認識** — 7,000文字以上の日本語文字認識（縦書き対応）
3. **レイアウト解析** — 文書構造の理解
4. **テーブル構造認識** — セル・グリッドの検出

#### 主な特徴

- **縦書き対応**: 日本語文書特有の縦書きレイアウトをネイティブサポート
- **読み順推定**: 論理的なテキストフロー再構成
- **手書き認識**: v0.8.0（2025-04）で追加
- **CPU推論**: v0.10.1（2025-11）でGPU不要のCPU推論モデル追加（50文字/行制限）
- **出力形式**: HTML, Markdown, JSON, CSV, サーチャブルPDF
- **図表抽出**: 埋め込み画像の個別抽出

#### 商用利用

- AWS Marketplace で YomiToku-Pro として提供（2025-11-10〜）
- オンプレミスライセンスも mlism.com 経由で取得可能

> **出典:**
> - [GitHub - kotaro-kinoshita/yomitoku](https://github.com/kotaro-kinoshita/yomitoku)
> - [日本語に特化したOCR、文書画像解析Pythonパッケージ「YomiToku」を公開しました｜Kotaro.Kinoshita](https://note.com/kotaro_kinoshita/n/n70df91659afc)
> - [日本語に特化したAI OCR「YomiToku」の紹介 - Qiita](https://qiita.com/kanzoo/items/9d382fe4ec991a7eacd2)

---

### 1.4 PaddleOCR

| 項目 | 内容 |
|------|------|
| 開発元 | Baidu（PaddlePaddle） |
| 最新バージョン | v3.4.0（2026-01-29） |
| ライセンス | Apache 2.0 |
| GPU要件 | CPU / GPU / XPU / NPU 対応 |
| 対応言語 | 100言語以上（PP-OCRv5: 日中英含む5種） |
| Python | 3.8〜3.12 |
| GitHub Stars | 60,000+ |
| リポジトリ | https://github.com/PaddlePaddle/PaddleOCR |

#### 主要コンポーネント

**PP-OCRv5**（テキスト認識）:
- PP-OCRv4 比で精度 **+13%**
- 単一モデルで5種類のテキスト対応: 簡体字、繁体字、ピンイン、英語、日本語
- 手書き認識（草書、非標準的な手書き）の改善
- 印鑑認識、チャート→テーブル変換、縦書き文書パースなど

**PP-StructureV3**（文書構造化）:
- PDF/画像を Markdown / JSON に変換
- レイアウト保持で商用ソリューション超え

**PP-ChatOCRv4**（LLM統合）:
- ERNIE 4.5 LLM と統合した情報抽出
- 精度 +15%、文書QA対応

**PaddleOCR-VL 1.5**（VLMベース, 2026-01）:
- 0.9B パラメータの超コンパクト Vision-Language Model
- **OmniDocBench v1.5: 94.5%**
- 111言語対応
- 不規則形状バウンディングボックス検出（曲がったテキスト対応）
- 統合テキストスポッティング・印鑑認識
- ERNIE-4.5-0.3B 言語モデル + 動的解像度ビジュアルエンコーダ

#### バージョン系譜

| バージョン | 公開時期 | 主な改善 |
|-----------|---------|---------|
| PP-OCRv5 | 2025-05 | 5文字種統合、精度+13% |
| PaddleOCR-VL 0.9B | 2025-10 | VLMベース文書パース、109言語 |
| PaddleOCR-VL 1.5 | 2026-01 | 不規則テキスト検出、印鑑認識、94.5% OmniDocBench |

> **出典:**
> - [GitHub - PaddlePaddle/PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
> - [PaddleOCR-VL: Boosting Multilingual Document Parsing via a 0.9B Ultra-Compact Vision-Language Model | ERNIE Blog](https://ernie.baidu.com/blog/posts/paddleocr-vl/)
> - [PaddleOCR Guide 2026: PP-OCRv3, v4, v5 for Developers](https://www.tenorshare.com/ocr/paddleocr.html)

---

### 1.5 GLM-OCR

| 項目 | 内容 |
|------|------|
| 開発元 | Zhipu AI（智譜AI） |
| 公開日 | 2026-02 |
| パラメータ数 | **0.9B**（CogViT 0.4B + GLM-0.5B） |
| ライセンス | コード: Apache 2.0, モデル: MIT |
| GPU要件 | 推論: vLLM/SGLang/Ollama（Apple Silicon MLX 対応） |
| リポジトリ | https://github.com/zai-org/GLM-OCR |

#### アーキテクチャ

GLM-V エンコーダ・デコーダアーキテクチャ:

1. **ビジュアルエンコーダ**: CogViT（0.4B, 大規模画像テキストデータで事前学習）
2. **クロスモーダルコネクタ**: 軽量設計、効率的トークンダウンサンプリング
3. **言語デコーダ**: GLM-0.5B

推論パイプラインは2段構成:
1. **PP-DocLayout-V3** によるレイアウト解析
2. 領域ごとの**並列認識**

#### 技術的革新

- **Multi-Token Prediction (MTP) Loss**: 学習効率・認識精度・汎化性能の向上
- **安定的フルタスク強化学習**: 全タスク横断の RL 学習

#### ベンチマーク

| ベンチマーク | スコア |
|-------------|--------|
| **OmniDocBench V1.5** | **94.62**（1位） |
| OCRBench (Text) | 94.0 |
| UniMERNet（数式） | 96.5 |
| PubTabNet（テーブル） | 85.2 |
| TEDS_TEST | 86.0 |
| Nanonets-KIE | 93.7 |
| Handwritten-KIE | 86.1 |

#### 対応タスク

- 文書OCR・テキスト抽出
- テーブル認識・抽出
- 数式認識
- 構造化文書からの情報抽出（KIE）
- レイアウト解析・領域検出
- 印鑑認識
- コードを含む文書処理

#### デプロイ方法

1. **Zhipu MaaS API** — クラウド、GPU不要
2. **vLLM/SGLang** — セルフホスト、推測デコーディング対応
3. **Ollama/MLX** — エッジデプロイ、Apple Silicon 最適化

> **出典:**
> - [GitHub - zai-org/GLM-OCR](https://github.com/zai-org/GLM-OCR)
> - [GLM-OCR: Z.ai's 0.9B Model Takes the Top Spot on Document Understanding Benchmarks](https://rits.shanghai.nyu.edu/ai/glm-ocr-z-ais-0-9b-model-takes-the-top-spot-on-document-understanding-benchmarks)
> - [Zhipu Launches 0.9B Lightweight GLM-OCR - AIBase](https://news.aibase.com/news/25178)
> - [Zhipu AI Introduces GLM-OCR - MarkTechPost](https://www.marktechpost.com/2026/03/15/zhipu-ai-introduces-glm-ocr-a-0-9b-multimodal-ocr-model-for-document-parsing-and-key-information-extraction-kie/)

---

### 1.6 HunyuanOCR

| 項目 | 内容 |
|------|------|
| 開発元 | Tencent Hunyuan |
| 公開日 | 2025-11 |
| パラメータ数 | **1B** |
| ディスク容量 | 6GB |
| GPU VRAM | 20GB（vLLM） |
| ライセンス | 独自ライセンス（License.txt） |
| 対応言語 | 100言語以上 |
| リポジトリ | https://github.com/Tencent-Hunyuan/HunyuanOCR |
| 論文 | https://arxiv.org/abs/2511.19575 |

#### アーキテクチャ

完全 End-to-End パラダイム（レイアウト解析等の前処理モジュール不要）:

1. **ビジョンエンコーダ**: SigLIP-v2-400M ベースの Native Vision Transformer (ViT)
   - 任意入力解像度対応（アダプティブパッチング、アスペクト比保持）
2. **アダプティブビジュアルアダプタ**: MLP アダプタ
3. **言語モデル**: 軽量 Hunyuan LLM

#### 技術的革新

- **純粋 End-to-End**: 前処理モジュール依存を排除し、エラー伝播を低減
- **データ駆動 + 強化学習**: RL 戦略によりOCRタスクの大幅な性能向上
  - OmniDocBench パース精度: 92.5% → **94.1%**（RL後）
- **ICDAR 2025 DIMT Challenge**: Small Model Track で**1位**獲得

#### ベンチマーク

| タスク | スコア |
|--------|--------|
| テキストスポッティング（総合） | 70.92% |
| OmniDocBench（文書パース） | **94.10%**（ED 0.042） |
| 数式認識 | 94.73% |
| テーブル認識 | 91.81% |
| カード情報抽出 | 92.29% |
| レシート情報抽出 | 92.53% |
| 動画字幕認識 | 92.87% |

#### 対応タスク

- テキストスポッティング（検出+認識）
- 文書パース（Markdown出力）
- 情報抽出（カード、レシート）
- 動画字幕抽出
- テキスト中心VQA
- 多言語認識・翻訳

> **出典:**
> - [GitHub - Tencent-Hunyuan/HunyuanOCR](https://github.com/Tencent-Hunyuan/HunyuanOCR)
> - [HunyuanOCR Technical Report (arXiv:2511.19575)](https://arxiv.org/abs/2511.19575)
> - [Tencent Hunyuan Releases HunyuanOCR - MarkTechPost](https://www.marktechpost.com/2025/11/26/tencent-hunyuan-releases-hunyuanocr-a-1b-parameter-end-to-end-ocr-expert-vlm/)

---

### 1.7 Chandra

| 項目 | 内容 |
|------|------|
| 開発元 | Datalab |
| ベースモデル | Qwen3 VL（Vision-Language Model） |
| ライセンス | コード: Apache 2.0, モデル: Modified OpenRAIL-M |
| GPU要件 | HuggingFace推論 or vLLMサーバー |
| 対応言語 | 40言語以上 |
| GitHub Stars | 4,900+ |
| リポジトリ | https://github.com/datalab-to/chandra |

#### 概要

複雑な文書処理に特化したOCRモデル。手書き、テーブル、数式、フォームをレイアウト保持しつつ処理。

#### 主な機能

- **手書き認識**: 草書、記入済みフォーム、宿題等
- **テーブル構造保持**: 結合セル対応
- **数式認識**: LaTeX 出力
- **フォーム再構成**: チェックボックス、ラジオボタン
- **複雑レイアウト**: 多段組み、新聞、教科書
- **バウンディングボックス座標**: 全要素にレイアウトメタデータ付与

#### 出力形式

- Markdown（レイアウトメタデータ付き）
- HTML（バウンディングボックス付き）
- JSON（座標付き）
- 画像抽出

#### デプロイ

```bash
pip install chandra-ocr
chandra input.pdf ./output --method hf    # HuggingFace推論
chandra input.pdf ./output --method vllm  # vLLM推論
```

- `--page-range`: ページ指定
- `--max-output-tokens`: 出力長制御
- `--include-images / --no-images`: 画像抽出切替

#### 商用利用

- 研究・個人利用・資金調達/売上$2M未満のスタートアップ: 無料
- 商用ライセンス: datalab.to 経由
- ホステッドAPI・無料Playground: datalab.to で提供

#### LayerX評価での結果

| 項目 | 評価 |
|------|------|
| 日本語認識 | Excellent |
| 縦書き | Excellent |
| 図表認識 | Excellent |
| テーブル構造 | Good |

> **出典:**
> - [GitHub - datalab-to/chandra](https://github.com/datalab-to/chandra)
> - [LayerX Tech Blog - OCR Technology Evolution](https://tech.layerx.co.jp/entry/2025/12/01/161913)

---

### 1.8 DeepSeek-OCR

| 項目 | 内容 |
|------|------|
| 開発元 | DeepSeek AI |
| バージョン | DeepSeek-OCR (v1: 2025-10), DeepSeek-OCR-2 (2026-01-27) |
| パラメータ数 | 3B（MoE） |
| ライセンス | MIT |
| リポジトリ | https://github.com/deepseek-ai/DeepSeek-OCR |
| 論文 | https://arxiv.org/abs/2510.18234 |
| HuggingFace | https://huggingface.co/deepseek-ai/DeepSeek-OCR |

#### DeepSeek-OCR (v1)

2段階 Transformer ベースの Document AI:

**Stage 1**: ビジョンエンコーダ
- Windowed SAM Vision Transformer + Dense CLIP-Large エンコーダ
- 16× 畳み込みコンプレッサで視覚トークンを圧縮

**Stage 2**: MoE 言語モデルデコーダ
- 高解像度文書をコンパクトなビジョントークンに圧縮後、デコード

**解像度モード**:

| モード | 解像度 | ビジョントークン数 |
|--------|--------|-------------------|
| Tiny | 512×512 | 64 |
| Small | 640×640 | 100 |
| Base | 1024×1024 | 256 |
| Large | 1280×1280 | 400 |
| **Gundam** | n×640×640 + 1×1024×1024 | 動的 |

**Gundam モード**: 複数ビューの動的タイリングで超高解像度ページ（新聞、設計図等）に対応。800トークン未満で MinerU 2.0（7,000トークン）を上回る性能。

**圧縮性能**: 圧縮比10倍以内で **OCR精度97%**、20倍でも約60%を維持。

#### DeepSeek-OCR-2

2026-01-27公開。3Bパラメータ。

**主な進化**:
- **DeepEncoder V2**: 「Causal Visual Flow」メカニズム — 固定ラスタ順ではなく、セマンティック推論に基づいて画像セグメントを動的に再配置
- **OmniDocBench v1.5: 91.09%**（前世代比+3.73%）
- テキスト抽出だけでなく、視覚的推論による包括的文書理解

**GPU要件**:
- Base: 8〜10GB GPU
- Gundam: 40GB A100 推奨

**推論速度**: A100-40G で vLLM 使用時 ~2,500 tokens/s

> **出典:**
> - [GitHub - deepseek-ai/DeepSeek-OCR](https://github.com/deepseek-ai/DeepSeek-OCR)
> - [DeepSeek-OCR: Contexts Optical Compression (arXiv:2510.18234)](https://arxiv.org/abs/2510.18234)
> - [DeepSeek-OCR 2: Complete Guide - DEV Community](https://dev.to/czmilo/deepseek-ocr-2-complete-guide-to-running-fine-tuning-in-2026-3odb)
> - [DeepSeek OCR 2 - Breaking Benchmarks Records | Proxnox](https://proxnox.github.io/deepseek-ocr-2-benchmarks-and-performances)

---

### 1.9 Nanonets-OCR-s

| 項目 | 内容 |
|------|------|
| 開発元 | Nanonets |
| 公開日 | 2025-10 |
| パラメータ数 | **4B**（ベース: Qwen2.5-VL-3B-Instruct） |
| ライセンス | 非明示（HuggingFaceで公開、698件のfine-tune派生あり） |
| GPU要件 | あり（BF16推論） |
| 対応言語 | 英語（公式記載）※多言語はベースモデル依存 |
| HuggingFace | https://huggingface.co/nanonets/Nanonets-OCR-s |

#### アーキテクチャ

Qwen2.5-VL-3B-Instruct をベースに、文書OCR特化でfine-tuningしたVLM。画像→Markdown変換を主タスクとする。

#### 学習データ

25万ページ以上の文書データで学習:
- 研究論文、金融・法律・医療文書、税務フォーム、レシート・請求書
- 画像・プロット・数式・署名・透かし・チェックボックス・複雑テーブルを含む文書
- 合成データ + 手動アノテーションの2段階学習

#### 主な機能

- LaTeX数式認識（インライン・ディスプレイ）
- 署名検出・分離（`<signature>` タグ）
- 透かし抽出（`<watermark>` タグ）
- チェックボックス → Unicode変換（☐/☑/☒）
- 複雑テーブル抽出（Markdown / HTML）
- ページ番号検出

#### 制限事項

> ⚠️ 公式が「**手書きテキストでは学習していない**」と明言 [^nanonets]
> 多言語サポートの明示的記載もなし。日本語手書きでの使用は要実測。

[^nanonets]: https://nanonets.com/research/nanonets-ocr-s

#### デプロイ

Transformers / vLLM / docext（専用ツール）の3方式。22件の量子化版も利用可能。

> **出典:**
> - [HuggingFace - nanonets/Nanonets-OCR-s](https://huggingface.co/nanonets/Nanonets-OCR-s)
> - [Nanonets Research - Nanonets-OCR-s](https://nanonets.com/research/nanonets-ocr-s)

---

### 1.10 olmOCR-2

| 項目 | 内容 |
|------|------|
| 開発元 | Allen AI (AI2) |
| 公開日 | 2025-10（v0.4.0） |
| パラメータ数 | **7B**（ベース: Qwen2.5-VL-7B, FP8量子化） |
| ライセンス | Apache 2.0 |
| GPU要件 | 12GB VRAM 以上（RTX 4090, L40S, A100, H100 で検証） |
| 対応言語 | 英語（主対象）※多言語の明示的サポートなし |
| リポジトリ | https://github.com/allenai/olmocr |

#### アーキテクチャ

Qwen2.5-VL-7B をベースに、文書→Markdownの変換に特化。単一パスでページ画像を処理し、Markdown（見出し・構造）/ HTML（テーブル）/ LaTeX（数式）を生成。

#### 学習手法

- **評価をユニットテストとして活用**: テーブル構造保持・読み順一貫性を検証する決定的verifierで品質管理
- **GRPO（Group Relative Policy Optimization）**: RL アルゴリズム。文書あたり28件の補完を生成し、より多くのテストに通過したものを報酬
- **olmOCR-synthmix-1025**: 2,186ページ、30,381検証ケースの合成データ（$0.12/ページ）
- **olmOCR-mix-1025**: 270,000ページ（学術論文、法律文書、歴史スキャン）+ 20,000ページの手書き・タイプライター文書

#### ベンチマーク（olmOCR-Bench, 7,000テストケース/1,400文書）

| カテゴリ | スコア |
|---------|--------|
| 総合 | **82.4** |
| 数学スキャン | 82.3 |
| テーブル | 84.9 |
| ヘッダ・フッタ | 96.1 |
| マルチカラム | 83.7 |

#### 処理コスト

FP8量子化により H100 で **3,400 tokens/s**。100万ページ変換で $200未満。

#### 制限事項

> ⚠️ ドキュメントは**英語PDF**にフォーカス。日本語を含む多言語サポートの明示的記載はない。日本語手書きでの使用は要実測。

> **出典:**
> - [GitHub - allenai/olmocr](https://github.com/allenai/olmocr)
> - [olmOCR 2 - Allen AI Blog](https://allenai.org/blog/olmocr-2)

---

### 1.11 GOT-OCR 2.0

| 項目 | 内容 |
|------|------|
| 開発元 | StepFun AI / UCAS（中国科学院大学） |
| 公開日 | 2024-09 |
| パラメータ数 | **580M** |
| ライセンス | コード: Apache 2.0, データ: CC BY-NC 4.0 |
| GPU要件 | CUDA 11.8 + PyTorch 2.0.1、Flash Attention |
| 対応言語 | 英語、中国語（Qwen LLM ベース） |
| リポジトリ | https://github.com/Ucas-HaoranWei/GOT-OCR2.0 |
| HuggingFace | https://huggingface.co/stepfun-ai/GOT-OCR2_0 |

#### アーキテクチャ

**Vary** コードベース上に構築、LLMバックエンドとして **Qwen** を使用したエンコーダ・デコーダ型。統一的なEnd-to-End OCRモデルで以下をサポート:

- **Plain text OCR**: プレーンテキスト抽出
- **Format text OCR**: 構造保持テキスト抽出
- **Fine-grained OCR**: 領域指定の精密認識

#### 手書き学習データ

- CASIA-HWDB2（中国語手書き）
- IAM（英語手書き）
- NorHand-v3（ノルウェー語手書き）

#### 制限事項

> ⚠️ **日本語は未対応**。中国語・英語での手書き対応は確認済みだが、日本語は fine-tuning が必要。パラメータ効率（580M）は fine-tuning のベースラインとして魅力的。

#### 評価ベンチマーク

Fox および OneChart ベンチマークを使用。公式リポジトリにベンチマークデータセットを同梱。

> **出典:**
> - [GitHub - Ucas-HaoranWei/GOT-OCR2.0](https://github.com/Ucas-HaoranWei/GOT-OCR2.0)
> - [HuggingFace - stepfun-ai/GOT-OCR2_0](https://huggingface.co/stepfun-ai/GOT-OCR2_0)

---

### 1.12 Mistral OCR 3

| 項目 | 内容 |
|------|------|
| 開発元 | Mistral AI |
| 公開日 | 2025-12 |
| モデルID | `mistral-ocr-2512` |
| パラメータ数 | 非公開（「競合より大幅に小さい」と記載） |
| ライセンス | プロプライエタリ（API提供、セルフホスティングオプションあり） |
| 料金 | $2/1,000ページ（Batch API: $1/1,000ページ） |

#### 概要

Mistral OCR 2 に対し **74%の総合勝率**を達成した文書→Markdown/HTML 変換モデル。

#### ベンチマーク（内部評価、fuzzy-match）

| タスク | Mistral OCR 3 | Azure AI | AWS Textract |
|--------|:------------:|:--------:|:------------:|
| 手書き認識 | **88.9%** | 78.2% | - |
| テーブル抽出 | **96.6%** | - | 84.8% |

#### 主な機能

- **手書き認識**: 草書、混合アノテーション、印刷フォーム上の手書き
- **フォーム処理**: ボックス、ラベル、密集レイアウト（請求書、領収書、行政文書）
- **スキャン文書**: 圧縮アーティファクト、傾き、歪み、低DPI、ノイズに耐性
- **複雑テーブル**: colspan/rowspan による HTML テーブル再構成
- Document AI Playground（ドラッグ&ドロップ UI）

#### 制限事項

> ⚠️ 「全言語で大幅な改善」と記載されるが、**日本語手書きの個別スコアは未公表**。プロプライエタリAPIのため、オフライン利用はセルフホスト契約が必要。

> **出典:**
> - [Introducing Mistral OCR 3 | Mistral AI](https://mistral.ai/news/mistral-ocr-3)
> - [Mistral OCR 3 Technical Review - PyImageSearch](https://pyimagesearch.com/2025/12/23/mistral-ocr-3-technical-review-sota-document-parsing-at-commodity-pricing/)
> - [Mistral Releases OCR 3 - InfoQ](https://www.infoq.com/news/2026/01/mistral-ocr3/)

---

## 2. 汎用VLMのOCR活用

### 2.1 Qwen3.5-397B-A17B

| 項目 | 内容 |
|------|------|
| 開発元 | Alibaba Cloud / Qwen Team |
| 公開日 | 2026-02-15 |
| パラメータ数 | 397B（17B アクティベート, Sparse MoE） |
| コンテキスト長 | 262,144トークン（YaRN拡張で最大1,010,000） |
| ライセンス | オープンウェイト |
| 対応言語 | 201言語・方言 |
| HuggingFace | https://huggingface.co/Qwen/Qwen3.5-397B-A17B |

#### アーキテクチャ

Hybrid MoE + Vision Encoder の統合マルチモーダルモデル:

- **Hidden Dimension**: 4096
- **レイヤー数**: 60（ハイブリッドレイアウト）
  - 15 × (3 × (Gated DeltaNet → MoE) + 1 × (Gated Attention → MoE))
- **MoE**: 512 エキスパート中 10+1（shared）をアクティベート
- **ビジョン**: Early Fusion で視覚・言語トークンを統合学習
- 画像・動画・文書入力対応

#### OCR関連ベンチマーク

| ベンチマーク | Qwen3.5-397B | Gemini 3 Pro | Claude 4.5 Opus |
|-------------|:------------:|:------------:|:---------------:|
| OCRBench | **93.1** | 90.4 | 85.8 |
| CC-OCR | **82.0** | 79.0 | 76.9 |
| OmniDocBench 1.5 | **90.8** | 88.5 | 87.7 |
| CharXiv | 80.8 | **81.4** | 68.5 |
| MMLongBench-Doc | 61.5 | 60.5 | **61.9** |
| AI2D Test | 93.9 | **94.1** | 87.7 |

#### OCR利用上の特徴

- VLM としてのプロンプトベース OCR（専用OCRパイプラインではない）
- 高解像度画像入力（最大1344×1344）
- Thinking Mode / Instruct Mode の切替可能
- vLLM / SGLang / HuggingFace Transformers でセルフホスト可能

> **出典:**
> - [Hugging Face - Qwen/Qwen3.5-397B-A17B](https://huggingface.co/Qwen/Qwen3.5-397B-A17B)
> - [Qwen3.5: Towards Native Multimodal Agents](https://qwen.ai/blog?id=qwen3.5)
> - https://x.com/hokazuya/status/2023706936886390970

---

### 2.2 Gemini 3.1 Pro Preview

| 項目 | 内容 |
|------|------|
| 開発元 | Google DeepMind |
| 入力モダリティ | テキスト、画像、動画、音声、PDF |
| ライセンス | プロプライエタリ（API提供） |
| コンテキスト長 | 大規模 |

#### OCR・文書理解性能

- **OmniDocBench 1.5**: Edit Distance **0.115**（SOTA — GPT-5.1: 0.147, Claude Sonnet 4.5: 0.145 を上回る）
- **MMMU-Pro**: 80.5%（ツールなし）
- 文書処理パイプライン全体（OCR → 視覚推論）で高い統合性能
- **Media Resolution Control**: ビジュアルトークン使用量を調整し、コスト vs 精度のバランス可能

#### 特徴

- スキャンPDF、画像、音声の混合コーパスに対する統合推論
- トレーサブル出力（アサーションを裏付ける画像/ページ/音声タイムスタンプの指示）
- GENSHI AI評価では Gemini 3/2.5 系は高密度文書で大規模欠落が報告されている点に注意

> **出典:**
> - [Gemini 3.1 Pro — Google DeepMind](https://deepmind.google/models/gemini/pro/)
> - [Abaka AI's OmniDocBench Standardizes Gemini 3's Performance](https://www.abaka.ai/blog/google-gemini-3-validates-omnidocbench)
> - [Gemini 3.1 Pro Complete Guide 2026 | NxCode](https://www.nxcode.io/en/resources/news/gemini-3-1-pro-complete-guide-benchmarks-pricing-api-2026)
> - [GENSHI AI - 医療文書OCR精度検証](https://genshi.ai/articles/ocr-evaluation)

---

### 2.3 Claude 4.6 Opus

| 項目 | 内容 |
|------|------|
| 開発元 | Anthropic |
| 公開日 | 2026-02-05 |
| コンテキスト長 | 1Mトークン |
| ライセンス | プロプライエタリ（API提供） |

#### OCR・文書理解性能

Anthropic公式にはOCR特化のベンチマーク公表がないが、第三者評価で以下が確認されている:

**Qwen3.5 モデルカード記載の比較**（Claude 4.5 Opus 相当）:

| ベンチマーク | スコア |
|-------------|--------|
| OCRBench | 85.8 |
| CC-OCR | 76.9 |
| OmniDocBench 1.5 | 87.7 |

**GENSHI AI 医療文書評価**:
- 高密度文書（退院サマリー等）で **「claude-opus-4-5 のみが実務利用を現実的に検討できる品質」** と評価
- 全文保持・構造安定性が最高評価
- 低〜中密度文書ではモデル選択肢が拡がる

#### 特徴

- 1Mトークンの長コンテキストにより大量文書の一括処理が可能
- 文書、スプレッドシート、プレゼンテーション対応
- MRCR v2（8-needle, 1M context）: 76%

> **出典:**
> - [Introducing Claude Opus 4.6 - Anthropic](https://www.anthropic.com/news/claude-opus-4-6)
> - [Hugging Face - Qwen/Qwen3.5-397B-A17B（比較ベンチマーク）](https://huggingface.co/Qwen/Qwen3.5-397B-A17B)
> - [GENSHI AI - 医療文書OCR精度検証](https://genshi.ai/articles/ocr-evaluation)

---

### 2.4 GPT-5.4 Thinking

| 項目 | 内容 |
|------|------|
| 開発元 | OpenAI |
| 公開日 | 2026-03-05 |
| バリエーション | GPT-5.4, GPT-5.4 Thinking, GPT-5.4 Pro |
| コンテキスト長 | 1Mトークン |
| ライセンス | プロプライエタリ（API提供） |

#### OCR・文書理解性能

- 「密度の高いスキャン、手書きフォーム、工学図面、チャート多用レポート」を**単一パスで解釈・推論可能**
- 従来のOCR+レイアウト検出+カスタムパーサーのパイプラインを不要にする設計思想
- BigLaw Bench（法律文書）: **91%**
- GPT-5.4 Thinking は文書理解でさらに強化

#### 主要パラメータ

| パラメータ | 用途 | 推奨設定 |
|-----------|------|---------|
| `image detail` | 画像解像度制御 | `auto`（標準）/ `original`（手書き・低品質） |
| `verbosity` | 転写の詳細度 | `high`（OCR的なリテラル転写） |
| `reasoning effort` | 推論計算量 | `high`（チャート・テーブル・図表） |
| Code Interpreter | マルチパス検査 | ズーム・クロップ・回転で密な文書に対応 |

#### GENSHI AI評価での位置づけ

- GPT-5.2 は紹介状（大文字）で有力だが、退院サマリー（高密度）では精度低下
- 文字サイズへの依存傾向がある
- GPT-5-nano は大規模欠落や出力なしの結果

> **出典:**
> - [Introducing GPT-5.4 | OpenAI](https://openai.com/index/introducing-gpt-5-4/)
> - [Getting the Most out of GPT-5.4 for Vision and Document Understanding - OpenAI Cookbook](https://developers.openai.com/cookbook/examples/multimodal/document_and_multimodal_understanding_tips)
> - [OpenAI launches GPT-5.4 - TechCrunch](https://techcrunch.com/2026/03/05/openai-launches-gpt-5-4-with-pro-and-thinking-versions/)
> - [GENSHI AI - 医療文書OCR精度検証](https://genshi.ai/articles/ocr-evaluation)

---

## 3. ベンチマーク横断比較

### OmniDocBench v1.5（文書理解総合）

| モデル | パラメータ | スコア | カテゴリ |
|--------|-----------|--------|---------|
| GLM-OCR | 0.9B | **94.62** | 専用OCR |
| PaddleOCR-VL 1.5 | 0.9B | 94.5 | 専用OCR |
| HunyuanOCR | 1B | 94.10 | 専用OCR |
| DeepSeek-OCR-2 | 3B | 91.09 | 専用OCR |
| Qwen3.5-397B-A17B | 17B act. | 90.8 | 汎用VLM |
| Gemini 3 Pro | 非公開 | 88.5* | 汎用VLM |
| Claude 4.5 Opus | 非公開 | 87.7* | 汎用VLM |

*olmOCR-2 は独自ベンチ（olmOCR-Bench）で82.4、OmniDocBench v1.5 のスコアは未公表

*Qwen3.5 モデルカード記載値

### OCRBench（テキスト認識）

| モデル | スコア |
|--------|--------|
| GLM-OCR | 94.0 |
| Qwen3.5-397B-A17B | 93.1 |
| Gemini 3 Pro | 90.4 |
| Claude 4.5 Opus | 85.8 |

### 日本語文書処理能力（LayerX Tech Blog 評価）

| モデル | 日本語認識 | 縦書き | 図表 | テーブル |
|--------|:----------:|:------:|:----:|:-------:|
| Chandra | ◎ | ◎ | ◎ | ○ |
| HunyuanOCR | ◎ | ◎ | △ | ○ |
| YomiToku | ◎ | △ | ○ | ○ |
| PP-OCRv5 | ○ | ◎ | △ | △ |
| PaddleOCR-VL | ○ | × | × | ○ |
| DeepSeek-OCR | × | × | ○ | × |
| Tesseract | × | × | - | - |

◎=Excellent, ○=Good, △=Moderate, ×=Weak

### GENSHI AI 医療文書評価

| モデル | 高密度文書（退院サマリー） | 低〜中密度文書（紹介状） |
|--------|:------------------------:|:----------------------:|
| Claude Opus | **実務レベル唯一** | ○ |
| GPT-5.2 | 精度低下 | 有力候補 |
| Gemini 3/2.5 | 大規模欠落 | 大規模欠落 |
| PaddleOCR (pp_ocr) | 認識不能 | 認識不能 |

### モデル特性まとめ

| モデル | パラメータ | GPU要件 | ライセンス | 日本語 | 手書き | 強み |
|--------|-----------|---------|-----------|:------:|:------:|------|
| NDLOCR | - | 必須 | CC BY 4.0 | ◎ | × | 古典籍・全文テキスト化 |
| NDLOCR-Lite | - | 不要 | CC BY 4.0 | ○ | △ | 軽量・オフライン |
| YomiToku | - | 推奨 | CC BY-NC-SA 4.0 | ◎ | ○ | 日本語特化・縦書き |
| PaddleOCR-VL 1.5 | 0.9B | あり | Apache 2.0 | ○ | ○ | 111言語・高精度 |
| GLM-OCR | 0.9B | あり | MIT | - | ○ | OmniDocBench 1位 |
| HunyuanOCR | 1B | 20GB | 独自 | - | - | End-to-End・100言語 |
| Chandra | - | あり | OpenRAIL-M | ◎ | ◎ | 手書き・複雑レイアウト |
| DeepSeek-OCR-2 | 3B | 8-40GB | MIT | × | - | 視覚圧縮・高速 |
| Nanonets-OCR-s | 4B | あり | 非明示 | ? | ×* | 文書→Markdown特化 |
| olmOCR-2 | 7B | 12GB+ | Apache 2.0 | ? | △ | RL学習・低コスト |
| GOT-OCR 2.0 | 580M | あり | Apache 2.0 | × | ○** | 軽量・FT向きベース |
| Mistral OCR 3 | 非公開 | API | プロプラ | ? | ○ | 手書き88.9%・安価 |
| Qwen3.5-397B | 17B act. | 大規模 | オープン | ○ | - | 最高OCRBench |
| Gemini 3.1 Pro | 非公開 | API | プロプラ | - | - | OmniDocBench ED最良 |
| Claude 4.6 Opus | 非公開 | API | プロプラ | ○ | - | 高密度文書で唯一実務級 |
| GPT-5.4 Thinking | 非公開 | API | プロプラ | - | ○ | 単一パス文書理解 |

\* 公式が「手書きでは学習していない」と明言
\*\* 中国語・英語の手書きのみ。日本語はfine-tuning要
? = 日本語での公式検証なし（ベースモデル経由で部分的に対応の可能性あり）

---

## 4. 参考文献

### 調査で使用した一次ソース

#### NDLOCR / NDLOCR-Lite
1. [OCR処理プログラム及び学習用データセットの公開について | NDLラボ](https://lab.ndl.go.jp/news/2022/2022-04-25/)
2. [NDLOCR-Liteの公開について | NDLラボ](https://lab.ndl.go.jp/news/2025/2026-02-24/)
3. [GitHub - ndl-lab/ndlocr_cli](https://github.com/ndl-lab/ndlocr_cli)
4. [GitHub - ndl-lab/ndlocr-lite](https://github.com/ndl-lab/ndlocr-lite)
5. [NDLOCR-Liteの使い方 | NDLラボ](https://lab.ndl.go.jp/data_set/ndlocrlite-usage/)

#### YomiToku
6. [GitHub - kotaro-kinoshita/yomitoku](https://github.com/kotaro-kinoshita/yomitoku)
7. [日本語に特化したOCR、文書画像解析Pythonパッケージ「YomiToku」を公開しました｜Kotaro.Kinoshita](https://note.com/kotaro_kinoshita/n/n70df91659afc)

#### PaddleOCR
8. [GitHub - PaddlePaddle/PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
9. [PaddleOCR-VL | ERNIE Blog](https://ernie.baidu.com/blog/posts/paddleocr-vl/)

#### GLM-OCR
10. [GitHub - zai-org/GLM-OCR](https://github.com/zai-org/GLM-OCR)
11. [GLM-OCR: Z.ai's 0.9B Model Takes the Top Spot | NYU Shanghai](https://rits.shanghai.nyu.edu/ai/glm-ocr-z-ais-0-9b-model-takes-the-top-spot-on-document-understanding-benchmarks)

#### HunyuanOCR
12. [GitHub - Tencent-Hunyuan/HunyuanOCR](https://github.com/Tencent-Hunyuan/HunyuanOCR)
13. [HunyuanOCR Technical Report (arXiv:2511.19575)](https://arxiv.org/abs/2511.19575)

#### Chandra
14. [GitHub - datalab-to/chandra](https://github.com/datalab-to/chandra)

#### DeepSeek-OCR
15. [GitHub - deepseek-ai/DeepSeek-OCR](https://github.com/deepseek-ai/DeepSeek-OCR)
16. [DeepSeek-OCR: Contexts Optical Compression (arXiv:2510.18234)](https://arxiv.org/abs/2510.18234)
17. [HuggingFace - deepseek-ai/DeepSeek-OCR-2](https://huggingface.co/deepseek-ai/DeepSeek-OCR-2)

#### Qwen3.5
18. [HuggingFace - Qwen/Qwen3.5-397B-A17B](https://huggingface.co/Qwen/Qwen3.5-397B-A17B)

#### Gemini 3.1 Pro
19. [Gemini 3.1 Pro — Google DeepMind](https://deepmind.google/models/gemini/pro/)
20. [Abaka AI OmniDocBench Standardizes Gemini 3's Performance](https://www.abaka.ai/blog/google-gemini-3-validates-omnidocbench)

#### Claude 4.6 Opus
21. [Introducing Claude Opus 4.6 - Anthropic](https://www.anthropic.com/news/claude-opus-4-6)

#### GPT-5.4
22. [Getting the Most out of GPT-5.4 for Vision and Document Understanding - OpenAI Cookbook](https://developers.openai.com/cookbook/examples/multimodal/document_and_multimodal_understanding_tips)

#### Nanonets-OCR-s
23. [HuggingFace - nanonets/Nanonets-OCR-s](https://huggingface.co/nanonets/Nanonets-OCR-s)
24. [Nanonets Research - Nanonets-OCR-s](https://nanonets.com/research/nanonets-ocr-s)

#### olmOCR-2
25. [GitHub - allenai/olmocr](https://github.com/allenai/olmocr)
26. [olmOCR 2 - Allen AI Blog](https://allenai.org/blog/olmocr-2)

#### GOT-OCR 2.0
27. [GitHub - Ucas-HaoranWei/GOT-OCR2.0](https://github.com/Ucas-HaoranWei/GOT-OCR2.0)
28. [HuggingFace - stepfun-ai/GOT-OCR2_0](https://huggingface.co/stepfun-ai/GOT-OCR2_0)

#### Mistral OCR 3
29. [Introducing Mistral OCR 3 | Mistral AI](https://mistral.ai/news/mistral-ocr-3)
30. [Mistral OCR 3 Technical Review - PyImageSearch](https://pyimagesearch.com/2025/12/23/mistral-ocr-3-technical-review-sota-document-parsing-at-commodity-pricing/)

### 第三者評価記事
31. [GENSHI AI - 医療文書OCR精度検証](https://genshi.ai/articles/ocr-evaluation)
32. [LayerX Tech Blog - OCR技術の進化と日本語LLM性能検証](https://tech.layerx.co.jp/entry/2025/12/01/161913)

### SNS参照
33. https://x.com/hokazuya/status/2023706936886390970 （Qwen3.5 OCR関連）
34. https://x.com/Zai_org/status/2018520052941656385 （GLM-OCR関連）
