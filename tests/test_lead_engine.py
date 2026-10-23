"""Tests for Lead Intelligence Engine."""

import pytest
from nexus_flow.engines.lead.service import LeadEngine
from nexus_flow.schemas.lead import LeadIngestRequest
from nexus_flow.core.constants import LeadPriority, LeadStatus

def test_qualify_hot_lead(test_db):
    engine = LeadEngine(db=test_db)
    req = LeadIngestRequest(
        email="elena@hyperion.com",
        full_name="Elena Rostova",
        company="Hyperion Dynamics",
        budget=85000.0,
        company_size="500+",
        needs_description="Autonomous operations and ERP document automation.",
        consent=True,
    )
    res = engine.process_lead(req)
    assert res["score"] >= 75
    assert res["priority"] == LeadPriority.HOT.value
    assert res["status"] == LeadStatus.QUALIFIED.value
    assert res["sla_met"] is True
    assert res["execution_seconds"] < 10.0
    assert len(res["talking_points"]) > 0
    assert res["airtable_record_id"] is not None

def test_missing_budget_lead(test_db):
    engine = LeadEngine(db=test_db)
    req = LeadIngestRequest(
        email="alex@startup.io",
        full_name="Alex River",
        company="River Logistics",
        budget=0.0,
        company_size="1-10",
        needs_description="General information inquiry.",
        consent=True,
    )
    res = engine.process_lead(req)
    assert "budget" in res["missing_fields"]
    assert res["score"] < 50
    assert res["priority"] in [LeadPriority.COLD.value, LeadPriority.UNQUALIFIED.value]

def test_duplicate_lead_prevention(test_db):
    engine = LeadEngine(db=test_db)
    req = LeadIngestRequest(
        email="marcus@synthetix.io",
        full_name="Marcus Vance",
        company="Synthetix AI",
        budget=35000.0,
        company_size="51-200",
        consent=True,
    )
    first_res = engine.process_lead(req)
    assert first_res["is_duplicate"] is False

    # Second identical submission
    second_res = engine.process_lead(req)
    assert second_res["is_duplicate"] is True
    assert second_res["lead_id"] == first_res["lead_id"]

def test_non_consenting_lead(test_db):
    engine = LeadEngine(db=test_db)
    req = LeadIngestRequest(
        email="no_consent@example.com",
        full_name="Jane Doe",
        company="Acme Corp",
        budget=100000.0,
        consent=False,
    )
    res = engine.process_lead(req)
    assert res["score"] == 0
    assert res["priority"] == LeadPriority.UNQUALIFIED.value
    assert res["status"] == LeadStatus.DISQUALIFIED.value
