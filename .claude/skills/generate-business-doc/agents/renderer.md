# renderer サブエージェント

## 役割

content-generator が生成したデータを元に、**ユニークな HTML/CSS レイアウト** を LLM で生成し、Playwright で PNG 画像化する。

## 処理フロー

1. 各ドキュメントのデータを受け取る
2. **LLM がデータに基づいてフルの HTML/CSS を生成**（固定テンプレート不使用）
3. `dataset/{type}/{id}.html` に HTML を保存
4. Playwright で HTML → PNG スクリーンショット
5. `dataset/{type}/{id}.png` を保存

## Playwright 設定

文書タイプ別の viewport サイズ:

| タイプ | viewport | 備考 |
|--------|----------|------|
| invoice | 794 x 1123 | A4 @96dpi, device_scale_factor=2 (実質192dpi) |
| receipt | 220 or 300 x auto (full_page) | 58mm=220px / 80mm=300px, metadata.paper_width で判定, device_scale_factor=2 |
| business_card | 346 x 210 | 名刺サイズ (91mm x 55mm @96dpi), device_scale_factor=2 |

## HTML 生成ガイドライン

### 共通必須要件

- **viewport に収まる**: CSS で `body { margin: 0; width: {viewport.width}px; }` を基本に
- **self-contained**: 外部リソースは Google Fonts のみ。画像・ロゴは CSS で表現
- **データの正確な反映**: ground_truth の全フィールド値が画像上に表示されること

### フォント

タイプによって使い分ける:

- **Invoice / Business Card**: Noto Sans JP
  ```html
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;700&display=swap" rel="stylesheet">
  ```
- **Receipt**: M PLUS 1 Code（モノスペース）を基本、Noto Sans JP を補助
  ```html
  <link href="https://fonts.googleapis.com/css2?family=M+PLUS+1+Code:wght@400;700&family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
  ```
  CSS: `font-family: 'M PLUS 1 Code', 'Noto Sans JP', monospace;`

---

## Invoice (請求書) レンダリング

metadata の `layout_style` に応じてスタイルを変える。diversity.md を参照。

各ドキュメントで以下を変えること:
- **配色**: モノクロ / ブルー系 / グレー系 / グリーン系
- **罫線**: 実線 / 破線 / なし / 二重線
- **ヘッダー配置**: 左寄せ / 中央 / 右寄せ
- **テーブルスタイル**: ボーダー付き / ストライプ / ミニマル
- **日付表示形式**: `2026年3月17日` / `2026/03/17` / `令和8年3月17日`
- **フォントサイズ・余白**: 文書ごとに微調整

構成要素:
- ヘッダー: 請求先名、「御中」、請求元情報
- メタ情報: 請求書番号、発行日、支払期限
- 明細テーブル: No, 品目, 数量, 単位, 単価, 金額
- 合計: 小計, 消費税, 合計金額
- 振込先情報
- 備考

---

## Receipt (領収書/レシート) レンダリング

**重要**: レシートは **POS 端末のサーマルプリンタで印字された外観** を再現すること。
Web デザインのような見た目は厳禁。コンビニ・スーパー・飲食店で受け取る感熱紙レシートを忠実に模倣する。

### 絶対禁止事項

以下は **すべてのレシートで禁止**:

- ❌ 背景色付きヘッダーバー（白以外の背景色全般）
- ❌ カード風のボーダーやボックスシャドウ
- ❌ 丸角（border-radius）
- ❌ カラーアクセント（青・緑・茶色・暖色系の色付け）
- ❌ HTML `<table>` 要素（flexbox か text-align で配置する）
- ❌ ストライプ背景（交互背景色）
- ❌ ラベル付き装飾ボックス（「請求先」枠囲み等）
- ❌ グラデーション
- ❌ 複数カラムの grid レイアウト

### 必須制約

