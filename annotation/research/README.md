# 日本語手書きOCR 評価データセット調査

調査日: 2026-03-16

## 調査概要

日本語手書きOCR用の評価データセットに関する包括的な調査結果をまとめたものです。4つの観点から並列調査を実施し、各レポートに整理しています。

---

## レポート一覧

### 1. [公開データセット一覧](./japanese-handwritten-ocr-datasets.md)

ETL文字データベース、KMNIST、くずし字データセット、HANDS、JEITA-HP、NDL OCRデータセット等、主要な日本語手書きOCR用の公開データセットを網羅的に調査。各データセットの仕様、ライセンス、入手方法、引用情報を整理。

**主要データセット（12カテゴリ）:**
- ETL文字データベース（~120万画像、AIST、非商用無料）
- KMNIST / Kuzushiji-49 / Kuzushiji-Kanji（CC BY-SA 4.0、無料DL）
- 日本古典籍くずし字データセット（108万文字、CC BY-SA 4.0）
- HANDS (Nakayosi/Kuchibue/Kondate)（学術利用、要申請）
- NDL OCR関連データセット群（パブリックドメイン / CC BY 4.0）

### 2. [国際コンペティション・ベンチマーク](./japanese-handwriting-ocr-benchmarks.md)

ICDAR、Kaggle Kuzushiji Recognition等の国際コンペティションで使用されるデータセットと、CASIA、IAM、RIMES等の他言語ベンチマークとの比較。

**主要コンペ・ベンチマーク:**
- ICDAR 2019 RRC-MLT（日本語含む10言語、20,000画像）
- DOST（大阪シーンテキスト、32,147画像、280万文字）
- Kaggle Kuzushiji Recognition（293チーム参加、F1スコア評価）
- CASIA-HWDB（中国語、漢字転移学習に有用）
- IAM / RIMES（英語/仏語、評価方法論の参考）

### 3. [最新研究動向（2023-2025年）](./japanese-handwritten-ocr-latest-research.md)

VLM/Transformerモデルの最新ベンチマーク、合成データ生成手法、産業応用データセット、Hugging Face公開物等を調査。

**主要な知見:**
- JSSODa / VJRODa（早稲田大・NII、2025年、縦書き日本語OCR評価）
- Fine-tuned Qwen2.5-VL-7Bが合成データでCER 0.1%達成（実世界では40.5%）
- PaddleOCR-VL 7BがOmniDocBenchで92.86（総合1位）
- **日本語手書き専用の標準ベンチマークはまだ不在**

### 4. [評価指標・方法論](./ocr-evaluation-metrics.md)

CER/WER等の評価指標、日本語特有の評価課題、検出+認識の統合評価、評価ツール・ライブラリ、Ground Truth作成のベストプラクティスを調査。

**推奨指標:**
| 評価フェーズ | 推奨指標 | 理由 |
|---|---|---|
| 文字認識精度 | CER（正規化版） | 日本語はスペース区切りなし |
| 読み順非依存 | FCA / BoW Error | レイアウト解析エラーの排除 |
| テキスト検出 | Hmean (IoU ≥ 0.5) | ICDAR標準 |
| End-to-End | CLEval F-measure | 検出+認識の統合評価 |

### 5. [アノテーションツール先行事例調査](./existing-tools-survey.md)

（既存の調査。アノテーションシステム構築のためのツール・ライブラリ調査）

---

## 重要な発見: 日本語手書きOCRデータセットの課題

1. **統一ベンチマークの不在**: 英語のIAMやフランス語のRIMESに相当する日本語手書きOCRの統一的標準ベンチマークが存在しない
2. **公開データの不足**: 自由にダウンロード可能な現代日本語手書き文字データは限定的（ETLは1973-1984年収集、くずし字系は古典籍）
3. **合成データと実世界データのギャップ**: クリーンな合成データでCER 0.1%でも、実世界データでは40%超に悪化
4. **旧字体・異体字の評価困難**: Unicode正規化（NFKC）では解決できず、別途変換テーブルが必要
5. **縦書き対応**: 縦書き日本語テキストの認識精度はまだ大きな課題

## 自由にダウンロード可能なデータセット（推奨順）

| データセット | 規模 | ライセンス | 入手URL |
|---|---|---|---|
| KMNIST | 70,000画像 / 10クラス | CC BY-SA 4.0 | https://github.com/rois-codh/kmnist |
| Kuzushiji-49 | 270,912画像 / 49クラス | CC BY-SA 4.0 | 同上 |
| Kuzushiji-Kanji | 140,424画像 / 3,832クラス | CC BY-SA 4.0 | 同上 |
| 日本古典籍くずし字 | 1,086,326文字 / 4,328文字種 | CC BY-SA 4.0 | https://codh.rois.ac.jp/char-shape/ |
| NDL 平仮名73文字 | 80,000画像 | PDM 1.0 | https://github.com/ndl-lab/hiragana_mojigazo |
| NDL 漢字300文字 | 146,157画像 | PDM 1.0 | https://github.com/ndl-lab/kanji_mojigazo |
| ETL文字データベース | ~1,200,000画像 / 3,036クラス | 非商用無料 | https://etlcdb.db.aist.go.jp/ |
