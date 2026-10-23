"""Tests for external integration adapters."""

import pytest
from nexus_flow.adapters.airtable import AirtableAdapter
from nexus_flow.adapters.slack import SlackAdapter
from nexus_flow.adapters.sheets import GoogleSheetsAdapter
from nexus_flow.adapters.stripe import StripeAdapter
from nexus_flow.adapters.email import EmailAdapter
from nexus_flow.core.security import sanitize_csv_cell

def test_airtable_adapter_mock():
    adapter = AirtableAdapter()
    res = adapter.create_or_update_lead({"Name": "Test Lead", "Email": "lead@test.com"})
    assert res["success"] is True
    assert res["record_id"].startswith("rec_mock_")
    assert res["mode"] == "mock"

def test_slack_adapter_mock():
    adapter = SlackAdapter()
    res = adapter.send_notification("#sales", "New Deal", "A new enterprise deal was qualified", priority="HOT")
    assert res["success"] is True
    assert len(adapter.sent_messages) == 1
    assert adapter.sent_messages[0]["priority"] == "HOT"

def test_sheets_formula_injection_defense():
    # Test formula injection payload
    malicious = "=cmd|' /C calc'!A0"
    sanitized = sanitize_csv_cell(malicious)
    assert sanitized.startswith("'=")

    adapter = GoogleSheetsAdapter()
    res = adapter.append_invoice_row({"vendor": malicious, "extracted_total": 500.0})
    assert res["success"] is True
    assert res["cells"][1] == "'=cmd|' /C calc'!A0"

def test_stripe_adapter_test_signature():
    adapter = StripeAdapter()
    payload = b'{"hello": "world"}'
    sig = adapter.generate_test_signature(payload)
    assert adapter.verify_webhook_signature(payload, sig) is True

def test_email_adapter_draft_only():
    adapter = EmailAdapter()
    draft = adapter.create_draft("test@example.com", "Test Subject", "Test Body")
    assert draft["success"] is True
    assert draft["details"]["status"] == "DRAFT"

    # Auto send blocked
    send_res = adapter.send_email(draft["draft_id"], "admin")
    assert send_res["success"] is False
