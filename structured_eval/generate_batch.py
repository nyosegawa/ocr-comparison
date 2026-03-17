"""Generate 9 synthetic Japanese business documents (3 invoices, 3 receipts, 3 business cards)
and render each to PNG using Jinja2 + Playwright."""

import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).parent
TEMPLATE_DIR = BASE_DIR / "templates"
DATASET_DIR = BASE_DIR / "dataset"

env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
env.globals["max"] = max


# ---------------------------------------------------------------------------
# Invoice data
# ---------------------------------------------------------------------------
INVOICES = [
    {
        "id": "invoice_001",
        "invoice_number": "INV-2026-0142",
        "issue_date": "2026-01-15",
        "due_date": "2026-02-28",
        "vendor_name": "株式会社テクノブリッジ",
        "vendor_address": "東京都渋谷区神宮前3-14-5 テクノビル8F",
        "vendor_phone": "03-5468-2310",
        "vendor_registration_number": "T4010401098765",
        "client_name": "合同会社グリーンフィールド",
        "client_address": "東京都千代田区丸の内1-9-2 グランフロント12F",
        "line_items": [
            {"description": "Webアプリケーション開発費（1月分）", "quantity": 1, "unit": "式", "unit_price": 180000, "amount": 180000},
            {"description": "クラウドサーバ保守・運用費", "quantity": 1, "unit": "月", "unit_price": 55000, "amount": 55000},
            {"description": "UI/UXデザイン修正対応", "quantity": 3, "unit": "件", "unit_price": 25000, "amount": 75000},
            {"description": "セキュリティ診断レポート作成", "quantity": 1, "unit": "式", "unit_price": 40000, "amount": 40000},
        ],
        "subtotal": 350000,
        "tax_rate": 0.10,
        "tax_amount": 35000,
        "total_amount": 385000,
        "bank_name": "三菱UFJ銀行",
        "bank_branch": "渋谷支店",
        "bank_account_type": "普通",
        "bank_account_number": "1234567",
        "bank_account_holder": "カ）テクノブリッジ",
        "notes": "お振込手数料はお客様ご負担にてお願いいたします。",
    },
    {
        "id": "invoice_002",
        "invoice_number": "INV-2026-0387",
        "issue_date": "2026-02-03",
        "due_date": "2026-03-31",
        "vendor_name": "大和建設工業株式会社",
        "vendor_address": "大阪府大阪市中央区本町4-2-12 大和ビルディング3F",
        "vendor_phone": "06-6245-8800",
        "vendor_registration_number": "T1200001054321",
        "client_name": "学校法人清風学園",
        "client_address": "大阪府大阪市天王寺区清水谷町6-1",
        "line_items": [
            {"description": "校舎改修工事（A棟外壁塗装）", "quantity": 1, "unit": "式", "unit_price": 2800000, "amount": 2800000},
            {"description": "屋上防水工事", "quantity": 1, "unit": "式", "unit_price": 1500000, "amount": 1500000},
            {"description": "空調設備更新工事（教室10室）", "quantity": 10, "unit": "室", "unit_price": 320000, "amount": 3200000},
            {"description": "電気配線改修工事", "quantity": 1, "unit": "式", "unit_price": 850000, "amount": 850000},
            {"description": "仮設足場設置・撤去", "quantity": 1, "unit": "式", "unit_price": 620000, "amount": 620000},
            {"description": "廃材処分・清掃費", "quantity": 1, "unit": "式", "unit_price": 180000, "amount": 180000},
            {"description": "現場管理費", "quantity": 1, "unit": "式", "unit_price": 450000, "amount": 450000},
        ],
        "subtotal": 9600000,
        "tax_rate": 0.10,
        "tax_amount": 960000,
        "total_amount": 10560000,
        "bank_name": "みずほ銀行",
        "bank_branch": "本町支店",
        "bank_account_type": "普通",
        "bank_account_number": "7654321",
        "bank_account_holder": "ダイワケンセツコウギョウ（カ",
        "notes": "工事完了後30日以内にお支払いください。別途工事完了報告書を送付いたします。",
    },
    {
        "id": "invoice_003",
        "invoice_number": "INV-2026-0058",
        "issue_date": "2026-01-28",
        "due_date": "2026-02-15",
        "vendor_name": "博多もつ鍋 まるよし",
        "vendor_address": "福岡県福岡市博多区中洲3-7-18",
        "vendor_phone": "092-281-4455",
        "vendor_registration_number": "T9400001032198",
        "client_name": "福岡商事株式会社",
        "client_address": "福岡県福岡市中央区天神2-5-1",
        "line_items": [
            {"description": "新年会ケータリング（15名様分）", "quantity": 1, "unit": "式", "unit_price": 7500, "amount": 7500},
        ],
        "subtotal": 7500,
        "tax_rate": 0.10,
        "tax_amount": 750,
        "total_amount": 8250,
        "bank_name": "福岡銀行",
        "bank_branch": "博多駅前支店",
        "bank_account_type": "普通",
        "bank_account_number": "3216549",
        "bank_account_holder": "ハカタモツナベ マルヨシ",
        "notes": None,
    },
]

