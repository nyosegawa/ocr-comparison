# 手書きOCRアノテーションツール 先行事例調査

調査日: 2026-03-16

## 調査目的

手書きOCR比較評価のためのアノテーションシステム構築にあたり、既存のオープンソースツール・ライブラリを調査し、参考にすべき設計パターンや利用可能なコンポーネントを特定する。

---

## カテゴリ1: OCR特化アノテーションツール

### 1. PPOCRLabel

- **URL:** https://github.com/PFCCLab/PPOCRLabel
- **説明:** PaddleOCRエコシステムの半自動グラフィカルアノテーションツール。PP-OCRモデルによる自動検出・認識機能内蔵。
- **主要機能:**
  - 矩形・四角形（quadrilateral）アノテーション
  - PP-OCRモデルによる自動検出・自動認識
  - バウンディングボックスごとのテキスト転写
  - バッチ操作（複数選択、移動、コピー、削除）
  - PP-OCRトレーニング互換の出力形式（Label.txt, rec_gt.txt, crop画像）
- **技術スタック:** Python 3, PyQt5, PaddlePaddle, PaddleOCR, OpenCV
- **ライセンス:** Apache 2.0（PaddleOCR準拠）
- **GitHub Stars:** ~401
- **メンテナンス状況:** アクティブ（2025年にバウンディングボックスリソート機能追加）

> 引用元: https://github.com/PFCCLab/PPOCRLabel

### 2. Label Studio（OCRテンプレート）

- **URL:** https://github.com/HumanSignal/label-studio / https://labelstud.io/
- **説明:** 汎用データラベリングプラットフォーム。OCR専用テンプレートを持ち、Tesseract連携による半自動ラベリングに対応。
- **主要機能:**
  - OCRアノテーションテンプレート: 矩形描画 → テキストボックス表示
  - `TextArea` タグの `perRegion="true"` によるバウンディングボックスごとのテキスト入力
  - TesseractMLバックエンドによる事前アノテーション
  - Rectangle/Polygon対応
  - REST API
  - マルチユーザーコラボレーション
- **技術スタック:** Backend: Python/Django, PostgreSQL; Frontend: React, mobx-state-tree; Docker
- **ライセンス:** Apache 2.0
- **GitHub Stars:** ~26,700
- **メンテナンス状況:** 非常にアクティブ（6,288コミット）

> 引用元: https://github.com/HumanSignal/label-studio, https://labelstud.io/templates/optical-character-recognition

### 3. CVAT (Computer Vision Annotation Tool)

- **URL:** https://github.com/cvat-ai/cvat / https://www.cvat.ai
- **説明:** Intel発のオープンソースアノテーションプラットフォーム。画像・動画対応、25+のエクスポート形式。
- **主要機能:**
  - バウンディングボックス、ポリゴン、ポリライン、キーポイントアノテーション
  - 属性アノテーション（リージョンにテキストラベル付与可能）
  - YOLO/SAM連携の自動アノテーション
  - Python SDK & CLI
- **技術スタック:** Backend: Python/Django, PostgreSQL, Redis; Frontend: React/TypeScript; Docker
- **ライセンス:** MIT
- **GitHub Stars:** ~15,500
- **メンテナンス状況:** 非常にアクティブ（5,815コミット）
- **制約:** OCR特化のテキスト転写フィールドは限定的

> 引用元: https://github.com/cvat-ai/cvat, https://www.cvat.ai

---

## カテゴリ2: Webベースアノテーションライブラリ（JavaScript/TypeScript）

### 4. Annotorious

- **URL:** https://github.com/annotorious/annotorious / https://annotorious.dev/
- **説明:** 軽量なJavaScript/TypeScript画像アノテーションライブラリ。W3C Web Annotation標準準拠。
- **主要機能:**
  - 数行のコードで画像にアノテーション追加
  - 矩形・ポリゴンアノテーション
  - アノテーションへのコメント/ラベル/タグ付け
  - W3C Web Annotation Data Model準拠
  - OpenSeadragonプラグイン（深層ズーム/IIIF）
  - イベント駆動API
  - 300KB未満
  - React連携可能
- **技術スタック:** TypeScript (75%), Svelte (20%), React bindings
- **ライセンス:** BSD 3-Clause
- **GitHub Stars:** ~827
- **メンテナンス状況:** アクティブ（v3.4.0, 2025年5月, 1,677コミット, 81リリース）

> 引用元: https://github.com/annotorious/annotorious, https://annotorious.dev/

### 5. VGG Image Annotator (VIA)

