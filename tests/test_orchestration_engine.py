"""Tests for Enterprise Orchestration Engine."""

import json
import pytest
from nexus_flow.engines.orchestration.service import OrchestrationEngine
from nexus_flow.schemas.orchestration import CustomerIntakeRequest, ContractDraftRequest
from nexus_flow.core.constants import ProjectStatus

def test_customer_intake_and_project_code(test_db):
    engine = OrchestrationEngine(db=test_db)
    req = CustomerIntakeRequest(
        client_name="Hyperion Dynamics",
        client_email="elena@hyperion.com",
        service_tier="Enterprise Tier",
    )
    res = engine.customer_intake(req)
    assert res["project_code"].startswith("PRJ-")
    assert res["is_existing"] is False
    assert res["status"] == ProjectStatus.INTAKE.value

def test_contract_drafting_and_approval(test_db):
    engine = OrchestrationEngine(db=test_db)
    intake_res = engine.customer_intake(
        CustomerIntakeRequest(
            client_name="Acme Corp",
            client_email="contact@acme.com",
            service_tier="Growth Automation",
        )
    )
    proj_id = intake_res["project_id"]

    draft_res = engine.prepare_contract_draft(
        ContractDraftRequest(project_id=proj_id, template_version="MSA-v2.1")
    )
    contract_id = draft_res["contract_id"]
    assert draft_res["approval_status"] == "PENDING"
    assert "MASTER SERVICES AGREEMENT" in draft_res["contract_text"]

    appr_res = engine.approve_contract(contract_id=contract_id, approved_by="Legal Partner")
    assert appr_res["approval_status"] == "APPROVED"

def test_stripe_hmac_signature_verification(test_db):
    engine = OrchestrationEngine(db=test_db)
    intake_res = engine.customer_intake(
        CustomerIntakeRequest(
            client_name="Stripe Client",
            client_email="stripe@client.com",
            service_tier="Scale Tier",
        )
    )
    code = intake_res["project_code"]

    event_payload = {
        "id": "evt_test_payment_success_991",
        "type": "payment_intent.succeeded",
        "data": {
            "object": {
                "amount": 500000,
                "currency": "usd",
                "metadata": {"project_code": code},
            }
        },
    }
    payload_bytes = json.dumps(event_payload).encode("utf-8")
    valid_sig = engine.stripe.generate_test_signature(payload_bytes)

    # 1. Valid Signature -> Payment Verified
    pay_res = engine.process_stripe_payment(payload_bytes, valid_sig)
    assert pay_res["success"] is True
    assert pay_res["payment_status"] == "PAID"
    assert pay_res["amount_dollars"] == 5000.0

    # 2. Duplicate Event -> Idempotently Ignored
    dup_res = engine.process_stripe_payment(payload_bytes, valid_sig)
    assert dup_res["status"] == "duplicate_ignored"

    # 3. Invalid Signature -> Raised ValueError
    with pytest.raises(ValueError, match="Unauthorized Stripe signature"):
        engine.process_stripe_payment(payload_bytes, "t=123,v1=tampered_invalid_hex")

def test_weekly_executive_digest(test_db):
    engine = OrchestrationEngine(db=test_db)
    digest = engine.generate_weekly_digest()
    assert "metrics" in digest
    assert "ai_executive_summary" in digest
    assert digest["source_coverage"].startswith("100% Verified")
