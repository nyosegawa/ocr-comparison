---
name: generate-business-doc
description: >
  活字ビジネス文書（請求書・領収書・名刺）の合成データを生成する。
  LLM の創造性でリアルな日本語ビジネスデータとユニークなレイアウト (HTML/CSS) を生成し、
  Playwright で画像化する。
  Use when: "データ生成", "generate-business-doc", "合成データ", "ビジネス文書生成",
  "請求書生成", "領収書生成", "名刺生成", "structured_eval データ"
compatibility: Requires Playwright (npx playwright install chromium), structured_eval/ directory
---

# ビジネス文書合成データ生成

## 概要

`structured_eval/dataset/` にビジネス文書の 4 点セットを生成する:

1. **JSON Schema** (`schema.json`) — 型ごとの正解データ構造定義
2. **JSON データ** (`{id}.json`) — 正解データ
3. **HTML レイアウト** (`{id}.html`) — LLM が生成したユニークなレイアウト
4. **PNG スクリーンショット** (`{id}.png`) — HTML を Playwright でレンダリング

## Instructions

### Step 1: マニフェスト確認

まず現在のデータセットの状態を確認する:

```bash
cat structured_eval/dataset/manifest.json 2>/dev/null || echo '{"generated":[],"coverage":{}}'
```

生成済みデータのカバレッジを把握し、未カバーの組み合わせを優先する。

### Step 2: content-generator サブエージェントを起動

Agent tool で `content-generator` サブエージェントを起動する。
プロンプトに以下を含める:

1. 生成する文書タイプ（invoice / receipt / business_card）
2. 生成数
3. 現在のマニフェストのカバレッジ情報
4. `references/diversity.md` と `references/schemas.md` の内容

サブエージェントは **JSON Schema** と **JSON データ配列** を返す。

- 初回生成時: Pydantic スキーマ (`structured_eval/src/schemas/`) を参考に JSON Schema を生成
- 追加生成時: 既存の `{type}/schema.json` を読み込んで準拠

`schema.json` が存在しない場合、サブエージェントの出力をもとに `{type}/schema.json` を保存する。

### Step 3: renderer サブエージェントを起動

content-generator の出力（JSON データ配列）を受け取り、Agent tool で `renderer` サブエージェントを起動する。
renderer は:

1. 各ドキュメントのデータを元に **ユニークな HTML/CSS レイアウト** を LLM で生成
2. `dataset/{type}/{id}.html` を保存
3. Playwright で HTML → PNG スクリーンショット (`device_scale_factor=2`)
4. `dataset/{type}/{id}.png` を保存

**重要**: 固定テンプレート (Jinja2) は使わない。LLM が毎回新しいレイアウトを生成する。

### Step 4: マニフェスト更新

生成されたデータの情報を `manifest.json` に追加し、カバレッジを更新する。

### Step 5: 完了報告

生成されたファイル一覧とカバレッジの更新状況を報告する。

## 引数

ユーザーが以下のように指定できる:

- `/generate-business-doc` — 各タイプ3枚ずつ、カバレッジが薄い組み合わせ優先
- `/generate-business-doc invoice 5` — 請求書を5枚
- `/generate-business-doc receipt 10` — 領収書を10枚
- `/generate-business-doc business_card 5` — 名刺を5枚

## Examples

### Example 1: 初回生成

User: `/generate-business-doc`

1. manifest.json が空なので全タイプ均等に生成
2. 業種・地域・規模・レイアウトスタイルをバラけさせる
3. 各タイプ3枚 × 3タイプ = 9枚生成
4. 各タイプの schema.json を生成・保存

### Example 2: 追加生成

User: `/generate-business-doc invoice 5`

1. manifest の coverage を確認
2. 既存の `invoice/schema.json` を読み込み準拠
3. IT業種が多ければ製造・建設・医療を優先
4. レイアウトスタイルも既存と被らないようにする
5. 請求書を5枚追加生成