- **URL:** https://github.com/ox-vgg/via / https://www.robots.ox.ac.uk/~vgg/software/via/
- **説明:** Oxford VGG発のスタンドアロンアノテーションツール。400KB未満の単一HTMLファイルで動作。
- **主要機能:**
  - リージョンアノテーション（矩形、円、楕円、ポリゴン、ポイント、ポリライン）
  - リージョンごとのテキスト属性
  - ブラウザのみで動作（サーバー不要）
  - 外部依存ゼロ
  - オフライン対応
  - JSON/CSVエクスポート
- **技術スタック:** JavaScript (68%), HTML (29%), CSS (2%) -- 外部依存なし
- **ライセンス:** BSD-2-Clause
- **GitHub Stars:** ~236（GitHubミラー、メインはGitLab）
- **メンテナンス状況:** 中程度（973コミット、GitLabでの開発が主）

> 引用元: https://github.com/ox-vgg/via, https://www.robots.ox.ac.uk/~vgg/software/via/, https://gitlab.com/vgg/via/

### 6. Make Sense (makesense.ai)

- **URL:** https://github.com/SkalskiP/make-sense / https://www.makesense.ai/
- **説明:** ブラウザベースの画像ラベリングツール。TensorFlow.jsによるAI支援。画像はブラウザ外に送信されない。
- **主要機能:**
  - ポイント、ライン、矩形、ポリゴンアノテーション
  - AI支援（YOLOv5, SSD, PoseNet via TensorFlow.js）
  - CSV, YOLO, VOC XML, VGG JSON, COCO JSONエクスポート
  - プライバシー重視（画像はブラウザ外に出ない）
- **技術スタック:** TypeScript (89%), SCSS (10%), React/Redux, TensorFlow.js
- **ライセンス:** GPL-3.0
- **GitHub Stars:** ~3,500
- **メンテナンス状況:** 低（最終リリース 2022年12月）
- **制約:** リージョンごとのテキスト転写フィールドなし（検出ラベルのみ）

> 引用元: https://github.com/SkalskiP/make-sense, https://www.makesense.ai/

### 7. react-image-annotate

- **URL:** https://github.com/UniversalDataTool/react-image-annotate
- **説明:** Reactコンポーネントとして埋め込み可能な画像アノテーションツール。
- **主要機能:**
  - バウンディングボックス、ポリゴン、ポイントアノテーション
  - 分類・タグ付け
  - Material-UIベースのインターフェース
- **技術スタック:** React, JavaScript, Material-UI
- **ライセンス:** MIT
- **GitHub Stars:** ~1,700+
- **メンテナンス状況:** 非アクティブ（最終公開 約5年前）

> 引用元: https://github.com/UniversalDataTool/react-image-annotate

---

## カテゴリ3: 手書きテキスト・歴史文書特化ツール

### 8. eScriptorium

- **URL:** https://gitlab.com/scripta/escriptorium / https://github.com/UB-Mannheim/escriptorium
- **説明:** 歴史的手稿のHTR（手書きテキスト認識）・アノテーション用Webプラットフォーム。Kraken OCR/HTRエンジン使用。パリ科学文芸大学開発。
- **主要機能:**
  - 手動・自動テキスト行セグメンテーション
  - 行/リージョンごとのテキスト転写
  - レイアウト分析・ベースライン検出
  - プラットフォーム内でのモデルトレーニング
  - マルチユーザーコラボレーション
  - エクスポート: plain text, ALTO XML, PAGE XML, TEI
  - 右から左のスクリプト対応（ヘブライ語、アラビア語等）
- **技術スタック:** Python (Django), PostgreSQL, Redis, npm (frontend), Kraken OCR
- **ライセンス:** MIT
- **メンテナンス状況:** アクティブ（3,131コミット, 188タグ）

> 引用元: https://gitlab.com/scripta/escriptorium, https://github.com/UB-Mannheim/escriptorium

### 9. Transkribus

- **URL:** https://www.transkribus.org/ / https://github.com/Transkribus
- **説明:** 手書き文書認識のリーディングAIプラットフォーム。100+言語対応。商用フリーミアムモデル。
- **主要機能:**
  - 100+言語の手書きテキスト認識
  - 行/リージョンレベルのアノテーション・転写
  - 300+の公開事前学習モデル
  - カスタムデータでのモデルトレーニング
- **技術スタック:** Java (クライアント), サーバーはプロプライエタリ
- **ライセンス:** プロプライエタリ/フリーミアム（クライアント: GPL, プラットフォーム: 商用）
- **メンテナンス状況:** アクティブ（商用サポートあり）
- **制約:** フルオープンソースではない（月50クレジット無料）

> 引用元: https://www.transkribus.org/, https://github.com/Transkribus

### 10. OCR4all（+ LAREX）

