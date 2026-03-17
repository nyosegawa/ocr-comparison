# スキーマ定義リファレンス

各文書タイプの JSON Schema は `structured_eval/dataset/{type}/schema.json` に保存される。
初回生成時は `structured_eval/src/schemas/` の Pydantic 定義を参考に生成する。

## Invoice (請求書)

必須フィールド: `vendor_name`, `total_amount`, `line_items[].description`, `line_items[].amount`

```
invoice_number: str | null     — 請求書番号
issue_date: str | null         — 発行日 (YYYY-MM-DD)
due_date: str | null           — 支払期限 (YYYY-MM-DD)
vendor_name: str               — 請求元の会社名
vendor_address: str | null     — 請求元の住所
vendor_phone: str | null       — 請求元の電話番号
vendor_registration_number: str | null — 登録番号 (T+13桁)
client_name: str | null        — 請求先の会社名
client_address: str | null     — 請求先の住所
line_items: list               — 明細行
  description: str             — 品目名
  quantity: float | null       — 数量
  unit: str | null             — 単位
  unit_price: float | null     — 単価
  amount: float                — 金額
subtotal: float | null         — 小計
tax_rate: float | null         — 消費税率 (0.10)
tax_amount: float | null       — 消費税額
total_amount: float            — 合計金額
bank_name: str | null          — 振込先銀行名
bank_branch: str | null        — 振込先支店名
bank_account_type: str | null  — 口座種別
bank_account_number: str | null — 口座番号
bank_account_holder: str | null — 口座名義
notes: str | null              — 備考
```

## Receipt (領収書)

必須フィールド: `store_name`, `total_amount`, `line_items[].description`, `line_items[].amount`

```
receipt_number: str | null     — 領収書番号
issue_date: str | null         — 発行日 (YYYY-MM-DD)
store_name: str                — 店舗名
store_address: str | null      — 店舗住所
store_phone: str | null        — 電話番号
store_registration_number: str | null — 登録番号
client_name: str | null        — 宛名
line_items: list               — 明細行
  description: str             — 品目名
  quantity: float | null       — 数量
  unit_price: float | null     — 単価
  amount: float                — 金額
subtotal: float | null         — 小計
tax_rate_8: float | null       — 8%対象額
tax_amount_8: float | null     — 8%消費税額
tax_rate_10: float | null      — 10%対象額
tax_amount_10: float | null    — 10%消費税額
total_amount: float            — 合計金額
payment_method: str | null     — 支払方法
notes: str | null              — 備考
```

## BusinessCard (名刺)

必須フィールド: `person_name`

```
person_name: str               — 氏名
person_name_reading: str | null — 読み
company_name: str | null       — 会社名
company_name_en: str | null    — 会社名(英語)
department: str | null         — 部署名
title: str | null              — 役職
address: str | null            — 住所
postal_code: str | null        — 郵便番号
phone: str | null              — 電話番号
fax: str | null                — FAX番号
mobile: str | null             — 携帯電話番号
email: str | null              — メールアドレス
website: str | null            — WebサイトURL
```

## JSON Schema の保存先

```
structured_eval/dataset/
├── invoice/schema.json
├── receipt/schema.json
└── business_card/schema.json
```

`schema.json` が存在しない場合、評価コードは `structured_eval/src/schemas/` の Pydantic 定義にフォールバックする。
