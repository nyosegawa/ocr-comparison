---
name: visual-check
description: >
  agent-browser でアクセシビリティツリーを取得し、UI 構造を機械的に検証する。
  CLS 測定、アニメーション完了待ち、スナップショット比較。
  Use when: "UI確認", "見た目チェック", "コンポーネント検証", "visual check",
  "accessibility tree", "CLS", "アクセシビリティ", "スナップショット".
---

# Visual Component Check

## Prerequisites

- Dev server 起動中 (http://localhost:5191)
- agent-browser インストール済み: `npx agent-browser install`

## Instructions

### Step 1: dev server 確認

```bash
curl -sf http://localhost:5191 || echo "dev server is not running on port 5191"
```

### Step 2: アクセシビリティツリー取得

```bash
npx agent-browser open http://localhost:5191
npx agent-browser snapshot
```

snapshot 出力の読み方:
- `@e1`, `@e2`... = 要素参照。以降のコマンドで使える
- `role=button`, `role=textbox` 等で要素の意味を確認
- name 属性で表示テキストを確認

### Step 3: インタラクション検証

```bash
npx agent-browser fill @e5 "test input"
npx agent-browser click @e7
npx agent-browser snapshot   # 操作後の状態確認
```

### Step 4: CLS 測定

```bash
npx agent-browser eval "
  let cls = 0;
  new PerformanceObserver(l => {
    for (const e of l.getEntries()) { if (!e.hadRecentInput) cls += e.value; }
  }).observe({type:'layout-shift',buffered:true});
  await new Promise(r => setTimeout(r, 1000));
  cls;
"
```

目標: CLS < 0.1 (Good)

### Step 5: アニメーション完了待ち

```bash
npx agent-browser eval "
  await Promise.all(
    document.getAnimations({subtree:true}).map(a => a.finished)
  );
  'animations complete';
"
```

### Step 6: スクリーンショット（必要時）

```bash
npx agent-browser screenshot /tmp/component.png
```

## Troubleshooting

- **agent-browser: command not found**: `npx agent-browser install` を実行
- **snapshot が空**: ページロード待ち不足。`npx agent-browser eval "await new Promise(r => setTimeout(r, 2000))"` 後に再試行
- **CLS が高い**: 画像の width/height 未指定、フォント FOUT、動的コンテンツ挿入を確認
