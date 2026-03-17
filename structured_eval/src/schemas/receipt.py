"""領収書 (Receipt) schema."""

from __future__ import annotations

from pydantic import Field

from .base import DocumentSchema, register_schema


class ReceiptLineItem(DocumentSchema):
    """領収書の明細行."""

    description: str = Field(..., description="品目名")
    quantity: float | None = Field(None, description="数量")
    unit_price: float | None = Field(None, description="単価")
    amount: float = Field(..., description="金額")

    @classmethod
    def document_type(cls) -> str:
        return "receipt_line_item"

    @classmethod
    def document_type_ja(cls) -> str:
        return "領収書明細"


@register_schema
class Receipt(DocumentSchema):
    """領収書."""

    receipt_number: str | None = Field(None, description="領収書番号")
    issue_date: str | None = Field(None, description="発行日 (YYYY-MM-DD)")

    store_name: str = Field(..., description="店舗名・発行者名")
    store_address: str | None = Field(None, description="店舗住所")
    store_phone: str | None = Field(None, description="店舗電話番号")
    store_registration_number: str | None = Field(
        None, description="適格請求書発行事業者登録番号 (T+13桁)"
    )

    client_name: str | None = Field(None, description="宛名（上様等）")

    line_items: list[ReceiptLineItem] = Field(
        default_factory=list, description="明細行"
    )

    subtotal: float | None = Field(None, description="小計（税抜）")
    tax_rate_8: float | None = Field(None, description="8%対象額")
    tax_amount_8: float | None = Field(None, description="8%消費税額")
    tax_rate_10: float | None = Field(None, description="10%対象額")
    tax_amount_10: float | None = Field(None, description="10%消費税額")
    total_amount: float = Field(..., description="合計金額")

    payment_method: str | None = Field(
        None, description="支払方法（現金/クレジットカード/電子マネー等）"
    )

    notes: str | None = Field(None, description="備考・但し書き")

    @classmethod
    def document_type(cls) -> str:
        return "receipt"

    @classmethod
    def document_type_ja(cls) -> str:
        return "領収書"