# ---------------------------------------------------------------------------
# Receipt data
# ---------------------------------------------------------------------------
RECEIPTS = [
    {
        "id": "receipt_001",
        "receipt_number": "R-20260210-0034",
        "issue_date": "2026-02-10",
        "store_name": "ドラッグストア コスモス",
        "store_address": "愛知県名古屋市中区栄3-15-27",
        "store_phone": "052-242-7788",
        "store_registration_number": "T3180001055678",
        "client_name": None,
        "line_items": [
            {"description": "ハンドソープ 泡タイプ", "quantity": 2, "unit_price": 398, "amount": 796},
            {"description": "※ ミネラルウォーター 2L", "quantity": 3, "unit_price": 88, "amount": 264},
            {"description": "マスク 30枚入", "quantity": 1, "unit_price": 498, "amount": 498},
        ],
        "subtotal": 1558,
        "tax_rate_8": 264,
        "tax_amount_8": 19,
        "tax_rate_10": 1294,
        "tax_amount_10": 117,
        "total_amount": 1558,
        "payment_method": "現金",
        "notes": "※は軽減税率(8%)対象商品です",
    },
    {
        "id": "receipt_002",
        "receipt_number": "R-20260305-0112",
        "issue_date": "2026-03-05",
        "store_name": "仙台メディカルクリニック",
        "store_address": "宮城県仙台市青葉区一番町2-4-1",
        "store_phone": "022-265-3300",
        "store_registration_number": "T7370001089012",
        "client_name": "佐藤健太",
        "line_items": [
            {"description": "初診料", "quantity": 1, "unit_price": 2880, "amount": 2880},
            {"description": "血液検査（一般）", "quantity": 1, "unit_price": 4200, "amount": 4200},
            {"description": "心電図検査", "quantity": 1, "unit_price": 1500, "amount": 1500},
            {"description": "処方箋料", "quantity": 1, "unit_price": 680, "amount": 680},
        ],
        "subtotal": 9260,
        "tax_rate_8": None,
        "tax_amount_8": None,
        "tax_rate_10": 9260,
        "tax_amount_10": 840,
        "total_amount": 9260,
        "payment_method": "クレジットカード",
        "notes": "医療費控除対象",
    },
    {
        "id": "receipt_003",
        "receipt_number": "R-20260118-0201",
        "issue_date": "2026-01-18",
        "store_name": "北海道不動産株式会社",
        "store_address": "北海道札幌市中央区北1条西4-2-2 札幌ノースプラザ6F",
        "store_phone": "011-222-5500",
        "store_registration_number": "T2430001076543",
        "client_name": "山田太郎",
        "line_items": [
            {"description": "賃貸仲介手数料（中央区マンション）", "quantity": 1, "unit_price": 75000, "amount": 75000},
            {"description": "火災保険料（2年分）", "quantity": 1, "unit_price": 22000, "amount": 22000},
            {"description": "鍵交換費用", "quantity": 1, "unit_price": 16500, "amount": 16500},
            {"description": "保証会社初回保証料", "quantity": 1, "unit_price": 37500, "amount": 37500},
            {"description": "入居時クリーニング費", "quantity": 1, "unit_price": 33000, "amount": 33000},
        ],
        "subtotal": 184000,
        "tax_rate_8": None,
        "tax_amount_8": None,
        "tax_rate_10": 184000,
        "tax_amount_10": 16727,
        "total_amount": 184000,
        "payment_method": "銀行振込",
        "notes": "賃貸契約に伴う初期費用として",
    },
]

