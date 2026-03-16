# 日本語手書きOCR 国際コンペティション・ベンチマーク データセット調査

調査日: 2026-03-16

---

## 目次

1. [ICDAR 関連コンペティション](#1-icdar-関連コンペティション)
2. [Kaggle くずし字認識コンペティション](#2-kaggle-くずし字認識コンペティション)
3. [日本語手書き文字データセット（国内）](#3-日本語手書き文字データセット国内)
4. [CASIA 中国語手書きデータセット](#4-casia-中国語手書きデータセット)
5. [IAM Handwriting Database（英語）](#5-iam-handwriting-database英語)
6. [RIMES（フランス語手書き）](#6-rimesフランス語手書き)
7. [その他の関連データセット](#7-その他の関連データセット)
8. [評価指標の比較](#8-評価指標の比較)
9. [日本語手書きOCR評価への応用可能性まとめ](#9-日本語手書きocr評価への応用可能性まとめ)

---

## 1. ICDAR 関連コンペティション

### 1.1 ICDAR 2019 RRC-MLT (Robust Reading Challenge on Multi-lingual Scene Text)

- **正式名称**: ICDAR2019 Robust Reading Challenge on Multi-lingual Scene Text Detection and Recognition (RRC-MLT-2019)
- **URL**: https://rrc.cvc.uab.es/?ch=15
- **論文**: [arXiv:1907.00945](https://arxiv.org/abs/1907.00945)

| 項目 | 詳細 |
|------|------|
| データの種類 | 自然シーン中の多言語テキスト画像 |
| 規模 | 実画像 20,000枚（10言語）+ 合成画像 277,000枚 |
| 対応言語 | Arabic, Bangla, Chinese, Devanagari, **English, French, German, Italian, Japanese, Korean** |
| 日本語サンプル数 | 訓練セットから約10,460サンプル（クロップされたテキスト画像） |
| タスク | (a) テキスト検出, (b) クロップ単語のスクリプト分類, (c) テキスト検出+スクリプト分類, (d) End-to-Endの検出+認識 |
| 評価指標 | IoU、H-mean (Precision/Recall調和平均)、F1スコア |
| 参加 | 60件の投稿（研究・産業界） |
| アクセス | RRCポータルへの登録でダウンロード可能 |
| 日本語OCR評価への応用 | シーンテキスト（看板、標識等）の検出・認識に適用可能。縦書き・横書きの両方を含む |

### 1.2 ICDAR 2017 RRC-MLT

- **正式名称**: ICDAR2017 Robust Reading Challenge on Multi-Lingual Scene Text Detection and Script Identification (RRC-MLT)
- **URL**: https://rrc.cvc.uab.es/?ch=8
- **論文**: [IEEE Xplore](https://ieeexplore.ieee.org/document/8270168/)

| 項目 | 詳細 |
|------|------|
| 規模 | 18,000枚（9言語、6スクリプト） |
| タスク | テキスト検出、スクリプト識別 |
| 参加 | 16チーム |
| 特徴 | 2019版の前身。日本語を含む多言語シーンテキスト |

### 1.3 ICDAR 2017 Robust Reading Challenge on Omnidirectional Video (DOST Dataset)

- **正式名称**: Downtown Osaka Scene Text Dataset (DOST)
- **URL**: https://rrc.cvc.uab.es/?ch=7
- **論文**: [SpringerLink](https://link.springer.com/chapter/10.1007/978-3-319-46604-0_32)

| 項目 | 詳細 |
|------|------|
| データの種類 | 全方位カメラで撮影された大阪市内商店街の連続画像 |
| 規模 | 32,147枚の連続画像、935,601テキスト領域（797,919判読可能 + 137,682判読不能）、2,808,340文字 |
| 特徴 | 日本語テキストが主体（ラテン文字も含む）。日本語の読解能力が必要なためクラウドソーシングではなく学生がアノテーション |
| タスク | ビデオ/静止画モード: テキスト位置特定、End-to-End認識、クロップ単語認識 |
| 日本語OCR評価への応用 | 実世界の日本語シーンテキスト認識の評価に最適 |

### 1.4 ICDAR 中国語手書き認識コンペティション（日本語漢字との関連）

#### ICDAR 2013 Chinese Handwriting Recognition Competition

- **論文**: [IEEE Xplore](https://ieeexplore.ieee.org/document/6628856/)
- **使用データベース**: CASIA-HWDB/OLHWDB

| 項目 | 詳細 |
|------|------|
| タスク（5種） | (1) 抽出特徴による分類, (2) オフライン単一文字認識, (3) オンライン単一文字認識, (4) オフラインテキスト認識, (5) オンラインテキスト認識 |
| 参加 | 10グループ、27システム |
| 最高精度 | 特徴分類: 93.89%, オフライン文字: 94.77%, オンライン文字: 97.39%, オフラインテキスト: 88.76%, オンラインテキスト: 95.03% |
| 評価指標 | 文字レベル正解率 (Correct Rate) |

#### ICDAR 2011 Chinese Handwriting Recognition Competition

- **論文**: [IEEE Xplore](https://ieeexplore.ieee.org/document/6065551/)
- **参加**: 8グループ、25システム
- **最高精度**: オフライン文字: 92.18%, オンライン文字: 95.77%, オフラインテキスト: 77.26%, オンラインテキスト: 94.33%

> **日本語との関連**: 中国語の簡体字・繁体字と日本語の漢字は共通の文字を多く含む。これらのコンペティションの手法・モデルは日本語漢字認識に転用可能。

### 1.5 ICDAR 2019 Post-OCR Text Correction

- **URL**: https://sites.google.com/view/icdar2019-postcorrectionocr
- **データ**: [Zenodo](https://zenodo.org/records/3515403)

| 項目 | 詳細 |
|------|------|
| 規模 | 2,200万OCR文字 + アライン済み正解データ |
| 対応言語 | 10ヨーロッパ言語（日本語は未対応） |
| タスク | (1) エラー検出, (2) エラー修正 |
| 評価指標 | 精度41-95%（検出）、最高44%改善（修正） |
| 日本語への応用 | 方法論のみ参考（日本語版は存在しない） |

---

## 2. Kaggle くずし字認識コンペティション

### 2.1 Kuzushiji Recognition Competition (2019)

- **正式名称**: Kuzushiji Recognition: Opening the Door to A Thousand Years of Japanese Culture
- **URL**: https://www.kaggle.com/c/kuzushiji-recognition
- **主催**: CODH (Center for Open Data in the Humanities), NII (国立情報学研究所), NIJL (国文学研究資料館)
- **プレスリリース**: https://www.nii.ac.jp/en/news/release/2019/0710.html

| 項目 | 詳細 |
|------|------|
| 期間 | 2019年7月19日 - 10月14日 |
| タスク | 生の古文書画像からくずし字を検出・認識するOCRアルゴリズムの開発 |
| 対象語彙 | 約4,800文字（Unicode基準） |
| ユニーク文字数 | 4,300以上（長尾分布で一部は1-2回のみ出現） |
| 評価指標 | **F1スコア（F-score）** |
| 参加規模 | 293チーム |
| 上位成績例 | 8位: GitHub公開解法, 15位: 0.900 (private LB), 31位: 0.858 |
| 賞 | 上位5チームに授与（2019年11月11日「日本文化とAI」シンポジウムにて） |
| 特記事項 | Kaggle史上初の人文学関連コンペティション、日本の組織による初のKaggle開催 |
| データセット | NIJL所蔵くずし字データセットのCODH修正版 |
| ライセンス | CC BY-SA 4.0 |

### 2.2 KMNIST (Kuzushiji-MNIST) データセットファミリー

- **GitHub**: https://github.com/rois-codh/kmnist
- **論文**: Clanuwat et al., "Deep Learning for Classical Japanese Literature", arXiv:1812.01718 (NeurIPS 2018 Workshop)
- **ライセンス**: CC BY-SA 4.0

#### Kuzushiji-MNIST (K-MNIST)

| 項目 | 詳細 |
|------|------|
| クラス数 | 10（ひらがな各行1文字: お、き、す、つ、な、は、ま、や、れ、を） |
| サンプル数 | 70,000（訓練: 60,000 / テスト: 10,000） |
| 画像サイズ | 28x28 グレースケール |
| バランス | 完全均等（各クラス6,000/1,000） |
| 評価指標 | Top-1 Accuracy |
| SOTA精度 | 99.34% (shake-shake-26 2x96d) |
| 特徴 | MNISTのドロップイン代替。MNISTより難易度が高い（ラベルと文字の多対一マッピング） |

#### Kuzushiji-49 (K-49)

| 項目 | 詳細 |
|------|------|
| クラス数 | 49（ひらがな48文字 + 踊り字1文字） |
| サンプル数 | 270,912（訓練: 232,365 / テスト: 38,547） |
| 画像サイズ | 28x28 グレースケール |
| バランス | 不均衡 |
| 評価指標 | Balanced Accuracy |
| SOTA精度 | 97.33% (PreActResNet-18 + Manifold Mixup) |

#### Kuzushiji-Kanji (K-Kanji)

| 項目 | 詳細 |
|------|------|
| クラス数 | 3,832（漢字） |
| サンプル数 | 140,424 |
| 画像サイズ | 64x64 グレースケール |
| バランス | 非常に不均衡（1文字あたり1-1,766サンプル） |
| 特徴 | フルデータセット提供、train/testスプリットは計画中 |

### 2.3 Kaggle: Handwriting OCR Data of Japanese and Korean (Nexdata)

- **URL**: https://www.kaggle.com/datasets/nexdatafrank/handwriting-ocr-data-of-japanese-and-korean
- **HuggingFace**: https://huggingface.co/datasets/Nexdata/Handwriting_OCR_Data_of_Japanese_and_Korean

| 項目 | 詳細 |
|------|------|
| 規模 | 100人（日本人50、韓国人49、アフガニスタン人1）、22,163点の手書き画像 |
| 収集方法 | A4用紙、罫線紙、方眼紙等にスマホで撮影 |
| 内容 | 日本語の作文、詩、散文、ニュース、物語等 |
| アノテーション | 行レベルの四角形バウンディングボックス + テキスト転写 |
| ライセンス | サンプルデータセット（フル版は有料） |

---

## 3. 日本語手書き文字データセット（国内）

### 3.1 ETL Character Database (ETLCDB)

- **URL**: http://etlcdb.db.aist.go.jp/
- **提供元**: 産業技術総合研究所 (AIST)（旧 電子技術総合研究所）
- **収集期間**: 1973-1984年

| データセット | 文字種 | サンプル数 | 書き手数 | 解像度 | 収集年 |
|---|---|---|---|---|---|
| ETL1 | 英数字、記号、カタカナ99 | 141,319 | 1,445 | 72x76 (64x63) | 1973 |
| ETL2 | ひらがな、カタカナ、英数字、記号、漢字（2,184種） | 52,796 | - | 60x60 | 1973 |
| ETL3 | 数字、大文字、特殊文字（48種） | 9,600 | 200 | 72x76 | 1974 |
| ETL4 | ひらがな（51種） | 6,120 | 120 | 72x76 | 1974 |
| ETL5 | カタカナ（51種） | 10,608 | 104 | 72x76 | 1975 |
| ETL6 | カタカナ、英数字、記号（114種） | - | - | - | - |
| ETL7 | ひらがな、カタカナ（同上拡張） | - | - | - | - |
| **ETL8B/8G** | **教育漢字881 + ひらがな75** | **153,916** | **160** | **64x63** | **1980** |
| **ETL9B/9G** | **JIS第1水準漢字含む3,036クラス** | **606,900** | - | **60x60** | - |

| 項目 | 詳細 |
|------|------|
| 総サンプル数 | 約120万文字画像 |
| 対象文字 | 手書き・印刷の英数字、記号、ひらがな、カタカナ、教育漢字、JIS第1水準漢字 |
| データ形式 | バイナリ形式 (B: 白黒, G: グレースケール) |
| ライセンス | **無料で研究利用可能**（2011年4月よりインターネットダウンロード提供） |
| 日本語OCR評価への応用 | 日本語手書き文字認識研究の最も基本的なベンチマーク。文字レベルの認識精度評価に最適 |

**注目すべきサブセット:**
- **ETL9G**: JIS第1水準漢字を含む3,036クラス、606,900サンプル。日本語漢字認識研究で最も広く使用
- **ETL8G**: 教育漢字879字+ひらがな71字。HuggingFaceでも提供 ([LT8/Kanji_ETL8G](https://huggingface.co/LT8/Kanji_ETL8G), [LT8/Kanji_ETL9G](https://huggingface.co/LT8/Kanji_ETL9G))

### 3.2 Nakayosi Database（中川研究室）

- **URL**: http://web.tuat.ac.jp/~nakagawa/database/en/about_nakayosi.html
- **提供元**: 東京農工大学 (TUAT) 中川研究室

| 項目 | 詳細 |
|------|------|
| 書き手数 | 163人 |
| 文字パターン数 | 10,403パターン（各書き手あたり） |
| 文字カテゴリ | 4,438クラス（JIS第1水準漢字、JIS第2水準漢字約1,000字、ひらがな、カタカナ、英字、数字、記号） |
| データの種類 | オンライン手書き文字パターン |
| テキスト元 | 日本語新聞から抜粋 |
| アクセス | 購入制（中川教授に問い合わせ: nakagawa@cc.tuat.ac.jp） |
| 日本語OCR評価への応用 | 日本語手書きテキスト認識のベンチマーク標準 |

### 3.3 Kondate Database（中川研究室）

- **URL**: http://web.tuat.ac.jp/~nakagawa/database/index.html
- **論文**: [Semantic Scholar](https://www.semanticscholar.org/paper/A-Database-of-On-Line-Handwritten-Mixed-Objects-Matsushita-Nakagawa/a0301f87024218433e08d9ae69d31a7764868f37) (2014)

| 項目 | 詳細 |
|------|------|
| 書き手数 | 100人 |
| 内容 | テキスト、図、表、地図、ダイアグラム等の混合手書きオブジェクト |
| 文字リスト | Kondate Nakayosi合わせて4,441文字 |
| 使用例 | 訓練: 75人分 / テスト: 25人分に分割 |
| 日本語OCR評価への応用 | セグメンテーションフリーの日本語手書きテキスト行認識のベンチマーク。OpenVINOの日本語手書き認識モデル(handwritten-japanese-recognition-0001)の学習に使用 |

### 3.4 日本古典籍くずし字データセット (CODH/NIJL)

- **URL**: https://codh.rois.ac.jp/char-shape/
- **提供元**: 人文学オープンデータ共同利用センター (CODH) / 国文学研究資料館 (NIJL)

| 項目 | 詳細 |
|------|------|
| 規模 | 古典籍44点、画像6,151コマ、くずし字4,328文字種、字形データ1,086,326文字（2019年11月時点） |
| 拡張版 | 文字種: 1,521 → 3,999 → 4,645種、文字数: 86,176 → 403,242 → 684,165点 |
| ライセンス | CC BY-SA 4.0 |
| 関連 | KMNISTデータセットの元データ、Kaggle Kuzushiji Recognitionの元データ |
| 日本語OCR評価への応用 | 歴史的文書・くずし字認識の評価に最適 |

### 3.5 NDL (国立国会図書館) OCRデータセット

- **URL**: https://lab.ndl.go.jp/data_set/ocr/
- **GitHub Part1**: https://github.com/ndl-lab/pdmocrdataset-part1
- **GitHub Part2**: https://github.com/ndl-lab/pdmocrdataset-part2

| 項目 | 詳細 |
|------|------|
| Part1 (OCRテキスト化) | 2,713画像（LINE社委託、2022年4月時点） |
| Part2 (OCR処理プログラム開発) | 3,997画像（Morpho AI Solutions委託、凸版印刷がデータセット構築） |
| 対象 | パブリックドメインのデジタル化資料（約247万点のOCR処理） |
| ライセンス | CC BY 4.0 |
| 精度評価 | 33カテゴリ中32カテゴリが目標性能を達成 |
| 日本語OCR評価への応用 | 近代・歴史的日本語文書のOCR精度評価に有用 |

### 3.6 JEITA-HP Database

| 項目 | 詳細 |
|------|------|
| 内容 | DATASET-A, DATASET-Bから構成されるオフライン文字パターン（ビットマップ画像） |
| 認識率 | 96.26%（OCRシステムによる評価） |
| 用途 | 手書き日本語文字認識システムの評価 |
| 関連 | IEICE PRMU技術報告で頻繁に参照 |

---

## 4. CASIA 中国語手書きデータセット

### 4.1 CASIA-HWDB / CASIA-OLHWDB

- **URL**: https://www.nlpr.ia.ac.cn/databases/handwriting/Home.html
- **提供元**: 中国科学院自動化研究所 (CASIA) パターン認識国家研究室 (NLPR)
- **論文**: [IEEE Xplore](https://ieeexplore.ieee.org/document/6065272/) (ICDAR 2011)

| 項目 | 詳細 |
|------|------|
| 書き手数 | 1,020人 |
| 収集方法 | Anotoペンを使用（オンライン＋オフライン同時収集） |
| 単一文字データ | 約390万サンプル、7,356クラス（7,185漢字 + 171記号） |
| テキストデータ | 約5,090ページ、135万文字サンプル |
| 文字セット | GB2312-80基準（6,763漢字: 第1水準3,755 + 第2水準3,008） |
| データ構成 | オンライン6データセット + オフライン6データセット（各3つが単一文字、3つがテキスト） |
| 評価指標 | 文字レベル正解率 |
| アクセス | 研究用途で利用可能（NLPR公式サイトから申請） |

**日本語OCR評価への応用:**
- 中国語漢字と日本語漢字の共通部分が多いため、漢字認識モデルの転移学習に活用可能
- ICDAR中国語手書きコンペティション (2011, 2013) の手法が日本語に応用可能
- ただし日本語固有の文字（ひらがな・カタカナ）や用法の違いには注意が必要

---

## 5. IAM Handwriting Database（英語）

- **URL**: https://fki.tic.heia-fr.ch/databases/iam-handwriting-database
- **初出**: ICDAR 1999
- **論文**: Marti & Bunke (2002)

| 項目 | 詳細 |
|------|------|
| 書き手数 | 657人 |
| スキャンページ数 | 1,539ページ |
| 文 | 5,685文（ラベル付き） |
| テキスト行 | 13,353行（ラベル付き） |
| 単語 | 115,320語（ラベル付き） |
| 解像度 | 300dpi、256階調グレースケール PNG |
| テキスト元 | LOBコーパス（英語） |
| ライセンス | **非商用研究目的のみ**（登録必要、引用義務あり） |
| 評価タスク | Large Writer Independent Text Line Recognition Task (訓練6,161 / 検証1,840 / テスト1,861行, 500人) |
| 主要評価指標 | **CER (Character Error Rate)**, **WER (Word Error Rate)** |

**ベンチマーク精度:**
| モデル | CER | WER |
|--------|-----|-----|
| CNN-BiLSTM + CTC | 3.59% | 9.44% |
| GPT-4o-mini | 1.71% | 3.34% |

**日本語OCR評価への応用:**
- 直接的にはデータは使えない（英語のみ）
- HTR手法の設計・評価方法論の参考として極めて重要
- CER/WER評価フレームワークは日本語にも適用可能
- セグメンテーションフリー認識手法の多くがIAMで検証されている

---

## 6. RIMES（フランス語手書き）

- **正式名称**: Reconnaissance et Indexation de donnees Manuscrites et de fac similes (RIMES)
- **URL**: http://www.a2ialab.com/doku.php?id=rimes_database:start
- **関連コンペ**: ICDAR 2011 French Handwriting Recognition Competition

| 項目 | 詳細 |
|------|------|
| 規模 | 12,723手書きページ、5,605通の手紙（2-3ページ/通） |
| 二次DB | 単一文字、手書き単語（300,000スニペット）、ロゴ |
| 書き手数 | 1,300人以上 |
| 収集方法 | ボランティアが架空のIDで9テーマのシナリオに基づく手紙を執筆 |
| テーマ | 個人情報変更、情報依頼、口座開設/閉鎖、契約変更、苦情、支払困難等 |
| ライセンス | **無料（学術利用のみ）**、NDA送付が必要 (rimesnda@a2ia.com) |
| 評価指標 | **CER, WER** |
| コンペタスク | (1) 辞書付き単語認識, (2) 行分割テキストブロック認識 |

**ベンチマーク精度例:**
- CNN-BLSTM-S2S-CTC: CER 3.13%, WER 8.94%

**日本語OCR評価への応用:**
- データは使えない（フランス語のみ）
- 手紙・フォーム形式の文書認識手法の参考
- 多言語展開を見据えた評価手法論の参考

---

## 7. その他の関連データセット

### 7.1 HJDataset (Historical Japanese Documents)

- **論文**: [CVPRW 2020](https://openaccess.thecvf.com/content_CVPRW_2020/papers/w34/Shen_A_Large_Dataset_of_Historical_Japanese_Documents_With_Complex_Layouts_CVPRW_2020_paper.pdf)
- **URL**: https://dell-research-harvard.github.io/HJDataset/
- **著者**: Zejiang Shen, Kaixuan Zhang, Melissa Dell (Harvard University)

| 項目 | 詳細 |
|------|------|
| 規模 | 250,000以上のレイアウト要素アノテーション |
| アノテーション | 7階層のレイアウト要素カテゴリ（バウンディングボックス、マスク、階層構造、読み順） |
| 特徴 | 縦書きテキスト対応、複雑レイアウトの歴史的日本語文書 |
| 方法 | 半ルールベースの抽出 + 人間による検査 |
| 用途 | テキスト領域検出、レイアウト分析 |

### 7.2 CEDAR Japanese OCR Database

- **URL**: https://cedar.buffalo.edu/japanese/JOCRdatabase.html
- **提供元**: CEDAR, SUNY Buffalo

| 項目 | 詳細 |
|------|------|
| サンプル数 | 約180,000文字画像 |
| カテゴリ | 3,300以上（JIS level-0, level-1） |
| 文字種 | 漢字、ひらがな、カタカナ、英数字、記号 |
| データソース | 書籍、FAX、雑誌、新聞、レーザープリンタ出力等 |
| 解像度 | 400dpi バイナリ TIFF |
| 真値 | 4バイトJISコード |
| 価格 | **$1,500 USD**（8mmテープまたはCDROM） |
| 特徴 | 印刷日本語文字の認識研究用（手書きではなく印刷文字が主） |

### 7.3 Nexdata Japanese Handwriting OCR Data

- **URL (101人版)**: https://github.com/Nexdata-AI/101-People-4538-Images-Japanese-Handwriting-OCR-Data
- **URL (5147画像版)**: https://github.com/Nexdata-AI/5147-Images-Japanese-Handwriting-OCR-data

| 項目 | 詳細 |
|------|------|
| 101人版 | 4,538画像、A4用紙、文字・行レベルのバウンディングボックス + テキスト転写 |
| 5147画像版 | 5,147画像の日本語手書きOCRデータ |
| 内容 | 社会生活、エンタメ、旅行、スポーツ、映画、作文等 |
| ライセンス | 商用利用向け有料データセット（サンプルはGitHubで公開） |

### 7.4 Kindai OCR (近代OCR)

- **GitHub**: https://github.com/DeepApps91/Kindai-OCR
- **用途**: 近代日本語雑誌のOCR

| 項目 | 詳細 |
|------|------|
| 学習データ | NDLデータセット（3,997ページ、103,256行）+ CODHデータセット（1,985ページ、59,465行） |
| 手法 | Transformer OCR |
| 用途 | 近代日本語文書のテキスト認識 |

---

## 8. 評価指標の比較

| 評価指標 | 略称 | 説明 | 使用されるデータセット/コンペ |
|----------|------|------|------------------------------|
| Character Error Rate | CER | 正解文字列に対する編集距離の割合 | IAM, RIMES, 一般的HTR評価 |
| Word Error Rate | WER | 正解単語列に対する編集距離の割合 | IAM, RIMES |
| Top-1 Accuracy | Acc | 文字分類の正解率 | KMNIST, ETL, CASIA |
| Balanced Accuracy | BAcc | クラス不均衡を考慮した正解率 | K-49 |
| F1 Score | F1 | 適合率と再現率の調和平均 | Kaggle Kuzushiji Recognition |
| Correct Rate | CR | 文字レベル正解率 | ICDAR中国語コンペ |
| H-mean (F-measure) | Hmean | 検出のPrecision/Recallの調和平均 | ICDAR MLTシーンテキスト |
| IoU | IoU | バウンディングボックスの重なり度合い | シーンテキスト検出 |

**日本語手書きOCR評価に推奨される指標:**
- **文字レベル**: CER（文字誤り率）が最も汎用的
- **単語レベル**: 日本語では形態素単位のWERが適切（分かち書きがないため）
- **文字認識**: Top-1 Accuracy（単一文字分類タスク）
- **検出+認識**: F1スコア（Kaggleくずし字方式）

---

## 9. 日本語手書きOCR評価への応用可能性まとめ

### 直接使用可能なデータセット（日本語）

| データセット | 文字タイプ | 規模 | アクセス | 推奨用途 |
|---|---|---|---|---|
| **KMNIST / K-49 / K-Kanji** | くずし字ひらがな・漢字 | 70K-270K | 無料 (CC BY-SA) | 文字分類ベンチマーク |
| **ETL8G / ETL9G** | ひらがな・漢字 | 15万-60万 | 無料 | 現代手書き文字認識ベンチマーク |
| **Nakayosi / Kondate** | 全文字種 | 4,438クラス | 要問合せ | 手書きテキスト行認識ベンチマーク |
| **NDL OCRデータセット** | 近代日本語 | 6,710画像 | 無料 (CC BY) | 文書OCR精度評価 |
| **日本古典籍くずし字** | くずし字 | 108万文字 | 無料 (CC BY-SA) | 歴史的文書認識 |
| **DOST** | 日本語シーンテキスト | 32K画像、280万文字 | RRC登録 | シーンテキスト認識 |
| **ICDAR MLT 2019** | 多言語(日本語含む) | 20K画像 | RRC登録 | 多言語シーンテキスト |

### 手法・方法論の参考となるデータセット（他言語）

| データセット | 言語 | 参考になる点 |
|---|---|---|
| **CASIA-HWDB** | 中国語 | 漢字認識手法、転移学習元 |
| **IAM** | 英語 | HTR評価フレームワーク、CER/WER手法 |
| **RIMES** | フランス語 | 文書レベル認識、評価手法 |

### 今後の展望

1. **統一ベンチマークの不在**: 日本語手書きOCRには英語のIAMやフランス語のRIMESに相当する統一的なベンチマークが存在しない
2. **文字種の多さ**: 日本語は3つの文字体系（ひらがな・カタカナ・漢字）を持ち、評価が複雑
3. **ICDAR MLTの活用**: 日本語を含む多言語シーンテキストの評価にはICDAR MLT 2017/2019が最適
4. **ETLCDBの重要性**: 国内では最も歴史的かつ広く使用されているベンチマーク
5. **くずし字データの充実**: CODH/NIJLのデータセットは歴史的文書認識で独自のポジション

---

## ソース一覧

### ICDAR関連
- [ICDAR 2019 RRC-MLT](https://rrc.cvc.uab.es/?ch=15)
- [ICDAR 2019 RRC-MLT 論文 (arXiv)](https://arxiv.org/abs/1907.00945)
- [ICDAR 2017 RRC-MLT](https://rrc.cvc.uab.es/?ch=8)
- [ICDAR 2017 Omnidirectional Video (DOST)](https://rrc.cvc.uab.es/?ch=7)
- [DOST Dataset (SpringerLink)](https://link.springer.com/chapter/10.1007/978-3-319-46604-0_32)
- [ICDAR 2013 Chinese Handwriting Recognition Competition](https://ieeexplore.ieee.org/document/6628856/)
- [ICDAR 2011 Chinese Handwriting Recognition Competition](https://ieeexplore.ieee.org/document/6065551/)
- [ICDAR 2024 Competitions](https://icdar2024.net/competitions/)
- [ICDAR 2025 Competitions](https://www.icdar2025.com/program/competitions)
- [ICDAR 2019 Post-OCR Text Correction](https://sites.google.com/view/icdar2019-postcorrectionocr)

### Kaggle・くずし字関連
- [Kaggle Kuzushiji Recognition Competition](https://www.kaggle.com/c/kuzushiji-recognition)
- [CODH Kaggle Competition Page](https://codh.rois.ac.jp/competition/kaggle/index.html.en)
- [NII Press Release](https://www.nii.ac.jp/en/news/release/2019/0710.html)
- [KMNIST GitHub (rois-codh/kmnist)](https://github.com/rois-codh/kmnist)
- [KMNIST Dataset (CODH)](https://codh.rois.ac.jp/kmnist/index.html.en)
- [Deep Learning for Classical Japanese Literature (arXiv:1812.01718)](https://arxiv.org/abs/1812.01718)
- [Nexdata Japanese/Korean OCR (Kaggle)](https://www.kaggle.com/datasets/nexdatafrank/handwriting-ocr-data-of-japanese-and-korean)

### 日本語データセット
- [ETL Character Database](http://etlcdb.db.aist.go.jp/)
- [ETL Database Details](http://etlcdb.db.aist.go.jp/database-development/)
- [ETL Download](https://etlcdb.db.aist.go.jp/download2/)
- [Kanji ETL9G (HuggingFace)](https://huggingface.co/LT8/Kanji_ETL9G)
- [Nakayosi Database](http://web.tuat.ac.jp/~nakagawa/database/en/about_nakayosi.html)
- [TUAT Nakagawa Lab Databases](http://web.tuat.ac.jp/~nakagawa/database/index.html)
- [日本古典籍くずし字データセット (CODH)](https://codh.rois.ac.jp/char-shape/)
- [NDL OCR事業](https://lab.ndl.go.jp/data_set/ocr/)
- [NDL OCRデータセット Part1 (GitHub)](https://github.com/ndl-lab/pdmocrdataset-part1)
- [NDL OCRデータセット Part2 (GitHub)](https://github.com/ndl-lab/pdmocrdataset-part2)
- [CODH Datasets](https://codh.rois.ac.jp/dataset/index.html.en)

### CASIA関連
- [CASIA Handwriting Databases](https://www.nlpr.ia.ac.cn/databases/handwriting/Home.html)
- [CASIA Databases (IEEE)](https://ieeexplore.ieee.org/document/6065272/)
- [CASIA Databases (ResearchGate)](https://www.researchgate.net/publication/232262651_CASIA_Online_and_Offline_Chinese_Handwriting_Databases)

### IAM / RIMES
- [IAM Handwriting Database](https://fki.tic.heia-fr.ch/databases/iam-handwriting-database)
- [IAM Database (ResearchGate)](https://www.researchgate.net/publication/226662568_The_IAM-database_An_English_sentence_database_for_offline_handwriting_recognition)
- [RIMES Database (HAL)](https://hal.science/hal-01395332)
- [ICDAR 2011 French Handwriting Competition](https://ieeexplore.ieee.org/document/6065550/)

### その他
- [HJDataset (CVPRW 2020)](https://openaccess.thecvf.com/content_CVPRW_2020/papers/w34/Shen_A_Large_Dataset_of_Historical_Japanese_Documents_With_Complex_Layouts_CVPRW_2020_paper.pdf)
- [CEDAR Japanese OCR Database](https://cedar.buffalo.edu/japanese/JOCRdatabase.html)
- [Nexdata 101 People Japanese OCR (GitHub)](https://github.com/Nexdata-AI/101-People-4538-Images-Japanese-Handwriting-OCR-Data)
- [Nexdata 5147 Images Japanese OCR (GitHub)](https://github.com/Nexdata-AI/5147-Images-Japanese-Handwriting-OCR-data)
- [Kindai OCR (GitHub)](https://github.com/DeepApps91/Kindai-OCR)
- [OpenVINO Handwritten Japanese Recognition](https://github.com/openvinotoolkit/open_model_zoo/blob/master/models/intel/handwritten-japanese-recognition-0001/README.md)
- [OCR Datasets Collection (GitHub)](https://github.com/xinke-wang/OCRDatasets)
- [Handwritten Document Benchmarks Survey (Springer)](https://link.springer.com/article/10.1186/s13640-015-0102-5)
