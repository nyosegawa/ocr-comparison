"""名刺 (Business Card) schema."""

from __future__ import annotations

from pydantic import Field

from .base import DocumentSchema, register_schema


@register_schema
class BusinessCard(DocumentSchema):
    """名刺."""

    person_name: str = Field(..., description="氏名")
    person_name_reading: str | None = Field(
        None, description="氏名の読み（ふりがな/カタカナ）"
    )

    company_name: str | None = Field(None, description="会社名・組織名")
    company_name_en: str | None = Field(None, description="会社名（英語）")

    department: str | None = Field(None, description="部署名")
    title: str | None = Field(None, description="役職")

    address: str | None = Field(None, description="住所")
    postal_code: str | None = Field(None, description="郵便番号")

    phone: str | None = Field(None, description="電話番号")
    fax: str | None = Field(None, description="FAX番号")
    mobile: str | None = Field(None, description="携帯電話番号")
    email: str | None = Field(None, description="メールアドレス")
    website: str | None = Field(None, description="Webサイト URL")

    @classmethod
    def document_type(cls) -> str:
        return "business_card"

    @classmethod
    def document_type_ja(cls) -> str:
        return "名刺"
