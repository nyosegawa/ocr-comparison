"""Tests for Pydantic schemas and provider-specific conversions."""

import json

import pytest

from src.schemas.base import (
    generate_json_schema,
    get_all_schema_types,
    get_all_schemas,
    get_schema,
    to_claude_schema,
    to_gemini_schema,
    to_openai_schema,
)
from src.schemas.invoice import Invoice, InvoiceLineItem
from src.schemas.receipt import Receipt, ReceiptLineItem
from src.schemas.business_card import BusinessCard


class TestSchemaRegistry:
    def test_all_types_registered(self):
        types = get_all_schema_types()
        assert "invoice" in types
        assert "receipt" in types
        assert "business_card" in types

    def test_get_schema(self):
        assert get_schema("invoice") is Invoice
        assert get_schema("receipt") is Receipt
        assert get_schema("business_card") is BusinessCard

    def test_get_all_schemas(self):
        schemas = get_all_schemas()
        assert len(schemas) == 3


class TestInvoiceSchema:
    def test_minimal_invoice(self):
        inv = Invoice(
            vendor_name="テスト株式会社",
            total_amount=10000,
        )
        assert inv.vendor_name == "テスト株式会社"
        assert inv.total_amount == 10000
        assert inv.invoice_number is None

    def test_full_invoice(self):
        inv = Invoice(
            invoice_number="INV-001",
            issue_date="2026-03-17",
            due_date="2026-04-30",
            vendor_name="テスト株式会社",
            vendor_address="東京都渋谷区1-2-3",
            vendor_phone="03-1234-5678",
            vendor_registration_number="T1234567890123",
            client_name="顧客株式会社",
            client_address="大阪市北区梅田1-2-3",
            line_items=[
                InvoiceLineItem(
                    description="システム開発",
                    quantity=1,
                    unit="式",
                    unit_price=500000,
                    amount=500000,
                )
            ],
            subtotal=500000,
            tax_rate=0.10,
            tax_amount=50000,
            total_amount=550000,
            bank_name="みずほ銀行",
            bank_branch="渋谷支店",
            bank_account_type="普通",
            bank_account_number="1234567",
            bank_account_holder="テスト（カ",
            notes="お支払いは期日までにお願いします",
        )
        data = inv.model_dump()
        assert data["line_items"][0]["description"] == "システム開発"
        assert data["total_amount"] == 550000

    def test_json_schema_generation(self):
        schema = generate_json_schema(Invoice)
        assert schema["type"] == "object"
        assert "vendor_name" in schema["properties"]
        assert "line_items" in schema["properties"]
        # Should not have $defs (fully dereferenced)
        assert "$defs" not in schema

    def test_document_type(self):
        assert Invoice.document_type() == "invoice"
        assert Invoice.document_type_ja() == "請求書"


class TestReceiptSchema:
    def test_minimal_receipt(self):
        r = Receipt(store_name="コンビニ", total_amount=500)
        assert r.store_name == "コンビニ"

    def test_json_schema_generation(self):
        schema = generate_json_schema(Receipt)
        assert "store_name" in schema["properties"]
        assert "$defs" not in schema


class TestBusinessCardSchema:
    def test_minimal_card(self):
        card = BusinessCard(person_name="田中太郎")
        assert card.person_name == "田中太郎"
        assert card.company_name is None

    def test_json_schema_generation(self):
        schema = generate_json_schema(BusinessCard)
        assert "person_name" in schema["properties"]


class TestProviderConversion:
    def test_claude_schema(self):
        schema = to_claude_schema(Invoice)
        # Claude accepts standard JSON Schema
        assert schema["type"] == "object"
        assert "properties" in schema

    def test_openai_schema(self):
        schema = to_openai_schema(Invoice)
        # Must have additionalProperties: false
        assert schema["additionalProperties"] is False
        # All properties must be in required
        assert set(schema["required"]) == set(schema["properties"].keys())
        # Optional fields should have anyOf with null
        notes_schema = schema["properties"]["notes"]
        assert "anyOf" in notes_schema
        null_types = [s for s in notes_schema["anyOf"] if s.get("type") == "null"]
        assert len(null_types) == 1

    def test_openai_nested_objects(self):
        schema = to_openai_schema(Invoice)
        # line_items is wrapped in anyOf due to default_factory; find the array variant
        li = schema["properties"]["line_items"]
        if "anyOf" in li:
            array_variant = [s for s in li["anyOf"] if s.get("type") == "array"][0]
            items_schema = array_variant["items"]
        else:
            items_schema = li["items"]
        assert items_schema["additionalProperties"] is False

    def test_gemini_schema(self):
        schema = to_gemini_schema(Invoice)
        assert "properties" in schema
        # Should not have title fields
        assert "title" not in schema

    def test_roundtrip_serialization(self):
        """All provider schemas should be JSON-serializable."""
        for schema_cls in get_all_schemas().values():
            for converter in [to_claude_schema, to_openai_schema, to_gemini_schema]:
                schema = converter(schema_cls)
                serialized = json.dumps(schema, ensure_ascii=False)
                assert isinstance(serialized, str)
                parsed = json.loads(serialized)
                assert isinstance(parsed, dict)