# ---------------------------------------------------------------------------
# Business card data
# ---------------------------------------------------------------------------
BUSINESS_CARDS = [
    {
        "id": "bcard_001",
        "person_name": "鈴木 亮介",
        "person_name_reading": "スズキ リョウスケ",
        "company_name": "株式会社ネクストイノベーション",
        "company_name_en": "Next Innovation Inc.",
        "department": "プロダクト開発本部 第2開発部",
        "title": "シニアエンジニア / Tech Lead",
        "address": "東京都港区六本木6-10-1 六本木ヒルズ森タワー35F",
        "postal_code": "106-6135",
        "phone": "03-6384-5500",
        "fax": "03-6384-5501",
        "mobile": "090-1234-5678",
        "email": "r.suzuki@nextinnovation.co.jp",
        "website": "https://www.nextinnovation.co.jp",
    },
    {
        "id": "bcard_002",
        "person_name": "藤原 龍太郎",
        "person_name_reading": "フジワラ リュウタロウ",
        "company_name": "東洋精密機械工業株式会社",
        "company_name_en": None,
        "department": "品質管理統括部 検査技術課",
        "title": "課長",
        "address": "広島県広島市南区出汐2-3-18 東洋精密広島工場内",
        "postal_code": "734-0001",
        "phone": "082-253-6100",
        "fax": "082-253-6101",
        "mobile": None,
        "email": "fujiwara.ryutaro@toyo-seimitsu.co.jp",
        "website": None,
    },
    {
        "id": "bcard_003",
        "person_name": "マイケル 高橋",
        "person_name_reading": "マイケル タカハシ",
        "company_name": "グローバルアカデミー四国",
        "company_name_en": "Global Academy Shikoku",
        "department": "カリキュラムデベロップメント部",
        "title": "プログラムディレクター",
        "address": "香川県高松市サンポート2-1 高松シンボルタワー10F",
        "postal_code": "760-0019",
        "phone": "087-811-2200",
        "fax": None,
        "mobile": "080-9876-5432",
        "email": "michael.takahashi@global-academy.jp",
        "website": "https://www.global-academy.jp",
    },
]


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------
VIEWPORT_SETTINGS = {
    "invoice": {"width": 794, "height": 1123},
    "receipt": {"width": 300, "height": 600},
    "business_card": {"width": 346, "height": 210},
}


def render_documents():
    """Render all documents to PNG and save ground truth JSON."""
    with sync_playwright() as p:
        browser = p.chromium.launch()

        for doc_type, docs, template_name in [
            ("invoice", INVOICES, "invoice.html.j2"),
            ("receipt", RECEIPTS, "receipt.html.j2"),
            ("business_card", BUSINESS_CARDS, "business_card.html.j2"),
        ]:
            template = env.get_template(template_name)
            vp = VIEWPORT_SETTINGS[doc_type]
            output_dir = DATASET_DIR / doc_type

            for doc in docs:
                doc_id = doc["id"]
                # Prepare template data (exclude 'id' from template context)
                template_data = {k: v for k, v in doc.items() if k != "id"}

                # Render HTML
                html = template.render(**template_data)

                # Create a new page with the right viewport
                page = browser.new_page(
                    viewport={"width": vp["width"], "height": vp["height"]},
                    device_scale_factor=2,
                )
                page.set_content(html, wait_until="networkidle")

                # Screenshot
                png_path = output_dir / f"{doc_id}.png"
                if doc_type == "receipt":
                    # For receipt, capture full page (variable height)
                    page.screenshot(path=str(png_path), full_page=True)
                else:
                    # For invoice and business card, clip to exact body size
                    page.screenshot(
                        path=str(png_path),
                        clip={"x": 0, "y": 0, "width": vp["width"], "height": vp["height"]},
                    )

                page.close()

                # Save ground truth JSON (all fields including null)
                json_path = output_dir / f"{doc_id}.json"
                ground_truth = {k: v for k, v in doc.items() if k != "id"}
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(ground_truth, f, ensure_ascii=False, indent=2)

                print(f"  {doc_type}/{doc_id}.png + .json")

        browser.close()


if __name__ == "__main__":
    print("Generating 9 business documents...")
    render_documents()
    print("Done.")