- **配色**: 黒テキスト (#000 〜 #333) + 白背景 (#fff) のみ
- **フォント**: `'M PLUS 1 Code', monospace` を基本。等幅フォントでサーマル印字感を出す
- **区切り線**: CSS border は一切使わない。**テキスト文字の繰り返し** で区切り線を表現する
  ```
  ━━━━━━━━━━━━━━━━━━━━━━━━━━
  ────────────────────────────
  ＝＝＝＝＝＝＝＝＝＝＝＝＝＝
  ********************************
  ----------------------------------------
  ```
- **padding**: body に左右 8〜12px 程度の控えめな余白のみ
- **line-height**: 1.4〜1.6（サーマル紙の行間）

### レイアウト構成（上から順に）

```
┌──────────────────────┐
│   店舗名（中央・大きめ）      │
│   住所（中央・小さめ）        │
│   TEL: xxx-xxx-xxxx        │
│ ━━━━━━━━━━━━━━━━━━━━━━ │
│ 登録番号: Txxxxxxxxxxxxx    │
│ No. xxx  2026/03/17 12:34  │
│ ━━━━━━━━━━━━━━━━━━━━━━ │
│ 品名               ¥1,000  │
│   2 × ¥500                │
│ 品名                 ¥800  │
│ ────────────────────── │
│ 小計               ¥1,800  │
│ (税8%対象 ¥1,000  税 ¥80)  │
│ (税10%対象 ¥800  税 ¥80)   │
│ ━━━━━━━━━━━━━━━━━━━━━━ │
│ 合計             ¥1,960    │
│ (うち消費税       ¥160)    │
│ ━━━━━━━━━━━━━━━━━━━━━━ │
│ お支払い: 現金              │
│ お預かり: ¥2,000            │
│ お釣り:   ¥40               │
│ ────────────────────── │
│ ご来店ありがとうございました│
└──────────────────────┘
```

### 商品明細の表示パターン

多様性のために以下のパターンを使い分ける:

**パターン A: 1行表示**
```
日替わり定食           ¥950
生ビール              ¥600
```

**パターン B: 2行表示（品名 + 数量×単価）**
```
日替わり定食
  2 × ¥950           ¥1,900
生ビール中ジョッキ
  2 × ¥600           ¥1,200
```

**パターン C: 品名横に数量**
```
日替わり定食     x2   ¥1,900
生ビール中ジョッキ x2 ¥1,200
```

### 合計の強調方法

以下のいずれかで合計を目立たせる（カラーは使わない）:

- **大きいフォントサイズ**（他の行の 1.5〜2 倍）
- **反転表示**（黒背景 + 白文字の 1 行のみ。これだけは背景色 OK）
- **二重の区切り線で囲む**（`━━━` で上下を挟む）
- **太字 + letter-spacing**

### バリエーションの出し方

レシートの多様性は以下の軸で出す（metadata に記録）:

| 軸 | バリエーション |
|---|---|
| 区切り文字 | `━` / `─` / `＝` / `*` / `-` |
| 金額フォーマット | `¥1,000` / `1,000円` / `￥1,000` |
| 明細表示 | パターン A / B / C |
| 合計強調 | 大フォント / 反転 / 二重線 / 太字 |
| 日時形式 | `2026/03/17 12:34` / `2026年03月17日` / `R8.03.17` |
| 用紙幅 | 58mm (220px) / 80mm (300px) |

---

## Business Card (名刺) レンダリング

構成要素:
- 会社名（日/英）
- 部署、役職
- 氏名（大きめ）、読み
- 連絡先: 住所、電話、FAX、携帯、メール、Web

名刺の多様性は diversity.md のレイアウトスタイル（配色・罫線・ヘッダー配置等）を参照。

## 実装パターン

```python
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

DATASET_DIR = Path("structured_eval/dataset")

VIEWPORT_SETTINGS = {
    "invoice": {"width": 794, "height": 1123},
    "receipt_80mm": {"width": 300, "height": 1},
    "receipt_58mm": {"width": 220, "height": 1},
    "business_card": {"width": 346, "height": 210},
}


def render_document(doc_type: str, doc_id: str, html: str, paper_width: str = "80mm"):
    """Render HTML to PNG using Playwright."""
    output_dir = DATASET_DIR / doc_type
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save HTML
    html_path = output_dir / f"{doc_id}.html"
    html_path.write_text(html, encoding="utf-8")

    # Determine viewport
    if doc_type == "receipt":
        vp_key = f"receipt_{paper_width}"
        vp = VIEWPORT_SETTINGS.get(vp_key, VIEWPORT_SETTINGS["receipt_80mm"])
    else:
        vp = VIEWPORT_SETTINGS.get(doc_type, {"width": 794, "height": 1123})

    png_path = output_dir / f"{doc_id}.png"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": vp["width"], "height": vp["height"]},
            device_scale_factor=2,
        )
        page.set_content(html, wait_until="networkidle")

        if doc_type == "receipt":
            page.screenshot(path=str(png_path), full_page=True)
        else:
            page.screenshot(
                path=str(png_path),
                clip={"x": 0, "y": 0, "width": vp["width"], "height": vp["height"]},
            )
        browser.close()
```

## 注意事項

- Playwright のインストールが必要: `npx playwright install chromium`
- Noto Sans JP フォントは Web フォントとして読み込むため、ネットワーク接続が必要
- `wait_until="networkidle"` でフォント読み込みを待つ
- HTML は完全な `<!DOCTYPE html>` から始まる self-contained な文書であること
- 各ドキュメントの HTML は **必ず異なるレイアウト** にすること（コピペ禁止）
