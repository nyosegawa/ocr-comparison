# 手書きOCR（日本語）の評価指標と評価方法論 総合調査

## 目次

1. [文字レベルの評価指標](#1-文字レベルの評価指標)
2. [単語・行レベルの評価指標](#2-単語行レベルの評価指標)
3. [文書レベルの評価指標](#3-文書レベルの評価指標)
4. [日本語特有の評価課題](#4-日本語特有の評価課題)
5. [検出＋認識の統合評価](#5-検出認識の統合評価)
6. [評価ツール・ライブラリ](#6-評価ツールライブラリ)
7. [Ground Truth作成のベストプラクティス](#7-ground-truth作成のベストプラクティス)
8. [最新ベンチマーク動向](#8-最新ベンチマーク動向)

---

## 1. 文字レベルの評価指標

### 1.1 Character Error Rate (CER)

OCR評価で最も基本的かつ広く使われる指標。レーベンシュタイン距離に基づき、Ground Truth（GT）テキストとOCR出力テキスト間の文字レベルの編集距離を測定する。

**計算式:**

```
CER = (S + D + I) / N
```

- `S` = 置換（Substitutions）の数
- `D` = 削除（Deletions）の数
- `I` = 挿入（Insertions）の数
- `N` = GT中の総文字数

**正規化CER（OCR-D方式）:**

```
CER_normalized = (S + D + I) / (S + D + I + C)
```

- `C` = 正解文字数（Correct characters）
- この方式では値が常に0〜100%の範囲に収まる

**特徴:**
- 値が低いほど高精度（0 = 完全一致）
- 挿入が多い場合、100%を超えることがある（例: GT "ABC" に対しOCR出力 "ABC12345" → CER = 166.67%）
- 日本語のようにスペースで単語区切りしない言語では、WERよりCERが適切な指標とされる
- OCR-Dでは「1文字」をUnicodeの書記素クラスタ（grapheme cluster）として技術的に定義している

**出典:**
- [Evaluate OCR Output Quality with CER and WER | Towards Data Science](https://towardsdatascience.com/evaluating-ocr-output-quality-with-character-error-rate-cer-and-word-error-rate-wer-853175297510/)
- [Understanding CER for AI Accuracy | Galileo](https://galileo.ai/blog/character-error-rate-cer-metric)
- [Quality Assurance in OCR-D](https://ocr-d.de/en/spec/ocrd_eval.html)

### 1.2 Character Accuracy (CA)

CERの補指標として使われる。

**計算式:**

```
CA = 1 - CER = (N - S - D - I) / N
```

または正規化版:

```
CA = C / (S + D + I + C)
```

**出典:**
- [Quality Assurance in OCR-D](https://ocr-d.de/en/spec/ocrd_eval.html)

### 1.3 Flexible Character Accuracy (FCA)

CERの重大な欠点（読み順依存性）を克服するために開発された指標。

**特徴:**
- テキストを行・サブ行チャンクに分割し、最大アラインメントを見つけてからペア比較する
- 読み順に依存しない評価が可能
- レイアウト解析のエラーと文字認識エラーを分離できる
- 2017年以降の国際コンペティションで実用されている
- OCR-Dでは将来実装予定の指標として挙げられている

**利点:**
- テキストブロックの並び替えや結合が発生しても、個々の文字・単語・行が正確に認識されていれば高精度を示す
- ワークフロー全体のチューニングに適した精度指標

**出典:**
- [Flexible character accuracy measure for reading-order-independent evaluation | Pattern Recognition Letters](https://www.sciencedirect.com/science/article/pii/S0167865520300416)
- [PRImA Research](http://www.primaresearch.org/www/assets/papers/PRL_Clausner_FlexibleCharacterAccuracy.pdf)

### 1.4 文字単位の適合率・再現率・F1

国立国会図書館（NDL）の古典籍OCR評価で採用されている方式。

**計算式:**

```
Precision = 正しく認識された文字数 / OCR出力の総文字数
Recall    = 正しく認識された文字数 / GT中の総文字数
F1        = 2 × Precision × Recall / (Precision + Recall)
```

**NDLでの実績:**
- NDLkotenOCR ver.2: 中央値F-score約0.92（3,028画像での評価）
- 評価にはクラウドソーシングによる翻刻データ（[みんなで翻刻](https://honkoku.org/)）をGTとして使用

**出典:**
- [NDL Experimental OCR Conversion](https://lab.ndl.go.jp/data_set/r4_kotenocr_en/)
- [MMOCR Evaluation Documentation](https://mmocr.readthedocs.io/en/stable/basic_concepts/evaluation.html)

---

## 2. 単語・行レベルの評価指標

### 2.1 Word Error Rate (WER)

CERと同じ計算原理を単語レベルに適用した指標。

**計算式:**

```
WER = (S_w + D_w + I_w) / N_w
```

- `S_w`, `D_w`, `I_w` = 単語レベルの置換・削除・挿入
- `N_w` = GT中の総単語数

**CERとの関係:**
- 1文字の誤りでも単語全体が誤りとなるため、WERはCERより高くなる傾向がある
- 例: CER 5% → WER 25% 程度になることがある
- 日本語ではスペースによる単語区切りがないため、WERの適用には形態素解析等による前処理が必要

**OCR-Dでの定義:**
- 「単語」はホワイトスペース間のシーケンスから句読点を除いたもの（Unicode TR29準拠）

**出典:**
- [Comparing CER and WER for NLP OCR Accuracy | Medium](https://medium.com/@tam.tamanna18/deciphering-accuracy-evaluation-metrics-in-nlp-and-ocr-a-comparison-of-character-error-rate-cer-e97e809be0c8)
- [Quality Assurance in OCR-D](https://ocr-d.de/en/spec/ocrd_eval.html)

### 2.2 Word Recognition Rate / Word Accuracy

単語レベルの完全一致で評価する指標。

**MMMOCRのWordMetricでは3つのマッチングモード:**
- **exact**: 完全一致
- **ignore_case**: 大文字小文字を無視
- **ignore_case_symbol**: 大文字小文字と句読点を無視（学術論文での標準的な報告方式）

**出典:**
- [MMOCR Evaluation Documentation](https://mmocr.readthedocs.io/en/stable/basic_concepts/evaluation.html)

### 2.3 Sequence Accuracy / Line Recognition Rate

行単位での完全一致率。手書き文字認識（HTR）の評価で広く使用される。

**報告されている性能レベル:**
- 行レベル認識: CER 2.88%, WER 9.39%
- 段落レベル認識: CER 3.75%, WER 10.48%
- ページレベル認識: CER 3.77%, WER 10.08%

**出典:**
- [End-to-End page-Level assessment of HTR | ScienceDirect](https://www.sciencedirect.com/science/article/pii/S003132032300393X)
- [Handwritten Text Recognition: A Survey | arXiv](https://arxiv.org/html/2502.08417v1)

### 2.4 Bag-of-Words Error Rate (BoW)

読み順に依存しない単語レベルの評価指標。

**計算式:**

```
BoW Error = Σ|count_GT(w) - count_OCR(w)| / (total_words_GT + total_words_OCR)
```

**特徴:**
- テキストを単語の多重集合（multiset）として扱い、出現順序を無視
- レイアウト解析の読み順エラーに影響されない
- FCA（Flexible Character Accuracy）と相関が高い
- CERとの差分（ΔWER = WER - BoW-WER）がレイアウト解析の品質指標になる

**出典:**
- [Quality Assurance in OCR-D](https://ocr-d.de/en/spec/ocrd_eval.html)
- [Europeana Newspapers OCR Workflow Evaluation | PRImA](https://primaresearch.org/www/assets/papers/HIP2015_Pletschacher_OCRWorkflowEvaluation.pdf)

---

## 3. 文書レベルの評価指標

### 3.1 Levenshtein距離（編集距離）

OCR評価指標の大半の基盤となるアルゴリズム。

**定義:**
2つの文字列間の最小編集操作数（挿入・削除・置換）。

**例:**
`fmd` → `ſind` は3操作（OCR-Dの例）

**正規化レーベンシュタイン距離:**

```
NLD = levenshtein_distance(s1, s2) / max(len(s1), len(s2))
```

**出典:**
- [Quality Assurance in OCR-D](https://ocr-d.de/en/spec/ocrd_eval.html)

### 3.2 Average Normalized Levenshtein Similarity (ANLS)

DocVQA等の文書理解タスクで標準的に使われる指標。Biten et al. (ICCV'19) で提案。

**計算式:**

```
NLS(s_pred, s_gt) = 1 - NLD(s_pred, s_gt)

ANLS = (1/N) Σ max(NLS(s_pred, s_gt_i))  (各質問に対する最大類似度の平均)
```

**閾値メカニズム:**
- 閾値0.5を使用
- NLS >= 0.5: そのスコアを採用（正しい領域が選択されたがOCR誤りあり）
- NLS < 0.5: スコア0（そもそも誤った領域を選択）

**特徴:**
- OCR誤りに対する穏やかなペナルティを適用
- 大文字小文字を区別しない（case-insensitive）
- スペースの違いはペナルティ対象
- LayoutLM, Donut等の文書理解モデル評価で使用

**Pythonライブラリ:** `pip install anls`

**出典:**
- [ANLS Implementation Guide | DOCSAID](https://docsaid.org/en/blog/impl-normalized-levenshtein-similarity/)
- [ANLS Python Package | PyPI](https://pypi.org/project/anls/)
- [GitHub - shunk031/ANLS](https://github.com/shunk031/ANLS)

### 3.3 1-NED (One Minus Normalized Edit Distance)

テキスト行レベルの評価で使用される指標。

**計算式（MMOCR）:**

```
score = 1 - (1/N) Σ [D(s_i, ŝ_i) / max(l_i, l̂_i)]
```

- `D(s_i, ŝ_i)` = レーベンシュタイン距離
- `l_i`, `l̂_i` = GT文字列とOCR出力文字列の長さ

**特徴:**
- 完全一致の単語精度より長いテキストの性能差を適切に捕捉
- 部分的な認識成功を評価に反映

**出典:**
- [MMOCR Evaluation Documentation](https://mmocr.readthedocs.io/en/stable/basic_concepts/evaluation.html)

### 3.4 BLEU的指標の応用

本来は機械翻訳評価用だが、OCR/文書理解分野でも応用されている。

**OCRBench v2での使用:**
- Long Reading（長文読み取り）タスクの評価に BLEU, METEOR, F1, edit distance を組み合わせて使用
- 日本語合成OCRデータセットでは BLEU-1 Score（character-level）をSacreBLEUで計算（NFKC正規化適用）

**出典:**
- [OCRBench v2 | arXiv](https://arxiv.org/html/2501.00321v2)
- [Synthetic Japanese OCR Dataset | Emergent Mind](https://www.emergentmind.com/topics/synthetic-japanese-ocr-dataset)

### 3.5 TEDS (Tree Edit Distance-based Similarity)

表認識タスク専用の評価指標。

**原理:**
- 表をHTML木構造として表現し、予測と正解の木間の正規化編集距離で類似度を測定
- 表の構造とセル内テキストの両方を評価

**利点:**
- 従来の隣接関係指標より多段セルのずれやOCRエラーを適切に捕捉

**出典:**
- [Image-based table recognition: data, model, and evaluation | arXiv](https://arxiv.org/abs/1911.10683)
- [The Ultimate Guide to Assessing Table Extraction | Nanonets](https://nanonets.com/blog/the-ultimate-guide-to-assessing-table-extraction/)

---

## 4. 日本語特有の評価課題

### 4.1 漢字・ひらがな・カタカナ混在テキストの評価

**課題:**
- 日本語は漢字・ひらがな・カタカナ・アルファベット・数字の3,000文字以上を使用し、認識対象のバリエーションが英語の26文字と比較して圧倒的に多い
- 文字種ごとに認識難易度が異なるため、全体CERだけでは性能を正確に把握できない

**推奨される評価方法:**
- 文字種別（漢字/ひらがな/カタカナ/英数字/記号）のCERを個別に報告
- 混在パターン別の精度を評価

**日本語OCRの実績値（TECHSCOREブログの比較）:**
- Google Cloud Vision: 平均CER 0.0547（最良）
- Azure Computer Vision: 平均CER 0.2145
- YomiToku: 平均CER 0.2161
- Tesseract: 平均CER 0.346
- OpenAI系（GPT-4o等）: CER 0.42〜0.99（実用性低い）

**出典:**
- [日本語対応 OCR モデルの比較 | TECHSCORE BLOG](https://blog.techscore.com/entry/2025/12/17/080000)
- [文字認識（OCR）技術の検証 | アルモニコス](https://www.armonicos.co.jp/laboratory/29/)

### 4.2 旧字体・異体字の扱い

**重要な制約: Unicode正規化（NFKC）では解決できない**

- Unicode正規化（NFC/NFKC）は全角⇔半角の統一や互換文字の正規化に有効
- しかし、旧字体と新字体は**異なるコードポイント**として定義されており、NFKC正規化では変換されない
- 例: 「學」(旧字体, U+5B78) と「学」(新字体, U+5B66) は正規化後も区別される
- CJK統合漢字は、どんなに字形が似ていても正規化で統合されない

**対応策:**
1. **旧字体→新字体の変換テーブル**を作成し、評価前に両テキストを正規化
2. JIS X 0208/0212/0213 の規格に基づく対応表の利用
3. IVS（Ideographic Variation Sequence）/ IVD（Ideographic Variation Database）による異体字管理
4. 評価ガイドラインで「どちらの字体も正解とする」ルールを明記

**出典:**
- [旧字体と新字体の相互変換 | Zenn](https://zenn.dev/shundeveloper/articles/634c84b4bf0db7)
- [Unicode正規化 - Wikipedia](https://ja.wikipedia.org/wiki/Unicode%E6%AD%A3%E8%A6%8F%E5%8C%96)
- [Unicode正規化 | Nomenclator](https://nomenclator.la.coocan.jp/unicode/normalization.htm)

### 4.3 送り仮名・表記揺れの扱い

**課題:**
- 「行なう」vs「行う」、「引き続き」vs「引続き」等の送り仮名のバリエーション
- 「サーバー」vs「サーバ」等の長音表記の揺れ
- 「Ｔｏｋｙｏ」（全角）vs「Tokyo」（半角）等の文字幅の違い

**対応策:**
1. **NFKC正規化**: 全角英数字→半角、半角カナ→全角カナの統一に有効
2. **neologdn**: 日本語テキスト前処理ライブラリ（MeCab+NEologd辞書推奨の正規化）
3. **評価ガイドライン**: 許容される表記バリエーションのリストを事前定義
4. **形態素解析による正規化**: 送り仮名の揺れを辞書形に統一してから比較

**出典:**
- [日本語テキストの前処理 | tuttieee's blog](https://tuttieee.hatenablog.com/entry/ja-nlp-preprocess)
- [文字列の表記揺れをUnicode正規化で解決 | Qiita](https://qiita.com/y-ken/items/d08eb7f66c8fb2fa7d21)

### 4.4 セグメンテーションフリーOCRの評価

**日本語固有の課題:**
- 日本語はスペースで単語を区切らないため、単語分割が曖昧
- 手書き文字では文字間のスペースも不明瞭で、文字セグメンテーション自体が困難
- 認識手がかりと言語コンテキストなしには文字を一意にセグメント化できない

**対応策:**
- WERではなくCERを主指標として採用
- 形態素解析器（MeCab等）で単語分割してからWERを計算する場合は、使用した解析器と辞書を明記
- End-to-end評価でセグメンテーションと認識を統合的に評価
- BoW（Bag of Words）指標で読み順依存性を排除

**出典:**
- [Thinning CJK script for segmentation-free OCRs | IJSRCSEIT](https://ijsrcseit.com/home/issue/view/article.php?id=CSEIT2410111)
- [Online Handwritten Chinese/Japanese Character Recognition | IntechOpen](https://www.intechopen.com/chapters/40720)

---

## 5. 検出＋認識の統合評価

### 5.1 テキスト検出の評価指標

#### 5.1.1 IoU (Intersection over Union)

**計算式:**

```
IoU = Area_overlap / (Area_1 + Area_2 - Area_overlap)
```

- 値域: 0〜1
- 一般的な閾値: 0.5（IoU > 0.5 で True Positive）

#### 5.1.2 Precision / Recall / F1 (Hmean)

**計算式:**

```
Precision = TP / (TP + FP)
Recall    = TP / (TP + FN)
Hmean     = 2 × P × R / (P + R)
```

**HmeanIOUMetric（MMOCR）:**
- テキスト検出タスクで最も広く使われる指標
- IoUベースのマッチング → Precision/Recall → 調和平均（Hmean = F1）
- スコア閾値のフィルタリング（デフォルト: 0.3〜0.9、0.1刻み）

**マッチング戦略:**
- **Vanilla**: 先着順マッチング（ICDAR標準）
- **Max_matching**: 全体のマッチ数を最適化

#### 5.1.3 mAP (mean Average Precision)

物体検出の標準指標。テキスト検出にも適用される。

**出典:**
- [MMOCR Evaluation Documentation](https://mmocr.readthedocs.io/en/stable/basic_concepts/evaluation.html)
- [Quality Assurance in OCR-D](https://ocr-d.de/en/spec/ocrd_eval.html)

### 5.2 End-to-End評価プロトコル

#### 5.2.1 DetEval（ICDAR2013）

- GT検出と予測検出の相互オーバーラップ率に基づくマッチング
- OO（One-to-One）、OM（One-to-Many）、MO（Many-to-One）の3段階評価
- 欠点: 粒度の違い、複数行テキスト、文字の不完全性に対応困難

#### 5.2.2 TedEval

NAVER CLOVAai が開発。DetEvalの欠点を解決。

- **インスタンスレベルマッチング**: 粒度の違いを処理
- **文字レベルスコアリング**: 検出品質をより精密に評価
- ICDAR15公式評価コードベース

**出典:**
- [GitHub - clovaai/TedEval](https://github.com/clovaai/TedEval)
- [TedEval: A Fair Evaluation Metric | arXiv](https://arxiv.org/abs/1907.01227)

#### 5.2.3 CLEval (Character-Level Evaluation)

NAVER CLOVAai が開発。最も細粒度のEnd-to-End評価指標。

**特徴:**
- 文字レベルのスコアを集約してEnd-to-End結果を評価
- 検出と認識の個別評価も統合的に提供
- Split/Mergeケースのインスタンスマッチング処理

**サポート機能:**
- Precision / Recall / F-measure
- サンプル単位の結果分析
- スケール別評価（テキストサイズ別性能）
- ドメイン別・方向別評価
- 信頼度スコアベースの評価

**入力フォーマット:**
- LTRB: 左上右下座標
- QUAD: 4点座標
- POLY: ポリゴン形式

**インストール:** `pip install cleval`

**出典:**
- [GitHub - clovaai/CLEval](https://github.com/clovaai/CLEval)
- [CLEval: Character-Level Evaluation | CVPR 2020 Workshop](https://openaccess.thecvf.com/content_CVPRW_2020/papers/w34/Baek_CLEval_Character-Level_Evaluation_for_Text_Detection_and_Recognition_Tasks_CVPRW_2020_paper.pdf)

#### 5.2.4 TIoU (Tightness-aware IoU)

CVPR 2019で提案。

- Recall R, Precision P, Tightness T（True Positive間の平均IoU）の調和平均
- 検出のタイト性を評価に組み込む

**出典:**
- [Tightness-aware Evaluation Protocol | CVPR 2019](https://openaccess.thecvf.com/content_CVPR_2019/papers/Liu_Tightness-Aware_Evaluation_Protocol_for_Scene_Text_Detection_CVPR_2019_paper.pdf)
- [GitHub - Yuliang-Liu/TIoU-metric](https://github.com/Yuliang-Liu/TIoU-metric)

### 5.3 Recognition-only vs End-to-End

| 評価方式 | 入力 | 評価対象 | 主要指標 |
|---------|------|---------|---------|
| Recognition-only | クロップ済画像 | 認識精度のみ | CER, WER, Word Accuracy |
| Detection-only | 原画像 | 検出精度のみ | IoU, Precision, Recall, Hmean |
| End-to-End | 原画像 | 検出＋認識 | CLEval F-measure, E2E Hmean |

---

## 6. 評価ツール・ライブラリ

### 6.1 Python汎用ライブラリ

#### jiwer

最も広く使われるCER/WER計算ライブラリ。

```python
pip install jiwer
```

```python
from jiwer import wer, cer, process_words, process_characters

reference = "こんにちは世界"
hypothesis = "こんにちわ世界"

# 基本的な使用
error_cer = cer(reference, hypothesis)
error_wer = wer(reference, hypothesis)

# 詳細な分析
output = process_characters(reference, hypothesis)
# output.cer, output.substitutions, output.deletions, output.insertions

# アライメント可視化
from jiwer import visualize_alignment
visualize_alignment(output)
```

**サポート指標:** WER, CER, MER (Match Error Rate), WIL (Word Information Lost), WIP (Word Information Preserved)

**特徴:**
- RapidFuzz（C++実装）による高速計算
- アライメント可視化機能
- エラー頻度の集計機能
- 前処理変換パイプライン（Compose API）

**出典:**
- [jiwer | PyPI](https://pypi.org/project/jiwer/)
- [jiwer Documentation](https://jitsi.github.io/jiwer/)
- [GitHub - jitsi/jiwer](https://github.com/jitsi/jiwer)

#### RapidFuzz

高速文字列マッチングライブラリ。レーベンシュタイン距離の計算に最適。

```python
pip install rapidfuzz
```

```python
from rapidfuzz.distance import Levenshtein
distance = Levenshtein.distance("手書き文字", "手書文字")
normalized = Levenshtein.normalized_distance("手書き文字", "手書文字")
```

**出典:**
- [RapidFuzz Documentation](https://rapidfuzz.github.io/RapidFuzz/Usage/index.html)
- [GitHub - rapidfuzz/RapidFuzz](https://github.com/rapidfuzz/RapidFuzz)

#### python-Levenshtein

RapidFuzzベースのレーベンシュタイン距離計算ライブラリ。

```python
pip install Levenshtein
```

**出典:**
- [GitHub - rapidfuzz/Levenshtein](https://github.com/rapidfuzz/Levenshtein)

#### ANLS

DocVQA評価用のANLS計算ライブラリ。

```python
pip install anls
```

```python
from anls import anls_score
score = anls_score(prediction="認識結果", gold_labels=["正解テキスト"], threshold=0.5)
```

**出典:**
- [ANLS | PyPI](https://pypi.org/project/anls/)
- [GitHub - shunk031/ANLS](https://github.com/shunk031/ANLS)

#### TorchMetrics

PyTorchエコシステム向けの評価指標ライブラリ。

```python
pip install torchmetrics
```

- `torchmetrics.text.EditDistance` でレーベンシュタイン距離を計算可能
- PyTorch Lightningとの統合

**出典:**
- [Edit Distance | PyTorch-Metrics Documentation](https://lightning.ai/docs/torchmetrics/stable/text/edit.html)

#### fastwer

CER/WER計算の軽量ライブラリ。

```python
pip install fastwer
```

**出典:**
- [GitHub - kennethleungty/OCR-Metrics-CER-WER](https://github.com/kennethleungty/OCR-Metrics-CER-WER)

### 6.2 OCR専用評価ツール

#### dinglehopper

Qurator/OCR-Dプロジェクトの OCR評価ツール。現在最も広く使われている。

```python
pip install dinglehopper
```

```bash
# 単一ファイル比較
dinglehopper ground-truth.page.xml ocr-result.alto.xml

# バッチ処理
dinglehopper-summarize results/
```

**サポートフォーマット:** ALTO XML, PAGE XML, プレーンテキスト
**出力:** HTML/JSONレポート（CER, WER, 差分表示）
**Unicode対応:** 対応済み

**出典:**
- [GitHub - qurator-spk/dinglehopper](https://github.com/qurator-spk/dinglehopper)

#### ocrevalUAtion

IMPACT プロジェクト発の評価ツール（アリカンテ大学開発）。

**特徴:**
- CER/WER/BoW のHTML形式レポート出力
- Rice法に基づくCER/WER計算
- 順序なしWER対応

**出典:**
- [GitHub - impactcentre/ocrevalUAtion](https://github.com/impactcentre/ocrevalUAtion)

#### ocreval (ISRI Tools)

ISRI Analytic Tools for OCR Evaluationの近代化版。UTF-8サポート。

**出典:**
- [GitHub - eddieantonio/ocreval](https://github.com/eddieantonio/ocreval)

#### ocrmultieval (OCR-D)

複数の評価バックエンドを統合するラッパーツール。

**対応バックエンド:**
- dinglehopper
- ocrevalUAtion
- PrimaTextEval
- CorAsvAnnEval / Compare
- OcrdSegmentEvaluate
- IsriOcreval

**出典:**
- [GitHub - OCR-D/ocrmultieval](https://github.com/OCR-D/ocrmultieval)

#### CLEval / TedEval

テキスト検出・認識の統合評価（前述）。

```python
pip install cleval
```

**出典:**
- [GitHub - clovaai/CLEval](https://github.com/clovaai/CLEval)
- [GitHub - clovaai/TedEval](https://github.com/clovaai/TedEval)

### 6.3 OCR評価フレームワーク

#### MMOCR

OpenMMLab のOCRツールキット。評価指標を組み込み。

**内蔵指標:**
- HmeanIOUMetric（検出）
- WordMetric / CharMetric（認識）
- OneMinusNEDMetric（NED）
- F1Metric（KIE）

**出典:**
- [MMOCR Evaluation Documentation](https://mmocr.readthedocs.io/en/stable/basic_concepts/evaluation.html)

#### PRImA LayoutEvaluation

レイアウト解析を含む包括的評価。現時点でレイアウト解析性能を包括的に捕捉できる唯一のツール。

**出典:**
- [PRImA Performance Evaluation](https://www.primaresearch.org/tools/PerformanceEvaluation)

### 6.4 評価ツール比較サマリー

| ツール名 | CER | WER | BoW | レイアウト | 入力形式 | 出力 |
|---------|-----|-----|-----|----------|---------|------|
| dinglehopper | ○ | ○ | - | - | ALTO/PAGE/TXT | HTML/JSON |
| ocrevalUAtion | ○ | ○ | ○ | - | 複数 | HTML |
| ocreval (ISRI) | ○ | ○ | - | - | TXT | TXT |
| PRImA LayoutEval | ○ | ○ | ○ | ○ | PAGE XML | 詳細レポート |
| CLEval | ○ (char-level) | - | - | ○ | LTRB/QUAD/POLY | JSON |
| MMOCR | ○ | ○ | - | ○ | 内蔵 | 内蔵 |

**注:** Neudecker et al. (HIP'21) の調査では、ツール間でCERの計算結果にばらつきがあることが報告されている。dinglehopperのCERが最もばらつきが小さく、ocrevalUAtionが最も大きかった。

**出典:**
- [A survey of OCR evaluation tools and metrics | HIP'21](https://dl.acm.org/doi/10.1145/3476887.3476888)
- [GitHub - cneud/hip21_ocrevaluation](https://github.com/cneud/hip21_ocrevaluation)

---

## 7. Ground Truth作成のベストプラクティス

### 7.1 アノテーションガイドライン

#### OCR-D Ground Truth Guidelines（標準的ガイドライン）

**基本原則:**
- PAGE-XML形式でのGTデータ作成（PRImA Research Labが開発）
- 技術的に検証可能なGT
- 既存の翻刻を規則に基づきGTデータに変換可能

**構成要素:**
1. **Transcription Guidelines**: テキスト翻刻の標準
2. **Layout and Structure**: 印刷テキストのレイアウト・構造マーキング
3. **Structure Ground Truth**: PAGE形式での領域・構造ラベリング

**出典:**
- [OCR-D Ground Truth Guidelines](https://ocr-d.de/en/gt-guidelines/trans/)
- [GitHub - OCR-D/gt-guidelines](https://github.com/OCR-D/gt-guidelines)

#### 共通ガイドラインの必須要素

1. **アノテーション対象の定義**: 何をアノテーションするか
2. **不明瞭文字の処理規則**: 読めない文字の扱い方
3. **改行・句読点の扱い**: 行をまたぐテキストの処理
4. **特殊要素**: ロゴ、透かし、図表の扱い
5. **文字コード・正規化**: Unicode正規化形式（NFC推奨）の指定

**出典:**
- [The Complete Guide to OCR Data Labeling | Kili Technology](https://kili-technology.com/blog/ocr-annotation)
- [Ultimate Guide to Document Annotation for OCR AI | Humans in the Loop](https://humansintheloop.org/ultimate-guide-to-document-annotation-for-ocr-ai/)

### 7.2 アノテーション粒度

| レベル | 用途 | 推奨場面 |
|-------|------|---------|
| 文字レベル | CAPTCHA解読、手書き文字認識 | 文字単位の精密評価が必要な場合 |
| 単語レベル | 一般的なOCR評価 | 大半のOCRユースケース |
| 行レベル | HTR（手書きテキスト認識） | 行単位の認識システム評価 |
| ブロック/段落レベル | レイアウト解析 | 文書構造の評価 |

### 7.3 Inter-Annotator Agreement (IAA)

**重要性:**
- アノテーターの一貫性はGTデータの品質に直結
- 低い一貫性はベンチマークを弱め、モデル性能評価の信頼性を損なう
- IAA測定はモデルの性能上限の推定にも使える

**主要指標:**

#### Cohen's Kappa (κ)

```
κ = (P_o - P_e) / (1 - P_e)
```

- `P_o` = 観測一致率
- `P_e` = 偶然一致率
- 2名のアノテーター間の評価に使用
- 名義尺度・二値データに適切

**scikit-learnでの実装:**
```python
from sklearn.metrics import cohen_kappa_score
kappa = cohen_kappa_score(annotator1, annotator2)
```

#### Krippendorff's Alpha (α)

- 複数アノテーター対応
- 名義・順序・区間・比率尺度すべてに対応
- 欠損データ（全アノテーターが全項目を評価しなくてもよい）に対応
- 値域: -1〜+1（1 = 完全一致）

**Label Studioでの統合:**
- Krippendorff's Alpha による一致度計算をサポート

#### Fleiss' Kappa

- 3名以上のアノテーター間の一致度
- 名義尺度データに使用

**出典:**
- [Cohen's Kappa | scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.cohen_kappa_score.html)
- [Krippendorff's Alpha for Annotation Agreement | Label Studio](https://labelstud.io/blog/how-to-use-krippendorff-s-alpha-to-measure-annotation-agreement/)
- [Inter-Annotator Agreement in Data Annotation | Encord](https://encord.com/blog/interrater-reliability-krippendorffs-alpha/)

### 7.4 品質管理手法

1. **ダブルアノテーション**: 同じデータを複数のアノテーターに割り当て、一致度を測定
2. **ゴールドスタンダード埋め込み**: 既知の正解を含むタスクをキューに混入し、アノテーターの精度を監視
3. **レビュー制度**: 訓練されたレビューアまたはコンセンサス投票による品質確認
4. **段階的アノテーション**: 初回アノテーション → 独立レビュー → 差異の解決
5. **定期的なIAA測定**: 一致度が閾値を下回った場合の再訓練

### 7.5 アノテーションツール

#### Label Studio

- OCRアノテーション用テンプレートあり
- 矩形/ポリゴン領域 → ラベル → テキスト翻刻の3段階ワークフロー
- GT設定機能（アノテーション結果をGTとしてマーク）
- Krippendorff's Alpha によるIAA計算対応

**出典:**
- [OCR Data Labeling Template | Label Studio](https://labelstud.io/templates/optical_character_recognition)
- [Evaluating OCR Model Performance with Label Studio](https://labelstud.io/blog/evaluating-mistral-ocr-with-label-studio/)

#### CVAT

- オープンソース画像アノテーションツール
- テキスト領域のバウンディングボックス/ポリゴンアノテーション対応
- 半自動アノテーション機能

**出典:**
- [GitHub - cvat-ai/cvat](https://github.com/cvat-ai/cvat)
- [Best Open-Source Image Annotation Tools | CVAT Blog](https://www.cvat.ai/resources/blog/best-open-source-image-annotation-tools)

---

## 8. 最新ベンチマーク動向

### 8.1 OCRBench / OCRBench v2

マルチモーダルLLMのOCR能力を評価する包括的ベンチマーク。

**OCRBench v2 (2025):**
- 8つの基本能力、23のタスク、31のシナリオ
- 10,000の人手検証済みQAペア
- バイリンガル（英語・中国語）※日本語は未対応
- 6種類の評価指標: TEDS, IoU, F1, BLEU/METEOR/edit distance, L1距離, Exact Match/ANLS

**出典:**
- [OCRBench v2 | arXiv](https://arxiv.org/html/2501.00321v2)
- [GitHub - Yuliang-Liu/MultimodalOCR](https://github.com/Yuliang-Liu/MultimodalOCR)

### 8.2 日本語OCR用データセット

| データセット | 内容 | 文字数/クラス数 | 評価指標 |
|------------|------|---------------|---------|
| ETL Character Database | 手書き・印刷文字約120万画像 | ひらがな/カタカナ/教育漢字/JIS第1水準漢字等 | Accuracy |
| Kuzushiji-MNIST | くずし字ひらがな 70,000画像 | 10クラス | Top-1 Accuracy |
| Kuzushiji-49 | くずし字ひらがな 270,912画像 | 49クラス | Balanced Accuracy |
| Kuzushiji-Kanji | くずし字漢字 140,424画像 | 3,832クラス | Top-1 Accuracy |
| NDL古典籍OCRデータ | 古典籍画像 | - | Character-level F-score |

**出典:**
- [ETL Character Database](http://etlcdb.db.aist.go.jp/the-etl-character-database/)
- [GitHub - rois-codh/kmnist](https://github.com/rois-codh/kmnist)
- [NDL Experimental OCR](https://lab.ndl.go.jp/data_set/r4_kotenocr_en/)

### 8.3 NDLOCR / NDLOCR-Lite

国立国会図書館が開発した日本語OCRシステム。

**精度:**
- 1860年代以降の書籍・雑誌: 90%以上の認識精度
- 明治期〜昭和初期: 市販OCRの約2倍（約40%→90%以上）
- 3つのモジュール構成: レイアウト認識、文字列認識、読み順整序

**出典:**
- [NDLOCR-Liteの公開 | NDLラボ](https://lab.ndl.go.jp/news/2025/2026-02-24/)
- [OCR処理プログラムの公開 | NDLラボ](https://lab.ndl.go.jp/news/2022/2022-04-25/)

---

## 実践的推奨事項

### 日本語手書きOCR評価のための推奨指標セット

| 評価フェーズ | 推奨指標 | 理由 |
|------------|---------|------|
| 文字認識精度 | CER (正規化版) | 日本語はスペース区切りなしのためWERより適切 |
| 文字認識精度（補助） | Character-level F1 | Precision/Recallの分離が可能 |
| 読み順非依存 | FCA or BoW Error | レイアウト解析エラーの影響を排除 |
| テキスト検出 | Hmean (IoU ≥ 0.5) | ICDAR標準 |
| End-to-End | CLEval F-measure | 検出＋認識の統合的文字レベル評価 |
| 文書理解 | ANLS | 部分的OCRエラーへの寛容な評価 |
| 表構造 | TEDS | 表のHTML構造比較 |

### 前処理チェックリスト

1. **Unicode正規化**: NFC形式に統一（OCR-D推奨）
2. **旧字体→新字体変換**: 変換テーブルによる前処理（NFKC非対応のため）
3. **全角半角統一**: NFKC正規化による英数字・カタカナの統一
4. **空白・改行の正規化**: 評価対象外とするか明示
5. **形態素解析**: WER計算時の単語分割方法を統一
