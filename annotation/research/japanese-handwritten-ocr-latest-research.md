# 日本語手書きOCR研究 最新調査レポート（2023-2025年）

調査日: 2026-03-16

---

## 目次

1. [最新arXiv論文で使われているデータセット](#1-最新arxiv論文で使われているデータセット)
2. [LLM/Vision Language Model による手書きOCR評価](#2-llmvision-language-model-による手書きocr評価)
3. [合成データ生成手法](#3-日本語手書きocr用の合成データ生成手法)
4. [Transformer/Attentionベースモデルのベンチマーク](#4-transformerattentionベースモデルのベンチマーク)
5. [産業応用で使われるデータセット](#5-産業応用で使われるデータセット)
6. [日本の研究機関が公開した新しいデータセット](#6-日本の研究機関が公開した新しいデータセット)
7. [Hugging Face等で公開されているデータセット](#7-hugging-face等で公開されているデータセット)
8. [主要OCRエンジン/VLMの比較](#8-主要ocrエンジンvlmの比較)
9. [評価指標まとめ](#9-評価指標まとめ)
10. [今後の課題と研究動向](#10-今後の課題と研究動向)

---

## 1. 最新arXiv論文で使われているデータセット

### 1.1 JSSODa（Japanese Simple Synthetic OCR Dataset）

| 項目 | 内容 |
|------|------|
| **論文タイトル** | Evaluating Multimodal Large Language Models on Vertically Written Japanese Text |
| **著者/機関** | Keito Sasagawa, Shuhei Kurita, Daisuke Kawahara（早稲田大学・国立情報学研究所） |
| **公開日** | 2025年11月 |
| **公開URL** | https://github.com/llm-jp/eval_vertical_ja |
| **HuggingFace** | https://huggingface.co/datasets/llm-jp/JSSODa |
| **arXiv** | https://arxiv.org/html/2511.15059v1 |

**データの特徴:**
- 総画像数: 22,493枚（訓練17,991 / テスト2,256 / 検証2,246）
- LLM（LLM-jp-3.1-instruct）が生成した日本語テキストを画像にレンダリング
- 約200種類の日本語フォントファイルを使用（Pillowライブラリで描画）
- 横書き・縦書きの両方に対応（1〜4カラムレイアウト）
- 平均706文字/画像
- ノイズや歪みなし（意図的に「クリーン」なデータ）

**評価指標と主要結果（縦書きテスト）:**

| モデル | CER（1カラム） | BLEU |
|--------|---------------|------|
| Gemma 3 27B | 7.62 | 91.4 |
| InternVL3 38B | 22.1 | 81.5 |
| Qwen2.5-VL-7B (Fine-tuned) | 0.104〜0.284 | 99.6〜99.8 |
| GPT-4.1 | 記載あり | 記載あり |
| GPT-5 | 記載あり | 記載あり |

### 1.2 VJRODa（Vertical Japanese Real-world OCR Dataset）

| 項目 | 内容 |
|------|------|
| **論文** | 同上（Sasagawa et al., 2025） |
| **公開URL** | https://github.com/llm-jp/eval_vertical_ja |

**データの特徴:**
- 100枚の実世界PDFからの画像
- 国立国会図書館WARPプロジェクトの資料が出典
- 平均1,144文字/画像
- 手動での転写（日本語の読み順に準拠）

**評価結果:**
- Fine-tuningなしではすべてのモデルが低精度
- Qwen2.5-VL-7B（Fine-tuned）: CER 40.5, BLEU 61.1

### 1.3 NDL PDF-Derived OCR Dataset

| 項目 | 内容 |
|------|------|
| **論文タイトル** | Harnessing PDF Data for Improving Japanese Large Multimodal Models |
| **著者/機関** | Jeonghun Baek, Akiko Aizawa, Kiyoharu Aizawa（東京大学・国立情報学研究所） |
| **公開日** | 2025年2月 |
| **arXiv** | https://arxiv.org/html/2502.14778v1 |
| **公開URL** | 論文採択後に公開予定 |

**データの特徴:**
- 国立国会図書館Webアーカイブプロジェクトの約200,000件のPDFから抽出
- 約362,000件のInstruction-tuningサンプルをGPT-4o-miniで生成
- PyMuPDF（PDF画像検出）、Surya（レイアウト解析・OCR）、Japanese-Cloob（意味的類似度マッチング）を使用
- 約300,000件のフィルタリング済み画像テキストペア

**評価指標と結果:**
- LLM-as-a-judge方式（GPT-4の回答品質に対する割合）
- Heron-Benchで最大13.8%改善
- LLaVA1.5-Swallow (8B): JA-LLaVA-Bench (Wild) で65.8%（従来最高を9.4%上回る）

### 1.4 Handwritten Text Recognition Survey (2025)

| 項目 | 内容 |
|------|------|
| **論文タイトル** | Handwritten Text Recognition: A Survey |
| **arXiv** | https://arxiv.org/abs/2502.08417 |
| **公開日** | 2025年2月 |

**備考:** ラテン文字系が中心であり、日本語/CJK文字認識の専用セクションは限定的。ただし、手書き認識全般のSOTA手法（TrOCR、DLoRA-TrOCR等）のレビューとして参考になる。

---

## 2. LLM/Vision Language Model による手書きOCR評価

### 2.1 縦書き日本語テキスト評価（Sasagawa et al., 2025）

**テスト対象モデル:**

| カテゴリ | モデル |
|----------|--------|
| オープンソース | Qwen2.5-VL (7B/32B), InternVL3 (8B/38B), Gemma 3 (12B/27B) |
| クローズドソース | GPT-4.1, GPT-5 |
| OCR特化型 | DeepSeek-OCR, PaddleOCR-VL |

**主要な知見:**
- 横書きでは多くのモデルが高精度を達成
- 縦書きでは精度が大幅に低下（特にFine-tuningなし）
- Fine-tuned Qwen2.5-VL-7BがCER 0.1%以下を達成（合成データ使用時）
- 実世界データ（VJRODa）ではFine-tuning後でもCER 40.5%と課題が残る

**ソース:** https://arxiv.org/html/2511.15059v1

### 2.2 Video OCR Benchmark（VideoDB, 2025）

| 項目 | 内容 |
|------|------|
| **論文** | Benchmarking Vision-Language Models on OCR in Dynamic Video Environments |
| **arXiv** | https://arxiv.org/abs/2502.06445 |
| **データセット** | 1,477枚のアノテーション付きフレーム |

**モデル比較結果:**
- GPT-4o: 全ドメインで65-80%の精度、法律/教育コンテンツで最大84%
- 手書きテキストでは全モデルが苦戦
- Claude: "BASE"を"Baseline"と誤認識
- Gemini: 文字の読み違いあり
- VLMは伝統的OCRより手書き認識で優位

### 2.3 OmniDocBench（CVPR 2025）でのVLM比較

| 項目 | 内容 |
|------|------|
| **ベンチマーク** | OmniDocBench v1.5 |
| **論文** | https://arxiv.org/html/2412.07626v1 |
| **HuggingFace** | https://huggingface.co/datasets/opendatalab/OmniDocBench |

**OCR Edit Distance（低いほど良い）:**

| モデル | スコア |
|--------|--------|
| GPT-4o | 0.02（最優秀） |
| Gemini 3 Pro | 0.115 |
| Claude Sonnet 4.5 | 0.145 |
| GPT-5.1 | 0.147 |

**特徴:**
- 1,355 PDFページ、9種類の文書タイプ
- 日本語を含む109言語対応
- 手書き・印刷テキストの両方を評価
- End-to-End / 単一モジュール / 属性ベースの3レベル評価

### 2.4 OCRBench v2（2025年1月）

| 項目 | 内容 |
|------|------|
| **論文** | OCRBench v2: An Improved Benchmark for Evaluating Large Multimodal Models on Visual Text Localization and Reasoning |
| **arXiv** | https://arxiv.org/abs/2501.00321 |
| **GitHub** | https://github.com/Yuliang-Liu/MultimodalOCR |

**特徴:**
- 10,000件の人手検証済みQAペア
- 31種類の多様なシナリオ
- **英語・中国語のバイリンガル（日本語は未対応）**
- 手書きコンテンツ抽出タスクを含む
- ほとんどのLMMが50/100以下のスコア

### 2.5 日本語OCRにおけるVLMの実践的知見（2024年時点）

**Azure AI Vision:**
- 2024年8月時点で日本語読み取り率最高との評価
- PCで作成されたPDFは精度100%

**Google Cloud Vision API:**
- 日本語歴史資料（縦書き・旧字あり）での実績
- ABBYY FineReaderと並ぶ最適解との評価

**生成AI（GPT-4V, Claude 3, Gemini）の限界:**
- 画像全体の理解力は高いが、精密なOCR処理に限界
- OCRエンジン + 生成AIの組み合わせが推奨される構成

**ソース:** https://note.com/japanmarketing/n/nc7182b94a5e7

---

## 3. 日本語手書きOCR用の合成データ生成手法

### 3.1 JSSODaの合成データ生成パイプライン

| 項目 | 詳細 |
|------|------|
| **テキスト生成** | LLM-jp-3.1-instruct（名詞プロンプトで段落規模のテキスト生成） |
| **画像レンダリング** | Pillowライブラリ、白背景上にテキスト描画 |
| **フォント** | 約200種類の日本語フォントファイル |
| **レイアウト** | 1-4カラム、横書き/縦書き |
| **特徴** | ノイズ・歪みなし（クリーンデータ） |
| **テキスト長** | 100〜3,000文字 |

**ソース:** https://github.com/llm-jp/eval_vertical_ja

### 3.2 PDFベースの半合成データ生成（Baek et al., 2025）

| 項目 | 詳細 |
|------|------|
| **ソースデータ** | 国立国会図書館のPDFコーパス（約200,000件） |
| **レイアウト解析** | Surya（90+言語対応） |
| **画像検出** | PyMuPDF |
| **視覚言語マッチング** | Japanese-Cloob |
| **NSFW/PII フィルタ** | GPT-4o-mini |
| **出力** | 362,000件のInstruction-tuningペア |

### 3.3 Manga OCRの合成データ生成

| 項目 | 詳細 |
|------|------|
| **プロジェクト** | manga-ocr (kha-white) |
| **手法** | マンガ風の合成画像テキストペア生成 |
| **参照データ** | Manga109-sデータセット（テキスト長分布計算用） |
| **特徴** | ルビ（ふりがな）、画像上のテキスト、多様なフォントスタイル対応 |
| **GitHub** | https://github.com/kha-white/manga-ocr/tree/master/manga_ocr_dev/synthetic_data_generator |

### 3.4 手書き合成の最新動向（GAN/Diffusion Model）

**GAN ベースの手法:**
- 手書き合成研究の60%以上がGAN基盤
- HiGAN+: Disentangled Representationsを用いた手書き模倣GAN
- HandDiff-GAN (NLPCC 2025): Diffusion強化型GAN

**Diffusion Model ベースの手法:**
- One-DM (ECCV 2024): One-shot Diffusion Mimickerによる手書きテキスト生成
- Zero-Shot Paragraph-level Handwriting Imitation with Latent Diffusion Models (IJCV 2025)
- Diff-Writer (2023): Diffusion Modelベースの中国語手書き文字生成器（日本語漢字との類似性から参照可能）

**サーベイ論文:** "A survey of handwriting synthesis from 2019 to 2024: A comprehensive review" (Pattern Recognition, 2025)
- ソース: https://www.sciencedirect.com/science/article/pii/S0031320325000172

**課題:** 日本語手書きに特化したGAN/Diffusionモデルの研究はまだ限定的。中国語手書き生成の技術が参考になるが、ひらがな・カタカナ・漢字の混在する日本語特有の課題への対応が必要。

---

## 4. Transformer/Attentionベースモデルのベンチマーク

### 4.1 TrOCR（Transformer-based OCR）

| 項目 | 内容 |
|------|------|
| **開発元** | Microsoft |
| **アーキテクチャ** | Vision Encoder-Decoder (ViT + Transformer Decoder) |
| **arXiv** | https://arxiv.org/abs/2109.10282 |

**最新の改良 (2024-2025):**
- DLoRA-TrOCR: パラメータの約0.6%のみ更新で同等以上の精度
- CER 7.56%（IAM Handwriting Database, TrOCR-BASE）
- **日本語への適用**: 明確なFine-tuning事例は未確認だが、モデルアーキテクチャとしては多言語拡張が可能

### 4.2 Qwen2.5-VL（Alibaba）

| 項目 | 内容 |
|------|------|
| **リリース日** | 2025年1月28日 |
| **対応言語** | 32言語（日本語含む） |
| **サイズ** | 7B / 32B / 72B |

**日本語縦書きOCR結果（Fine-tuning後）:**
- JSSODa: CER 0.104%〜0.284%, BLEU 99.6〜99.8
- VJRODa: CER 40.5%, BLEU 61.1

### 4.3 InternVL3（OpenGVLab）

| 項目 | 内容 |
|------|------|
| **サイズ** | 8B / 38B |
| **特徴** | 汎用文書理解・マルチモーダル推論に最適化 |

**日本語縦書きOCR結果:**
- JSSODa (1カラム): CER 22.1, BLEU 81.5（38Bモデル）

### 4.4 PaddleOCR-VL（Baidu）

| 項目 | 内容 |
|------|------|
| **最新版** | PP-OCRv5 |
| **パラメータ数** | 0.07B（軽量）/ 0.9B / 7B |
| **対応言語** | 100+言語（日本語含む） |
| **HuggingFace** | https://huggingface.co/blog/baidu/ppocrv5 |

**性能:**
- OmniDocBench最高スコア: 92.86（7Bモデル）
- PP-OCRv4比で全体+13ポイント改善
- 手書き・縦書き・日本語で大幅改善
- 処理速度: 370+文字/秒（CPU）
- GPT-4o, Gemini 2.5 Pro, Qwen2.5-VLを上回る（OCR特化タスクにおいて）

### 4.5 Manga OCR

| 項目 | 内容 |
|------|------|
| **開発者** | kha-white |
| **アーキテクチャ** | Vision Encoder Decoder |
| **GitHub** | https://github.com/kha-white/manga-ocr |
| **HuggingFace** | https://huggingface.co/kha-white/manga-ocr-base |

**特徴:**
- 日本語マンガテキストに特化
- 複数行テキストの一括認識
- 縦書き・横書き・ルビ対応
- CER約14.4%（MangaOCR実装での報告値）
- **手書き文字は非対応**（印刷テキスト向け）

### 4.6 従来のベンチマークデータセット

#### KMNIST（Kuzushiji-MNIST）

| データセット | クラス数 | 画像サイズ | 画像数 |
|-------------|---------|-----------|--------|
| Kuzushiji-MNIST | 10 | 28x28 | 70,000 |
| Kuzushiji-49 | 49 | 28x28 | 270,912 |
| Kuzushiji-Kanji | 3,832 | 64x64 | 140,424 |

- **公開元:** ROIS-DS CODH
- **URL:** https://codh.rois.ac.jp/kmnist/
- **GitHub:** https://github.com/rois-codh/kmnist
- **最終更新:** 2025年8月19日

#### ETL Character Database（AIST）

| 項目 | 内容 |
|------|------|
| **総画像数** | 約1,200,000枚 |
| **文字種** | ひらがな、カタカナ、教育漢字、JIS第1水準漢字、英数字、記号 |
| **画像サイズ** | 60x60, 64x63, 72x76, 128x127 |
| **収集期間** | 1973-1984年 |
| **URL** | https://etlcdb.db.aist.go.jp/ |
| **利用条件** | 研究目的で無料（要申請） |

---

## 5. 産業応用で使われるデータセット

### 5.1 Japanese-Mobile-Receipt-OCR-1.3K

| 項目 | 内容 |
|------|------|
| **論文タイトル** | Japanese-Mobile-Receipt-OCR-1.3K: A Comprehensive Dataset Analysis and Fine-tuned VLM for Structured Receipt Data Extraction |
| **公開URL** | https://www.techrxiv.org/users/955537/articles/1324642 |
| **HuggingFace（モデル）** | https://huggingface.co/sabaridsnfuji/Japanese-Receipt-VL-3B-JSON |

**データの特徴:**
- 1,300枚の実世界日本語レシート画像（モバイル撮影）
- 34,727件のテキストエントリ
- 平均トークン長 約9.3（最大255）
- 漢字・仮名・数字の混在

**Fine-tuned モデル:**
1. Japanese-Receipt-VL-3B-JSON: Qwen2.5-VL-3Bベース
2. Japanese-Receipt-VL-lfm2-450M: LiquidAI LFM2-VL-450Mベース

**評価指標:** WER（Word Error Rate）, CER（Character Error Rate）, フィールド命名一貫性, 階層構造精度

### 5.2 日本語請求書OCRデータセット

| 項目 | 内容 |
|------|------|
| **画像数** | 1,000枚 |
| **内訳** | 基本的な仮想編集500枚 + プロフェッショナル編集500枚 |
| **アノテーション** | 会社名、住所、氏名、FAX番号、電話番号 |
| **用途** | 請求書検出・認識・End-to-End OCR |

### 5.3 帳票OCRデータセット

| 項目 | 内容 |
|------|------|
| **画像数** | 9,497枚（10種類のフォーム） |
| **アノテーション** | 矩形バウンディングボックス |
| **用途** | フォーム検出タスク |

### 5.4 医療文書OCR

- 物理検査報告書データセット: 行レベルの矩形バウンディングボックスアノテーション + 転写
- 用途: 検査報告書の検出・認識

### 5.5 住所認識

- CEDAR JOCR: 264枚のスキャン文書から約180,000枚のラベル付き文字画像（3,354文字カテゴリ）
- 住所認識精度: 3,500枚以上の画像で83.68%
- 辞書: 111,000フレーズ以上
- **URL:** https://cedar.buffalo.edu/japanese/JOCRdatabase.html

### 5.6 YomiToku（産業向け日本語OCRエンジン）

| 項目 | 内容 |
|------|------|
| **開発者** | Kotaro Kinoshita |
| **GitHub** | https://github.com/kotaro-kinoshita/yomitoku |
| **PyPI** | https://pypi.org/project/yomitoku/ |
| **ライセンス** | CC BY-SA 4.0 |

**特徴:**
- 日本語文書画像解析に特化したPythonパッケージ
- 7,000文字以上の日本語文字認識
- 4つの専用AIモデル: テキスト検出、テキスト認識、レイアウト解析、表構造認識
- v0.8.0 (2025年4月): 手書き文字認識対応
- v0.10.1 (2025年11月): GPU不要のCPU推論モデル
- 出力形式: HTML, Markdown, JSON, CSV, 検索可能PDF
- AWS Marketplace版（YomiToku-Pro）あり
- **正式なベンチマークスコアは未公開**

---

## 6. 日本の研究機関が公開した新しいデータセット

### 6.1 国立国会図書館（NDL）

#### NDLOCR-Lite（2026年2月24日公開）

| 項目 | 内容 |
|------|------|
| **GitHub** | https://github.com/ndl-lab/ndlocr-lite |
| **ライセンス** | CC BY 4.0 |
| **特徴** | GPU不要の軽量OCR、Windows/Mac/Ubuntu対応 |
| **手書き対応** | 英文・手書き文字に「実験的に対応」 |

#### NDL古典籍OCR-Lite（2024年11月26日公開）

| 項目 | 内容 |
|------|------|
| **特徴** | 江戸期以前の和古書・清代以前の漢籍のくずし字OCR |
| **環境** | 一般的なノートPCで動作 |

#### NDL OCR学習用データセット

| 項目 | 内容 |
|------|------|
| **GitHub** | https://github.com/ndl-lab/pdmocrdataset-part2 |
| **ライセンス** | CC BY 4.0 |
| **画像数** | 3,997枚（2022年4月時点） |
| **内容** | 著作権保護期間満了資料から作成、「手書き」属性を含むインライン情報 |
| **委託先** | 株式会社モルフォAIソリューションズ |

### 6.2 LLM-jp（NII関連プロジェクト）

#### JSSODa / VJRODa

- 前述（セクション1.1, 1.2）
- NII所属の研究者が主導
- GitHub: https://github.com/llm-jp/eval_vertical_ja

### 6.3 ROIS-DS CODH

#### KMNISTデータセット（継続運用中）

- 前述（セクション4.6）
- miwoアプリ: くずし字AI認識アプリ、3,176,251枚の画像を処理済み（2025年11月時点）
- **URL:** https://codh.rois.ac.jp/miwo/

### 6.4 AIST ETL Character Database（継続運用中）

- 前述（セクション4.6）
- 1973-1984年のデータだが、現在もダウンロード提供中
- **URL:** https://etlcdb.db.aist.go.jp/

### 6.5 東京大学（Baek et al.）

- NDL PDFコーパスを活用したVLM学習用データセット
- 前述（セクション1.3）

---

## 7. Hugging Face等で公開されているデータセット

### 7.1 llm-jp/JSSODa

| 項目 | 内容 |
|------|------|
| **URL** | https://huggingface.co/datasets/llm-jp/JSSODa |
| **内容** | LLM生成日本語テキストの合成OCRデータセット |
| **用途** | 縦書き/横書き日本語OCR評価 |

### 7.2 Nexdata/Handwriting_OCR_Data_of_Japanese_and_Korean

| 項目 | 内容 |
|------|------|
| **URL** | https://huggingface.co/datasets/Nexdata/Handwriting_OCR_Data_of_Japanese_and_Korean |
| **画像数** | 100人、22,163件の手書きデータ（サンプル版） |
| **Kaggle** | https://www.kaggle.com/datasets/nexdatafrank/handwriting-ocr-data-of-japanese-and-korean |
| **備考** | 完全版は有料 |

### 7.3 kha-white/manga-ocr-base

| 項目 | 内容 |
|------|------|
| **URL** | https://huggingface.co/kha-white/manga-ocr-base |
| **種別** | 学習済みモデル |
| **用途** | 日本語マンガテキストOCR |

### 7.4 sabaridsnfuji/Japanese-Receipt-VL-3B-JSON

| 項目 | 内容 |
|------|------|
| **URL** | https://huggingface.co/sabaridsnfuji/Japanese-Receipt-VL-3B-JSON |
| **種別** | 学習済みモデル（Qwen2.5-VL-3Bベース） |
| **用途** | 日本語レシートOCR・構造化データ抽出 |

### 7.5 sabaridsnfuji/Japanese-Receipt-VL-lfm2-450M

| 項目 | 内容 |
|------|------|
| **URL** | https://huggingface.co/sabaridsnfuji/Japanese-Receipt-VL-lfm2-450M |
| **種別** | 学習済みモデル（LiquidAI LFM2-VL-450Mベース） |
| **用途** | 軽量日本語レシートOCR |

### 7.6 LT8/Kanji_ETL9G

| 項目 | 内容 |
|------|------|
| **URL** | https://huggingface.co/LT8/Kanji_ETL9G |
| **種別** | ETL9Gデータセットの漢字部分 |

### 7.7 PaddlePaddle/PaddleOCR-VL

| 項目 | 内容 |
|------|------|
| **URL** | https://huggingface.co/PaddlePaddle/PaddleOCR-VL |
| **種別** | OCR-VLモデル（日本語対応） |

### 7.8 opendatalab/OmniDocBench

| 項目 | 内容 |
|------|------|
| **URL** | https://huggingface.co/datasets/opendatalab/OmniDocBench |
| **種別** | 文書解析ベンチマーク（日本語含む109言語対応） |

### 7.9 Kaggle: Handwriting OCR Data of Japanese and Korean

| 項目 | 内容 |
|------|------|
| **URL** | https://www.kaggle.com/datasets/nexdatafrank/handwriting-ocr-data-of-japanese-and-korean |
| **画像数** | 71,535枚 |
| **公開日** | 2023年10月 |

### 7.10 Kaggle: OCR image data of Japanese documents

| 項目 | 内容 |
|------|------|
| **URL** | https://www.kaggle.com/datasets/appenlimited/ocr-image-data-of-japanese-documents |
| **種別** | 日本語文書OCRデータ |

### 7.11 Nexdata 商用データセット

| データセット | 画像数 | 内容 |
|-------------|--------|------|
| 5,147 Images Japanese Handwriting OCR | 5,147 | A4紙、罫線紙、方眼紙上の手書き |
| 101 People Japanese Handwriting OCR | 4,538 | 101人による手書き（多分野） |

- **URL:** https://www.nexdata.ai/datasets/ocr/1296
- **GitHub:** https://github.com/Nexdata-AI/5147-Images-Japanese-Handwriting-OCR-data

---

## 8. 主要OCRエンジン/VLMの比較

### 8.1 日本語手書きOCR実践比較（2024年時点）

| エンジン | 印字文書精度 | 手書き精度 | 備考 |
|---------|------------|-----------|------|
| Tesseract | 不十分 | 精度が出ない | レガシー、LSTM基盤 |
| EasyOCR | 実用的 | 検出可能だが誤認識多い | CNN/RNN |
| PaddleOCR | EasyOCR同等 | 良くない | DBNet/CRNN |
| Azure Document Intelligence | 非常に高精度 | 記載なし | クラウドサービス |
| TrOCR | 英語で実行可能 | 単一行で機能 | Transformer |

**ソース:** https://zenn.dev/starai/articles/8f99d760acfe34

### 8.2 最新OCRモデルランキング（2025-2026）

| モデル | OmniDocBench | パラメータ | ライセンス |
|--------|-------------|-----------|----------|
| PaddleOCR-VL 7B | 92.86 | 7B | Apache 2.0 |
| MinerU 2.5 | 90.67 | - | AGPL-3.0 |
| dots.ocr 3B | 88.41 | 3B | Apache 2.0 |
| Gemini 2.5 Pro | 88.03 | - | API |
| PaddleOCR-VL 0.9B | 92.56 | 0.9B | Apache 2.0 |

**ソース:** https://www.codesota.com/ocr

### 8.3 DeepSeek-OCR（2025年10月リリース）

| 項目 | 内容 |
|------|------|
| **特徴** | Vision-Language方式、100言語対応 |
| **日本語** | CJK対応済み |
| **手書き** | コア機能ではない、専用ツールに劣る |
| **問題点** | 手書きで幻覚生成やテキストスキップが発生 |

**ソース:** https://skywork.ai/blog/llm/deepseek-ocr-for-handwriting-recognition-accuracy-test-and-tips/

---

## 9. 評価指標まとめ

### 9.1 文字レベル指標

| 指標 | 説明 | 算出方法 |
|------|------|---------|
| **CER** (Character Error Rate) | 文字レベルの誤り率 | Levenshtein Distance / 正解文字数 |
| **BLEU** (character-level) | 文字レベルのBLEUスコア | SacreBLEU + NFKC正規化 |
| **1-Edit Distance** | 編集距離に基づく精度 | 1 - (Edit Distance / max(len_pred, len_ref)) |

### 9.2 単語/文レベル指標

| 指標 | 説明 |
|------|------|
| **WER** (Word Error Rate) | 単語レベルの誤り率 |
| **BLEU/METEOR** | 文レベルの類似度 |
| **F1スコア** | 情報抽出タスクでの適合率と再現率の調和平均 |

### 9.3 文書レベル指標

| 指標 | 説明 |
|------|------|
| **TEDS** (Tree Edit Distance Similarity) | 表構造認識の精度 |
| **ANLS** (Average Normalized Levenshtein Similarity) | VQAタスクでの正規化類似度 |
| **IoU** (Intersection over Union) | テキスト領域検出精度 |

### 9.4 LLM評価指標

| 指標 | 説明 |
|------|------|
| **LLM-as-a-judge** | GPT-4の回答品質に対する割合で評価 |
| **Heron-Bench** | 日本語特化の視覚言語モデルベンチマーク |
| **JA-LLaVA-Bench** | 日本語版LLaVAベンチマーク（COCO/Wild） |

---

## 10. 今後の課題と研究動向

### 10.1 現状の課題

1. **縦書き日本語の認識精度**: Fine-tuningなしでは依然として精度が低い（VJRODaでCER 40%超）
2. **手書き専用ベンチマークの不足**: 日本語手書きに特化した標準的なベンチマークが存在しない
3. **実世界データと合成データのギャップ**: クリーンな合成データではCER 0.1%でも、実世界データでは40%に跳ね上がる
4. **VLMの手書き認識限界**: 生成AI単体では精密なOCR処理に限界があり、OCRエンジンとの組み合わせが推奨される
5. **日本語特有の課題**: ひらがな・カタカナ・漢字の混在、ルビ、旧字体、くずし字への対応
6. **公開データセットの不足**: 研究用の日本語OCRデータセットが限定的（YomiToku開発者のコメント）

### 10.2 研究動向

1. **VLM + OCRエンジンのハイブリッド構成**: Azure OCR + GPT等の組み合わせが実用的
2. **軽量モデルの台頭**: PaddleOCR-VL 0.9B、NDLOCR-Lite等のGPU不要モデル
3. **LLMによる合成データ生成**: JSSODaのようなLLMベースの合成パイプラインが増加
4. **Fine-tuningの重要性**: Qwen2.5-VLのFine-tuningでCER 0.1%を達成した事例
5. **産業向けVLM**: レシート、帳票等の特化型モデルの開発が活発
6. **ICDAR 2025**: 非ラテン言語のHTRコンペティション（日本語含む可能性）

### 10.3 推奨される今後の研究方向

- 日本語手書きOCR専用のベンチマークデータセットの構築
- 手書き日本語に特化した合成データ生成モデル（GAN/Diffusion）の開発
- VLMのFine-tuning手法の体系化（特に縦書き・手書き）
- 実世界の多様な文書（医療、法務、行政）への適用評価
- 日本語手書き文字の品質評価メトリクスの標準化

---

## 参考文献・ソースURL一覧

### 論文

1. Sasagawa et al. (2025) "Evaluating MLLMs on Vertically Written Japanese Text" - https://arxiv.org/html/2511.15059v1
2. Baek et al. (2025) "Harnessing PDF Data for Improving Japanese LMMs" - https://arxiv.org/html/2502.14778v1
3. OCRBench v2 (2025) - https://arxiv.org/abs/2501.00321
4. Video OCR Benchmark (2025) - https://arxiv.org/abs/2502.06445
5. OmniDocBench (CVPR 2025) - https://arxiv.org/html/2412.07626v1
6. PaddleOCR 3.0 Technical Report - https://arxiv.org/html/2507.05595v1
7. Handwritten Text Recognition Survey (2025) - https://arxiv.org/abs/2502.08417
8. TrOCR (Microsoft, 2021) - https://arxiv.org/abs/2109.10282
9. Handwriting Synthesis Survey 2019-2024 - https://www.sciencedirect.com/science/article/pii/S0031320325000172

### データセット・リポジトリ

10. JSSODa on HuggingFace - https://huggingface.co/datasets/llm-jp/JSSODa
11. eval_vertical_ja (GitHub) - https://github.com/llm-jp/eval_vertical_ja
12. KMNIST (GitHub) - https://github.com/rois-codh/kmnist
13. KMNIST (CODH) - https://codh.rois.ac.jp/kmnist/
14. ETL Character Database - https://etlcdb.db.aist.go.jp/
15. NDL OCR Dataset - https://github.com/ndl-lab/pdmocrdataset-part2
16. NDLOCR-Lite - https://github.com/ndl-lab/ndlocr-lite
17. Manga OCR - https://github.com/kha-white/manga-ocr
18. Nexdata Japanese Handwriting - https://huggingface.co/datasets/Nexdata/Handwriting_OCR_Data_of_Japanese_and_Korean
19. OmniDocBench on HuggingFace - https://huggingface.co/datasets/opendatalab/OmniDocBench
20. PaddleOCR - https://github.com/PaddlePaddle/PaddleOCR

### ツール・サービス

21. YomiToku - https://github.com/kotaro-kinoshita/yomitoku
22. Japanese-Receipt-VL-3B-JSON - https://huggingface.co/sabaridsnfuji/Japanese-Receipt-VL-3B-JSON
23. PaddleOCR-VL - https://huggingface.co/PaddlePaddle/PaddleOCR-VL
24. OCR Models Benchmark - https://www.codesota.com/ocr

### 日本語情報ソース

25. NDLラボ - https://lab.ndl.go.jp/news/2025/2026-02-24/
26. OCR調査（簡易版） - https://zenn.dev/starai/articles/8f99d760acfe34
27. Azure OCR + 生成AI - https://note.com/japanmarketing/n/nc7182b94a5e7
28. CEDAR JOCR - https://cedar.buffalo.edu/japanese/JOCRdatabase.html
29. Japanese-Mobile-Receipt-OCR-1.3K - https://www.techrxiv.org/users/955537/articles/1324642
30. ICDAR 2025 Competitions - https://www.icdar2025.com/program/competitions
