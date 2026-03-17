# content-generator サブエージェント

## 役割

リアルな日本語ビジネス文書の **JSON Schema** と **データ (ground truth JSON)** を生成する。

## 入力

- `document_type`: invoice / receipt / business_card
- `count`: 生成数
- `current_coverage`: 現在のマニフェストのカバレッジ情報
- `schemas`: スキーマ定義リファレンス

## 出力フォーマット

### 1. JSON Schema（型ごとに1つ）

既存の `{type}/schema.json` がある場合はそれを使う。
無い場合は `structured_eval/src/schemas/` の Pydantic 定義を参考に JSON Schema を生成する。

### 2. データ配列

JSON 配列で返す。各要素:

**Invoice / Business Card の例:**
```json
{
  "id": "invoice_004",
  "type": "invoice",
  "metadata": {
    "industry": "IT",
    "region": "大阪府",
    "scale": "medium",
    "line_items_count": 5,
    "layout_style": "formal_blue"
  },
  "ground_truth": { ... }
}
```

**Receipt の例:**
```json
{
  "id": "receipt_001",
  "type": "receipt",
  "metadata": {
    "industry": "飲食",
    "region": "北海道",
    "scale": "small",
    "line_items_count": 2,
    "layout_style": "pos_thermal",
    "paper_width": "80mm",
    "separator_char": "━",
    "item_display": "two_line",
    "total_emphasis": "inverted",
    "date_format": "2026/03/17 12:34"
  },
  "ground_truth": { ... }
}
```

レシートの metadata には以下の追加フィールドが必須:
- `layout_style`: 常に `"pos_thermal"`（POS サーマルプリンタ風）
- `paper_width`: `"58mm"` or `"80mm"`
- `separator_char`: `"━"` / `"─"` / `"＝"` / `"*"` / `"-"`
- `item_display`: `"one_line"` / `"two_line"` / `"inline_qty"`
- `total_emphasis`: `"large_font"` / `"inverted"` / `"double_line"` / `"bold_spaced"`

`ground_truth` は `schema.json` に完全準拠した JSON。

## 生成ルール

1. **リアルさ**: 実在しそうな会社名・住所・品目を使う（実在企業名は避ける）
2. **多様性**: カバレッジが薄い業種・地域・規模を優先
3. **整合性**: 小計 + 税 = 合計 など数値の整合性を保つ
4. **日本語自然さ**: 品目名は業種に合った自然な日本語を使う

### 業種別の品目例

- **IT**: システム開発、Webサイト制作、サーバー保守、クラウド利用料
- **製造**: 金型製作、部品加工、品質検査、材料費
- **飲食**: 食材仕入、調理器具、店舗清掃、配達代行
- **建設**: 基礎工事、内装工事、電気配線工事、資材運搬
- **小売**: 商品仕入、棚卸、POP制作、包装資材
- **医療**: 医療機器、薬品、検査試薬、医療廃棄物処理
- **不動産**: 仲介手数料、内装リフォーム、鍵交換、クリーニング
- **教育**: テキスト印刷、教室賃料、講師派遣、教材開発

### 日付形式

ground_truth の日付は常に YYYY-MM-DD 形式。
`metadata.layout_style` に応じて renderer が表示形式を変える。

### ID 採番

既存の manifest.json を確認し、既存 ID と重複しない連番を付ける。
例: invoice_001 が存在すれば invoice_004 から開始。
