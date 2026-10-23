"""Tests for FastAPI HTTP routes."""

import pytest

def test_health_check_endpoint(client):
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["database_connected"] is True

def test_metrics_endpoint(client):
    res = client.get("/api/v1/metrics")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "counts" in data["data"]

def test_lead_ingest_and_list_endpoints(client):
    payload = {
        "full_name": "Marcus Vance",
        "email": "marcus@test.com",
        "company": "Synthetix AI",
        "budget": 30000.0,
        "company_size": "51-200",
        "needs_description": "API triage automation",
        "consent": True,
    }
    post_res = client.post("/api/v1/leads", json=payload)
    assert post_res.status_code == 201
    assert post_res.json()["success"] is True

    get_res = client.get("/api/v1/leads")
    assert get_res.status_code == 200
    assert len(get_res.json()["data"]) >= 1

def test_support_ticket_endpoints(client):
    payload = {
        "sender": "support@apex.com",
        "subject": "Help with API key",
        "body": "How do I configure my bearer token?",
    }
    post_res = client.post("/api/v1/support/tickets", json=payload)
    assert post_res.status_code == 201
    assert post_res.json()["data"]["intent"] == "technical_support"

def test_orchestration_intake_and_approvals(client):
    payload = {
        "client_name": "Hyperion Labs",
        "client_email": "ops@hyperion.com",
        "service_tier": "Enterprise Tier",
    }
    post_res = client.post("/api/v1/orchestration/intake", json=payload)
    assert post_res.status_code == 201

    appr_res = client.get("/api/v1/orchestration/approvals")
    assert appr_res.status_code == 200
