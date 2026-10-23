"""Tests for Invoice Intelligence Engine."""

import pytest
from nexus_flow.engines.invoice.service import InvoiceEngine
from nexus_flow.core.constants import InvoiceStatus

SAMPLE_INVOICE_TEXT = """ACME ENTERPRISE CLOUD SERVICES
Invoice #: INV-2026-8801
Date: 2026-10-23
Currency: USD

Line Items:
- Infrastructure Consulting: Qty 1 @ $1000.00 = $1000.00
- Database Maintenance: Qty 2 @ $125.00 = $250.00

Subtotal: $1250.00
Tax: $125.00
Total Amount Due: $1375.00
"""

def test_clean_invoice_arithmetic_valid(test_db):
    engine = InvoiceEngine(db=test_db)
    res = engine.process_invoice(filename="acme_invoice.txt", content=SAMPLE_INVOICE_TEXT.encode("utf-8"))
    assert res["is_arithmetic_valid"] is True
    assert res["extracted_total"] == 1375.00
    assert res["calculated_total"] == 1375.00
    assert res["status"] == InvoiceStatus.EXTRACTED.value

def test_arithmetic_discrepancy_detected(test_db):
    engine = InvoiceEngine(db=test_db)
    # Deliberate mismatch: declared total is $1800 but sum is $1375
    discrepant_text = SAMPLE_INVOICE_TEXT.replace("Total Amount Due: $1375.00", "Total Amount Due: $1800.00")
    res = engine.process_invoice(filename="discrepant.txt", content=discrepant_text.encode("utf-8"))
    assert res["is_arithmetic_valid"] is False
    assert res["status"] == InvoiceStatus.FLAGGED_DISCREPANCY.value

def test_duplicate_invoice_flagged(test_db):
    engine = InvoiceEngine(db=test_db)
    res1 = engine.process_invoice(filename="inv1.txt", content=SAMPLE_INVOICE_TEXT.encode("utf-8"))
    assert res1["duplicate_flag"] is False

    res2 = engine.process_invoice(filename="inv1_copy.txt", content=SAMPLE_INVOICE_TEXT.encode("utf-8"))
    assert res2["duplicate_flag"] is True

def test_invoice_approval_and_sheets_export(test_db):
    engine = InvoiceEngine(db=test_db)
    res = engine.process_invoice(filename="export_test.txt", content=SAMPLE_INVOICE_TEXT.encode("utf-8"))
    inv_id = res["invoice_id"]

    # Approve
    appr = engine.approve_invoice(inv_id, approved_by="Finance Lead")
    assert appr["status"] == InvoiceStatus.APPROVED.value

    # Export to sheets
    exp = engine.export_to_sheets(inv_id)
    assert exp["success"] is True
    assert exp["status"] == InvoiceStatus.EXPORTED.value
    assert exp["row_number"] is not None