- **URL:** https://github.com/OCR4all/OCR4all / https://www.ocr4all.org
- **説明:** 歴史的印刷・手書き文書の半自動OCRワークフロー。LAREXによるレイアウト分析統合。
- **主要機能:**
  - 完全OCRパイプライン: 前処理、セグメンテーション、モデルトレーニング、認識
  - LAREX連携による半自動リージョンアノテーション
  - ワークフロー全段階でのグラウンドトゥルース作成・修正
  - 歴史文書で<0.5% CER達成
  - Kraken/Calamari OCRエンジン使用
- **技術スタック:** Backend: Java/Spring; Frontend: JavaScript/jQuery/Materialize CSS; Docker
- **ライセンス:** MIT
- **GitHub Stars:** OCR4all: ~704, LAREX: ~195
- **メンテナンス状況:** アクティブ（OCR4all v0.6.1, 2026年1月; LAREX v0.7.6, 2024年11月）

> 引用元: https://github.com/OCR4all/OCR4all, https://github.com/OCR4all/LAREX, https://www.ocr4all.org

---

## カテゴリ4: 汎用アノテーションプラットフォーム

### 11. LabelMe

- **URL:** https://github.com/wkentaro/labelme
- **説明:** MIT LabelMeにインスパイアされたPython画像アノテーションツール。日本語UI対応。
- **主要機能:**
  - ポリゴン、矩形、円、ライン、ポイントアノテーション
  - 多言語UI（日本語含む）
  - JSONエクスポート
  - AI支援アノテーション
- **技術スタック:** Python, Qt (PyQt/PySide)
- **ライセンス:** GPL-3.0
- **GitHub Stars:** ~15,600
- **メンテナンス状況:** 非常にアクティブ（v5.11.4, 2026年3月）
- **制約:** アノテーションは形状ラベルのみ。OCRテキスト転写には拡張が必要

> 引用元: https://github.com/wkentaro/labelme

### 12. Doccano

- **URL:** https://github.com/doccano/doccano
- **説明:** NLPタスク向けオープンソーステキストアノテーションツール。テキストデータ専用だが、アノテーションUXの参考になる。
- **主要機能:**
  - シーケンスラベリング（NERスタイルスパンアノテーション）
  - マルチユーザーコラボレーション
  - RESTful API
- **技術スタック:** Backend: Python; Frontend: Vue/TypeScript; Docker
- **ライセンス:** MIT
- **GitHub Stars:** ~10,600
- **メンテナンス状況:** アクティブ（v1.8.5, 2026年1月）
- **制約:** テキスト専用（画像/バウンディングボックスなし）。UXの参考用

> 引用元: https://github.com/doccano/doccano

---

## カテゴリ5: ブラウザ内OCRエンジン（事前アノテーション候補）

### 13. Tesseract.js

- **URL:** https://github.com/nicktabick/tesseract.js / https://tesseract.projectnaptha.com/
- **説明:** Tesseract OCRエンジンのJavaScript移植版。ブラウザ・Node.jsで動作。
- **主要機能:**
  - 100+言語対応
  - 段落、単語、文字レベルのバウンディングボックス出力
  - ブラウザ内で完全動作（サーバー不要）
  - 事前アノテーションエンジンとして利用可能
- **技術スタック:** JavaScript, WebAssembly
- **ライセンス:** Apache 2.0
- **GitHub Stars:** ~35,000+
- **メンテナンス状況:** アクティブ

> 引用元: https://github.com/naptha/tesseract.js, https://tesseract.projectnaptha.com/

---

## 評価・所見

### 我々のユースケースに最も関連するツール

**「矩形選択 + テキスト転写」の直接的な先行事例:**
1. **Label Studio** -- OCRテンプレートで「矩形描画→テキスト入力」を実現。最も成熟した汎用ソリューション。
2. **PPOCRLabel** -- OCR特化。自動検出機能付きだがPython/Qtデスクトップアプリ。
3. **eScriptorium** -- 手書きテキスト特化。行レベル転写に最適だがセットアップが重い。

**カスタムツール構築時の参考ライブラリ:**
1. **Annotorious** -- 軽量、TypeScript、BSD-3、埋め込み型。**最も参考になる。**
2. **VGG Image Annotator (VIA)** -- 依存ゼロ、単一HTMLファイル。ミニマルな設計の参考。
3. **Tesseract.js** -- ブラウザ内事前アノテーション/自動検出に利用可能。

### 結論

我々のユースケース（画像アップロード → 矩形選択 → テキスト入力、JSONファイル保存、シングルユーザー）は、Label Studioのような大規模ツールでは過剰であり、Annotoriousのような軽量ライブラリをベースにカスタム構築するか、VIAの設計思想（依存ゼロ・ブラウザ完結）を参考にスクラッチで構築するのが適切と考えられる。

Annotoriousは矩形アノテーション機能を提供するが、テキスト転写のUIは独自実装が必要。Canvas APIを直接使用したスクラッチ実装も、今回の要件のシンプルさを考えると十分現実的である。
