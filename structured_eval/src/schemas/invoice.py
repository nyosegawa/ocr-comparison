"""請求書 (Invoice) schema."""

from __future__ import annotations

from pydantic import Field

from .base import DocumentSchema, register_schema


class InvoiceLineItem(DocumentSchema):
    """請求書の明細行."""

    description: str = Field(..., description="品目・サービス名")
    quantity: float | None = Field(None, description="数量")
    unit: str | None = Field(None, description="単位")
    unit_price: float | None = Field(None, description="単価（税抜）")
    amount: float = Field(..., description="金額")

    @classmethod
    def document_type(cls) -> str:
        return "invoice_line_item"

    @classmethod
    def document_type_ja(cls) -> str:
        return "請求書明細"


@register_schema
class Invoice(DocumentSchema):
    """請求書."""

    invoice_number: str | None = Field(None, description="請求書番号")
    issue_date: str | None = Field(None, description="発行日 (YYYY-MM-DD)")
    due_date: str | None = Field(None, description="支払期限 (YYYY-MM-DD)")

    vendor_name: str = Field(..., description="請求元（発行者）の会社名")
    vendor_address: str | None = Field(None, description="請求元の住所")
    vendor_phone: str | None = Field(None, description="請求元の電話番号")
    vendor_registration_number: str | None = Field(
        None, description="適格請求書発行事業者登録番号 (T+13桁)"
    )

    client_name: str | None = Field(None, description="請求先の会社名・氏名")
    client_address: str | None = Field(None, description="請求先の住所")

    line_items: list[InvoiceLineItem] = Field(
        default_factory=list, description="明細行"
    )

    subtotal: float | None = Field(None, description="小計（税抜）")
    tax_rate: float | None = Field(None, description="消費税率 (例: 0.10)")
    tax_amount: float | None = Field(None, description="消費税額")
    total_amount: float = Field(..., description="合計金額（税込）")

    bank_name: str | None = Field(None, description="振込先銀行名")
    bank_branch: str | None = Field(None, description="振込先支店名")
    bank_account_type: str | None = Field(None, description="口座種別（普通/当座）")
    bank_account_number: str | None = Field(None, description="口座番号")
    bank_account_holder: str | None = Field(None, description="口座名義")

    notes: str | None = Field(None, description="備考")

    @classmethod
    def document_type(cls) -> str:
        return "invoice"

    @classmethod
    def document_type_ja(cls) -> str:
        return "請求書"
