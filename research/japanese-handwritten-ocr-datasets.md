# 日本語手書きOCR用 公開評価データセット調査

調査日: 2026-03-16

---

## 目次

1. [ETL文字データベース (ETL Character Database)](#1-etl文字データベース-etl-character-database)
2. [KMNIST (Kuzushiji-MNIST)](#2-kmnist-kuzushiji-mnist)
3. [Kuzushiji-49 / Kuzushiji-Kanji](#3-kuzushiji-49--kuzushiji-kanji)
4. [日本古典籍くずし字データセット](#4-日本古典籍くずし字データセット)
5. [HANDS データベース (Nakagawa Lab, TUAT)](#5-hands-データベース-nakagawa-lab-tuat)
6. [JEITA-HP 日本語手書き文字パターンデータベース](#6-jeita-hp-日本語手書き文字パターンデータベース)
7. [PRMUアルゴリズムコンテスト関連データセット](#7-prmuアルゴリズムコンテスト関連データセット)
8. [NDL（国立国会図書館）OCR関連データセット](#8-ndl国立国会図書館ocr関連データセット)
9. [近代雑誌OCR学習用データセット (CODH)](#9-近代雑誌ocr学習用データセット-codh)
10. [CEDAR Japanese Character Image Database](#10-cedar-japanese-character-image-database)
11. [Kaggle Kuzushiji Recognition コンペティション](#11-kaggle-kuzushiji-recognition-コンペティション)
12. [その他の関連データセット](#12-その他の関連データセット)

---

## 1. ETL文字データベース (ETL Character Database)

### 基本情報

| 項目 | 内容 |
|------|------|
| 正式名称 | ETL Character Database (ETL文字データベース) |
| URL | http://etlcdb.db.aist.go.jp/ |
| 提供元 | 国立研究開発法人 産業技術総合研究所 (AIST)（旧・電子技術総合研究所） |
| 収集期間 | 1973年〜1984年 |
| 協力機関 | 日本電子工業振興協会（現JEITA）、大学、民間研究機関 |

### データの種類

文字単位のデータセット。手書きおよび印刷の英数字、記号、ひらがな、カタカナ、教育漢字、JIS第1水準漢字等を含む。OCRシートに記入された手書き文字のスキャン画像で構成。

### データセット別仕様

| データセット | サンプル数 | 文字種数 | 文字種類 | 画像サイズ | 階調 | 作成年 | 筆記者数 |
|---|---|---|---|---|---|---|---|
| ETL1 | 141,319 | 99 | 数字10、大文字26、記号12、カタカナ51 | 64x63 px | 4bit (16階調) | 1973/09 | 1,445 |
| ETL2 | 52,796 | 2,184 | ひらがな、カタカナ、英数字、記号、漢字 | 60x60 px | 6bit (64階調) | 1973/10 | - |
| ETL3 | 9,600 | 48 | 数字10、大文字26、記号12 | 72x76 px | 4bit (16階調) | 1974/04 | 200 |
| ETL4 | 6,120 | 51 | ひらがな51 | 72x76 px | 4bit (16階調) | 1974/12 | 120 |
| ETL5 | 10,608 | 51 | カタカナ51 | 72x76 px | - | 1975/02 | 104 (各208サンプル) |
| ETL6 | 157,662 | 114 | カタカナ46、数字10、大文字26、記号32 | 64x63 px | 4bit | 1976/12 | 1,383 |
| ETL7 | 16,800 | 48 | ひらがな46、濁点、半濁点 | 64x63 px | 4bit | - | 175 |
| ETL8B | 153,916 | 956 | ひらがな、漢字 | 64x63 px | 2値 | - | 約161/クラス |
| ETL8G | - | 956 | ひらがな、漢字 | 128x127 px | 多値 | - | - |
| ETL9B | - | 3,036 | ひらがな、JIS第1水準漢字 | 64x63 px | 2値 | - | 200/クラス |
| ETL9G | 607,200 | 3,036 | ひらがな、JIS第1水準漢字 | 128x127 px | 多値 | - | 200/クラス |

**合計: 約120万文字画像**

### フォーマット

- 独自バイナリフォーマット（データセットごとにレコード長が異なる）
- Pythonによる読み出しライブラリあり: https://github.com/CaptainDario/ETLCDB_data_reader
- 画像抽出ユーティリティ: https://github.com/choo/etlcdb-image-extractor

### ライセンス / 利用条件

- 著作権: AIST（産業技術総合研究所）が保有
- **非商用目的のみ無料で使用可能**（登録ユーザーに限る）
- 商用利用は条件交渉が必要
- データの無断再配布・直接リンクの公開は禁止
- 使用時はデータベース名の表記が必要

### 引用情報

> Electrotechnical Laboratory, Japanese Technical Committee for Optical Character Recognition, "ETL Character Database", 1973-1984.

特定のデータセットを引用する場合は「ETL-n Character Database」（nは該当番号）と表記。

### ダウンロード

- 登録フォームで利用条件に同意後、パスワードを取得してダウンロード
- ダウンロードページ: https://etlcdb.db.aist.go.jp/download2/

### メンテナンス状況

- 2011年4月よりインターネット経由のダウンロード提供開始（それ以前は磁気テープ・CD-Rで郵送）
- データ自体の更新はなし（1973-1984年収集のアーカイブ）
- ウェブサイトは稼働中

### ソース
- http://etlcdb.db.aist.go.jp/the-etl-character-database/
- http://etlcdb.db.aist.go.jp/database-development/
- https://github.com/ichisadashioko/etlcdb

---

## 2. KMNIST (Kuzushiji-MNIST)

### 基本情報

| 項目 | 内容 |
|------|------|
| 正式名称 | KMNIST Dataset (Kuzushiji-MNIST) |
| URL | https://codh.rois.ac.jp/kmnist/index.html.en |
| GitHubリポジトリ | https://github.com/rois-codh/kmnist |
| 提供元 | ROIS-DS 人文学オープンデータ共同利用センター (CODH) |
| 原データ | 国文学研究資料館 (NIJL) 等が作成した「くずし字データセット」 |

### データの種類

文字単位。古典籍から抽出されたくずし字（変体仮名）のひらがな10文字クラスの手書き文字画像。MNISTのドロップイン互換データセットとして設計。

### データ量

| 項目 | 値 |
|------|-----|
| 画像サイズ | 28x28 グレースケール |
| 総画像数 | 70,000 |
| クラス数 | 10（ひらがな各行から1文字ずつ） |
| 訓練データ | 60,000（各クラス6,000） |
| テストデータ | 10,000（各クラス1,000） |
| クラスバランス | 完全にバランス済み |

### フォーマット

- MNIST形式（オリジナルMNISTと同一フォーマット）
- NumPy形式（.npz）

### ライセンス

**CC BY-SA 4.0**（クリエイティブ・コモンズ 表示-継承 4.0 国際）

### 引用論文

> Tarin Clanuwat, Mikel Bober-Irizar, Asanobu Kitamoto, Alex Lamb, Kazuaki Yamamoto, David Ha, "Deep Learning for Classical Japanese Literature", arXiv:1812.01718 (NeurIPS 2018 Workshop)

### ダウンロード

- GitHub: https://github.com/rois-codh/kmnist
- `python download_data.py` で対話的にダウンロード可能
- TensorFlow Datasets: https://www.tensorflow.org/datasets/catalog/kmnist
- Kaggle: https://www.kaggle.com/datasets/anokas/kuzushiji

### メンテナンス状況

- 2019年2月5日に画像処理を改善して更新
- NeurIPS 2018で発表

### ソース
- https://codh.rois.ac.jp/kmnist/index.html.en
- https://github.com/rois-codh/kmnist

---

## 3. Kuzushiji-49 / Kuzushiji-Kanji

### Kuzushiji-49

| 項目 | 内容 |
|------|------|
| 正式名称 | Kuzushiji-49 |
| 画像サイズ | 28x28 グレースケール |
| 総画像数 | 270,912 |
| クラス数 | 49（ひらがな48文字 + 踊り字1文字） |
| 訓練データ | 232,365（63MB） |
| テストデータ | 38,547（11MB） |
| クラスバランス | **不均衡**（balanced accuracy推奨） |
| フォーマット | NumPy形式のみ |

### Kuzushiji-Kanji

| 項目 | 内容 |
|------|------|
| 正式名称 | Kuzushiji-Kanji |
| 画像サイズ | 64x64 グレースケール |
| 総画像数 | 140,424 |
| クラス数 | 3,832（漢字） |
| クラスバランス | **高度に不均衡**（1クラスあたり1〜1,766サンプル） |
| フォーマット | tarアーカイブ（310MB） |
| Train/Test分割 | 計画中（未実施） |

### 共通事項

- 提供元・ライセンス・引用情報はKMNISTと同一
- GitHub: https://github.com/rois-codh/kmnist からダウンロード可能
- CC BY-SA 4.0

### ソース
- https://github.com/rois-codh/kmnist
- https://paperswithcode.com/dataset/kuzushiji-49
- https://datasets.activeloop.ai/docs/ml/datasets/kuzushiji-kanji-kkanji-dataset/

---

## 4. 日本古典籍くずし字データセット

### 基本情報

| 項目 | 内容 |
|------|------|
| 正式名称 | 日本古典籍くずし字データセット (Kuzushiji Dataset / Japanese Classical Text Character Shape Dataset) |
| URL | https://codh.rois.ac.jp/char-shape/ |
| 提供元 | ROIS-DS CODH + 国文学研究資料館 (NIJL) |
| 原データ | 日本古典籍データセットの翻刻プロセスで生成 |

### データの種類

文字単位。古典籍（44点）の画像データから切り出したくずし字の字形データ。ひらがな（変体仮名）、カタカナ、漢字を含む。

### データ量

| 項目 | 値 |
|------|-----|
| 文字種数 | 4,328 |
| 文字画像数 | 1,086,326 |
| 対象古典籍 | 44点 |
| ページ数 | 6,151ページ |
| 更新時期 | 2019年11月（大幅拡充: 684,165 → 1,086,326文字） |

### フォーマット

- CSV形式（原本画像上の文字座標＝バウンディングボックス情報）
- 文字画像は原本ページ画像から切り出して利用

### ライセンス

**CC BY-SA 4.0**（クリエイティブ・コモンズ 表示-継承 4.0 国際）

### 引用情報

> 『日本古典籍くずし字データセット』（国文研ほか所蔵／CODH加工） doi:10.20676/00000340

### 機能

- くずし字データベース検索（ひらがな・変体仮名・カタカナ・漢字）
- 文字種ごとのくずし字一覧表示

### メンテナンス状況

- 継続的にデータ拡充が行われている
- KMNISTデータセットの元データとしても使用されている

### ソース
- https://codh.rois.ac.jp/char-shape/
- https://current.ndl.go.jp/car/37494

---

## 5. HANDS データベース (Nakagawa Lab, TUAT)

東京農工大学 中川正樹研究室が収集・配布するオンライン手書きデータベース群。複数のデータベースで構成される。

### 5-1. HANDS-Nakayosi (HANDS-nakayosi_t-98-09)

| 項目 | 内容 |
|------|------|
| 正式名称 | TUAT Nakagawa Lab. HANDS-nakayosi_t-98-09 |
| URL | http://web.tuat.ac.jp/~nakagawa/database/en/about_nakayosi.html |
| 提供元 | 東京農工大学 中川正樹研究室 |
| データの種類 | **オンライン**手書き文字パターン（ストロークデータ） |
| 収集元 | 日本語新聞記事の抜粋テキスト |
| 筆記者数 | 163名 |
| パターン数 | 1,695,689パターン（163名 x 10,403パターン/名） |
| 文字カテゴリ数 | 4,438 |
| 文字種類 | JIS第1水準漢字、約1,000のJIS第2水準漢字（人名用）、ひらがな、カタカナ、英数字、記号等 |
| フォーマット | 独自バイナリ形式、IPDBライブラリで読み出し |
| 言語要件 | 日本語文字コードシステム・フォントが必要 |

### 5-2. HANDS-Kuchibue (HANDS-kuchibue_d-97-06)

| 項目 | 内容 |
|------|------|
| 正式名称 | TUAT Nakagawa Lab. HANDS-kuchibue_d-97-06 |
| URL | http://web.tuat.ac.jp/~nakagawa/database/en/about_kuchibue.html |
| 提供元 | 東京農工大学 中川正樹研究室 |
| データの種類 | **オンライン**手書き文字パターン（ストロークデータ） |
| 筆記者数 | 120名 |
| パターン数 | 1,435,440パターン（120名 x 11,962パターン/名） |
| 文字カテゴリ数 | 3,356 |
| 文字種類 | JIS第1水準漢字、ひらがな、カタカナ、英数字、記号等 |
| フォーマット | バイナリ形式、ASCIIテキスト形式、UNIPEN形式 |

### 5-3. HANDS-Kondate (HANDS-kondate-14-09-01)

| 項目 | 内容 |
|------|------|
| 正式名称 | TUAT Nakagawa Lab. HANDS-kondate-14-09-01 |
| URL | http://web.tuat.ac.jp/~nakagawa/database/en/kondate_about.html |
| 提供元 | 東京農工大学 中川正樹研究室 |
| データの種類 | **オンライン**手書きの混合オブジェクト（テキスト、線画、数式、図表、地図等） |
| 筆記者数 | 日本語100名、英語約25名、タイ語約45名 |
| ページ数 | 約4,200ページ |
| 文字種数 | 3,881 |
| フォーマット | InkML形式（グラウンドトゥルースタグ付き） |
| 引用論文 | M. Matsushita, M. Nakagawa, "A Database of On-line Handwritten Mixed Objects Named Kondate", ICFHR 2014 |

### HANDS共通事項

- **ライセンス**: 学術目的での利用。購入申請が必要
- **入手方法**: 中川教授に直接連絡 (nakagawa@cc.tuat.ac.jp)
- **条件**: 利用時にデータベースの使用を適切に表記すること
- **ドキュメント**: 日本語のみ
- **IPDBライブラリ**: ipdblib.zip (74KB) がダウンロード可能
- データベースポータル: http://web.tuat.ac.jp/~nakagawa/database/index.html
- **OpenVINO**: IntelのOpenVINOモデル `handwritten-japanese-recognition-0001` はNakayosi + Kondateデータセットで訓練（4,441文字対応）

### ソース
- http://web.tuat.ac.jp/~nakagawa/database/index.html
- http://web.tuat.ac.jp/~nakagawa/database/en/about_nakayosi.html
- http://web.tuat.ac.jp/~nakagawa/database/en/about_kuchibue.html
- https://web.tuat.ac.jp/~nakagawa/pub/2014/pdf/Matsushita_ICFHR2014.pdf

---

## 6. JEITA-HP 日本語手書き文字パターンデータベース

### 基本情報

| 項目 | 内容 |
|------|------|
| 正式名称 | JEITA-HP手書き文字パターンデータベース |
| 提供元 | JEITA（一般社団法人 電子情報技術産業協会）/ AIST |
| 関連組織 | 旧・日本電子工業振興協会 (EIAJ) |

### データの種類

手書き日本語文字パターン（オフライン、文字単位）。

### データ量

| 項目 | 値 |
|------|-----|
| 文字種数 | 3,214 |
| 各文字のサンプル数 | 580 |
| 総サンプル数 | 約1,864,120（推定: 3,214 x 580） |

### 比較

- ETL9Bより大規模: ETL9Bは3,036クラス x 200サンプル
- JEITA-HPは3,214クラス x 580サンプル

### ライセンス / 利用条件

- 現在の入手可能性については不明確
- AIST/JEITAへの直接問い合わせが必要と思われる

### 引用・ベンチマーク

- 多くの学術論文で手書き文字認識のベンチマークとして使用
- 98%以上の高い認識率が報告されている
- HANDS-Nakayosiデータベースで訓練したOCRシステムによるJEITA-HPでの認識率は96.26%

### 注意事項

- 公式ウェブページおよび明確なダウンロードURLは確認できず
- ETL文字データベースとの関連性が深い（同じ研究コミュニティで利用）
- 現在のオンライン入手方法は不明（直接問い合わせ推奨）

### ソース
- https://nlpr.ia.ac.cn/2013papers/gjkw/gk27.pdf (ベンチマーク比較論文)
- https://www.mdpi.com/2076-3417/14/1/225

---

## 7. PRMUアルゴリズムコンテスト関連データセット

### 基本情報

| 項目 | 内容 |
|------|------|
| 正式名称 | PRMUアルゴリズムコンテスト (PRMU Algorithm Contest) |
| 主催 | 電子情報通信学会 パターン認識・メディア理解研究会 (IEICE PRMU) |
| URL | https://www.ieice.org/iss/prmu/jpn/alcon.html |

### 手書き文字認識関連の回

#### 第21回 (2017年): 「この文字読めますか？〜くずし字認識にチャレンジ！〜」
- くずし字認識をテーマとしたコンテスト

#### 第23回 (2019年): 「くずし字認識チャレンジ2019」
- サイト: https://sites.google.com/view/alcon2019
- CodaLabで実施、約40名登録、210件の投稿、24件のアルゴリズム応募
- KMNISTデータセットの普及促進に貢献
- 表彰式: 2019年12月19日（大分大学）

### データセットについて

- コンテスト用のデータセットはKMNIST/くずし字データセットをベースにしたものが使用されたと推定
- コンテスト専用の配布条件あり

### ソース
- https://www.ieice.org/iss/prmu/jpn/alcon.html
- https://sites.google.com/view/alcon2019
- http://codh.rois.ac.jp/kuzushiji-challenge/article/20190616-1.html.ja

---

## 8. NDL（国立国会図書館）OCR関連データセット

### 8-1. 文字画像データセット（平仮名73文字版）

| 項目 | 内容 |
|------|------|
| 正式名称 | 文字画像データセット（平仮名73文字版） |
| GitHub | https://github.com/ndl-lab/hiragana_mojigazo |
| 提供元 | 国立国会図書館 NDLラボ |
| データの種類 | 印刷物からの文字画像（平仮名、文字単位） |
| 文字種 | 73文字（平仮名） |
| 総画像数 | 80,000枚 |
| 画像形式 | PNG |
| 各文字の画像数 | 112〜1,285枚（文字により変動） |
| 対象年代 | 1900〜1940年代 |
| ライセンス | PDM 1.0 (Public Domain Mark) |

**ダウンロードURL:**
- 7z: http://lab.ndl.go.jp/dataset/hiragana73.7z (~190MB)
- tar.gz: http://lab.ndl.go.jp/dataset/hiragana73.tar.gz (~193MB)
- zip: http://lab.ndl.go.jp/dataset/hiragana73.zip (~233MB)

### 8-2. 文字画像データセット（漢字300文字版）

| 項目 | 内容 |
|------|------|
| 正式名称 | 文字画像データセット（漢字300文字版） |
| GitHub | https://github.com/ndl-lab/kanji_mojigazo |
| 提供元 | 国立国会図書館 NDLラボ |
| データの種類 | 印刷物からの文字画像（頻出漢字、文字単位） |
| 文字種 | 300文字（漢字） |
| 総画像数 | 146,157枚 |
| 画像形式 | PNG |
| 各文字の画像数 | 117〜1,000枚 |
| 対象年代 | 1900〜1940年代 |
| ライセンス | PDM 1.0 (Public Domain Mark) |

**ダウンロードURL:**
- 7z: http://lab.ndl.go.jp/dataset/kanji300.7z (~371MB)
- tar.gz: http://lab.ndl.go.jp/dataset/kanji300.tar.gz (~373MB)
- zip: http://lab.ndl.go.jp/dataset/kanji300.zip (~446MB)

### 8-3. OCR学習用データセット（著作権保護期間満了分）

| 項目 | 内容 |
|------|------|
| 正式名称 | デジタル化資料のOCR学習用データセット |
| GitHub | https://github.com/ndl-lab/pdmocrdataset-part1 |
| 提供元 | 国立国会図書館 + LINE株式会社 |
| データの種類 | **印刷書籍**（手書きではない）のOCR学習用アノテーション済み画像 |
| 対象 | 1870〜1940年代の著作権保護期間満了資料 |
| 画像数 | 2,713画像 |
| フォーマット | JSON形式（4.8GB、四角形バウンディングボックス＋テキスト転写）、PascalVOC 1.1形式（1.8GB） |
| ライセンス | PDM 1.0 (Public Domain Mark) |

**ダウンロードURL:**
- JSON: https://lab.ndl.go.jp/dataset/pdm_ocr_dataset/line/tosho_all_linejson.zip
- PascalVOC: https://lab.ndl.go.jp/dataset/pdm_ocr_dataset/line/tosho_all_pascalvoc1.1.zip

### 8-4. NDLOCR / NDLOCR-Lite

| 項目 | 内容 |
|------|------|
| 正式名称 | NDLOCR（日本語OCR処理プログラム） |
| 提供元 | 国立国会図書館 |
| ライセンス | CC BY 4.0 |
| NDLOCR ver.2 | 2023年7月リリース |
| NDLOCR-Lite | 2026年2月公開、GPU不要の軽量版、英語テキスト・手書き文字に実験的対応 |
| 対応字種 | 23,026文字種 |
| 全文テキストデータ | 著作権切れ図書28万点のOCR全文テキスト |

### 注意

8-1, 8-2のNDL文字画像データセットは**印刷物からの抽出文字**であり、手書き文字ではない。ただし、歴史的な活字のバリエーションを含み、OCRモデルの訓練に有用。

### ソース
- https://github.com/ndl-lab/hiragana_mojigazo
- https://github.com/ndl-lab/kanji_mojigazo
- https://github.com/ndl-lab/pdmocrdataset-part1
- https://lab.ndl.go.jp/data_set/ocr/

---

## 9. 近代雑誌OCR学習用データセット (CODH)

### 基本情報

| 項目 | 内容 |
|------|------|
| 正式名称 | 近代雑誌OCR学習用データセット |
| URL | https://codh.rois.ac.jp/modern-magazine/dataset/ |
| 提供元 | CODH + 国立国語研究所 |
| データの種類 | 近代雑誌の**印刷テキスト**（行単位の転写テキスト＋座標情報） |
| ページ数 | 1,985ページ |
| 行数 | 59,465行 |
| 文字種数 | 4,935 |
| 総文字数 | 1,472,004文字 |
| サイズ | 2.2GB (Version 1) |
| フォーマット | NDLOCR XML形式 |
| ライセンス | CC BY 4.0 |

### 引用情報

> 『近代雑誌OCR学習用データセット』(CODH・国語研作成) doi:10.20676/00000415

### 関連ソフトウェア

- Kindai-OCR: 近代日本語書籍向けOCRシステム
- GitHub: https://github.com/DeepApps91/Kindai-OCR

### ソース
- https://codh.rois.ac.jp/modern-magazine/dataset/
- https://codh.rois.ac.jp/software/kindai-ocr/

---

## 10. CEDAR Japanese Character Image Database

### 基本情報

| 項目 | 内容 |
|------|------|
| 正式名称 | CEDAR Japanese Character Image Database |
| URL | https://cedar.buffalo.edu/japanese/JOCRdatabase.html |
| 提供元 | CEDAR (Center of Excellence for Document Analysis and Recognition), University at Buffalo |
| データの種類 | **機械印刷**の日本語文字画像（手書きではない） |
| 文字カテゴリ数 | 3,300以上（JIS level-0, level-1） |
| 総画像数 | 約180,000 |
| 文字種類 | 漢字、ひらがな、カタカナ、英数字、記号 |
| ソース | 書籍、FAX、雑誌、レーザープリンタ出力、新聞 |
| 元ドキュメント数 | 264ページ |
| 画像形式 | TIFF (400 ppi, 二値画像) |
| グラウンドトゥルース | 4バイトJISコード |
| 価格 | **$1,500 USD** |
| 提供媒体 | 8mmテープまたはCD-ROM |

### 連絡先

Dr. S. N. Srihari, CEDAR Director
520 Lee Entrance, Suite 202, Amherst, NY 14228-2567
srihari@cedar.Buffalo.EDU

### 注意

このデータベースは**印刷文字**のデータベースであり、手書き文字ではない。

### ソース
- https://cedar.buffalo.edu/japanese/JOCRdatabase.html
- https://cedar.buffalo.edu/Databases/JOCR/

---

## 11. Kaggle Kuzushiji Recognition コンペティション

### 基本情報

| 項目 | 内容 |
|------|------|
| 正式名称 | Kuzushiji Recognition: Opening the Door to A Thousand Years of Japanese Culture |
| URL | https://www.kaggle.com/c/kuzushiji-recognition |
| 開催期間 | 2019年7月19日 〜 2019年10月14日 |
| 主催 | CODH, NII, NIJL 等 |

### データセットの特徴

- 日本古典籍のページ画像とバウンディングボックス付きアノテーション
- 4,300以上のユニークな文字種
- 頻度分布がロングテール（一部の文字は1-2回しか出現しない）
- 変体仮名（1つの現代ひらがなに複数の字形が存在）
- 文字の連結・重なりあり
- 縦書きレイアウト（ルールが一定ではない）

### データ構成

- train_images, test_images（ページ画像）
- train.csv（文字ラベル＋座標）
- unicode_translation.csv

### ライセンス

CC BY-SA 4.0（基本データセットと同様）

### ソース
- https://www.kaggle.com/c/kuzushiji-recognition
- https://codh.rois.ac.jp/competition/kaggle/index.html.en

---

## 12. その他の関連データセット

### 12-1. Nexdata 日本語手書きOCRデータセット

| 項目 | 内容 |
|------|------|
| 名称 | 5147 Images Japanese Handwriting OCR dataset |
| URL | https://www.nexdata.ai/datasets/ocr/1296 |
| GitHub | https://github.com/Nexdata-AI/5147-Images-Japanese-Handwriting-OCR-data |
| データ量 | 5,147画像 |
| アノテーション | 行単位の四角形バウンディングボックス＋テキスト転写 |
| 分野 | 社会生活、エンターテインメント、旅行、スポーツ、映画、作文 |

### 12-2. Nexdata 101人日本語手書きOCRデータ

| 項目 | 内容 |
|------|------|
| 名称 | 101 People 4538 Images Japanese Handwriting OCR Data |
| GitHub | https://github.com/Nexdata-AI/101-People-4538-Images-Japanese-Handwriting-OCR-Data |
| データ量 | 4,538画像、101名の筆記者 |
| アノテーション | 文字レベルの矩形バウンディングボックス＋テキスト転写 |

### 12-3. Kaggle: Handwriting OCR Data of Japanese and Korean

| 項目 | 内容 |
|------|------|
| URL | https://www.kaggle.com/datasets/nexdatafrank/handwriting-ocr-data-of-japanese-and-korean |
| データの種類 | 日本語＋韓国語の手書きOCRデータ |

### 12-4. Kaggle: Handwritten Japanese Hiragana Characters

| 項目 | 内容 |
|------|------|
| URL | https://www.kaggle.com/datasets/farukece/handwritten-japanese-hiragana-characters |
| データの種類 | 手書きひらがな文字画像 |

### 12-5. Japanese-Mobile-Receipt-OCR-1.3K

| 項目 | 内容 |
|------|------|
| 名称 | Japanese-Mobile-Receipt-OCR-1.3K |
| データ量 | 1,300枚のレシート画像、34,727テキストエントリ |
| データの種類 | モバイル撮影の日本語レシート画像 |
| 用途 | 構造化データ抽出 |

---

## データセット比較サマリー

| データセット | 種別 | 文字/行/文書 | 文字種数 | 総画像数 | 手書き/印刷 | ライセンス | 入手性 |
|---|---|---|---|---|---|---|---|
| ETL (ETL1-9) | オフライン | 文字単位 | 〜3,036 | 〜1,200,000 | 手書き+印刷 | 非商用無料(要登録) | 公開(登録制) |
| KMNIST | オフライン | 文字単位 | 10 | 70,000 | 手書き(くずし字) | CC BY-SA 4.0 | 自由DL |
| Kuzushiji-49 | オフライン | 文字単位 | 49 | 270,912 | 手書き(くずし字) | CC BY-SA 4.0 | 自由DL |
| Kuzushiji-Kanji | オフライン | 文字単位 | 3,832 | 140,424 | 手書き(くずし字) | CC BY-SA 4.0 | 自由DL |
| 古典籍くずし字 | オフライン | 文字単位 | 4,328 | 1,086,326 | 手書き(くずし字) | CC BY-SA 4.0 | 自由DL |
| HANDS-Nakayosi | オンライン | 文字単位 | 4,438 | 1,695,689 | 手書き | 学術利用(購入) | 要申請 |
| HANDS-Kuchibue | オンライン | 文字単位 | 3,356 | 1,435,440 | 手書き | 学術利用(購入) | 要申請 |
| HANDS-Kondate | オンライン | 文書単位 | 3,881 | 4,200ページ | 手書き(混合) | 学術利用(購入) | 要申請 |
| JEITA-HP | オフライン | 文字単位 | 3,214 | 〜1,864,120 | 手書き | 要問合せ | 不明 |
| NDL 平仮名73 | オフライン | 文字単位 | 73 | 80,000 | 印刷 | PDM 1.0 | 自由DL |
| NDL 漢字300 | オフライン | 文字単位 | 300 | 146,157 | 印刷 | PDM 1.0 | 自由DL |
| NDL OCR学習用 | オフライン | 行/文書 | - | 2,713 | 印刷 | PDM 1.0 | 自由DL |
| 近代雑誌OCR | オフライン | 行単位 | 4,935 | 59,465行 | 印刷 | CC BY 4.0 | 自由DL |
| CEDAR Japanese | オフライン | 文字単位 | 3,300+ | 180,000 | 印刷 | 有償($1,500) | 購入 |

---

## 用途別推奨

### 手書き文字認識の研究・評価に最適
1. **ETL文字データベース** - 最大規模の日本語手書き文字データ（約120万画像）
2. **HANDS-Nakayosi / Kuchibue** - オンライン手書き文字認識のベンチマーク標準
3. **JEITA-HP** - 手書き文字認識の評価ベンチマークとして広く引用

### 機械学習の入門・教育に最適
1. **KMNIST** - MNISTの直接互換で導入が容易
2. **Kuzushiji-49** - より多くの文字クラスでの挑戦

### くずし字認識に最適
1. **日本古典籍くずし字データセット** - 100万文字超の大規模データ
2. **Kuzushiji-Kanji** - 64x64画像で3,832漢字をカバー
3. **Kaggle Kuzushiji Recognition** - ページレベルの認識タスク

### 自由にダウンロード可能なデータセット（ライセンスが緩い順）
1. NDLデータセット群（PDM 1.0 = パブリックドメイン）
2. KMNIST / Kuzushiji系（CC BY-SA 4.0）
3. 近代雑誌OCR（CC BY 4.0）
4. ETL文字データベース（非商用無料、要登録）
