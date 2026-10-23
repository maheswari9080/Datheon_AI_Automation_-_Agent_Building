"""System health, metrics, and audit trail query routes."""

import time
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from nexus_flow.core.config import get_settings
from nexus_flow.db.session import get_db
from nexus_flow.db.models import (
    LeadRecord,
    SupportTicketRecord,
    InvoiceRecord,
    ProjectRecord,
    PaymentRecord,
    AuditEventRecord,
    ApprovalRequestRecord,
)
from nexus_flow.adapters import AirtableAdapter, SlackAdapter, StripeAdapter, GoogleSheetsAdapter, EmailAdapter
from nexus_flow.schemas.common import ApiResponse, HealthCheckResponse

router = APIRouter(tags=["System Telemetry"])
settings = get_settings()
START_TIME = time.time()

@router.get("/health", response_model=HealthCheckResponse)
def health_check(db: Session = Depends(get_db)):
    uptime = time.time() - START_TIME
    db_ok = True
    try:
        db.query(AuditEventRecord).first()
    except Exception:
        db_ok = False

    services = {
        "airtable": AirtableAdapter().health_check(),
        "slack": SlackAdapter().health_check(),
        "stripe": StripeAdapter().health_check(),
        "google_sheets": GoogleSheetsAdapter().health_check(),
        "email_provider": EmailAdapter().health_check(),
    }

    return HealthCheckResponse(
        status="healthy" if db_ok else "unhealthy",
        version=settings.app_version,
        mode="live" if settings.live_mode else "demo",
        uptime_seconds=round(uptime, 1),
        database_connected=db_ok,
        services=services,
    )

@router.get("/metrics", response_model=ApiResponse[dict])
def get_metrics(db: Session = Depends(get_db)):
    leads = db.query(LeadRecord).all()
    tickets = db.query(SupportTicketRecord).all()
    invoices = db.query(InvoiceRecord).all()
    payments = db.query(PaymentRecord).all()
    projects = db.query(ProjectRecord).all()
    approvals = db.query(ApprovalRequestRecord).filter(ApprovalRequestRecord.status == "PENDING").all()
    audits = db.query(AuditEventRecord).order_by(AuditEventRecord.created_at.desc()).limit(100).all()

    avg_lead_latency = (
        sum(l.latency_seconds for l in leads) / len(leads) if leads else 0.0
    )

    return ApiResponse(
        success=True,
        data={
            "mode": "live" if settings.live_mode else "demo",
            "counts": {
                "leads": len(leads),
                "support_tickets": len(tickets),
                "invoices": len(invoices),
                "projects": len(projects),
                "verified_payments": len(payments),
                "pending_approvals": len(approvals),
            },
            "financials": {
                "verified_revenue_usd": sum(p.amount_cents for p in payments) / 100.0,
                "total_invoiced_usd": sum(i.extracted_total for i in invoices),
            },
            "sla": {
                "avg_lead_latency_seconds": round(avg_lead_latency, 2),
                "lead_sla_target_seconds": settings.lead_sla_max_seconds,
            },
            "recent_audit_count": len(audits),
        },
    )

@router.get("/audit", response_model=ApiResponse[List[dict]])
def get_audit_trail(
    limit: int = Query(50, ge=1, le=200),
    event_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(AuditEventRecord)
    if event_type:
        query = query.filter(AuditEventRecord.event_type == event_type)
    records = query.order_by(AuditEventRecord.created_at.desc()).limit(limit).all()

    out = [
        {
            "id": a.id,
            "event_type": a.event_type,
            "action": a.action,
            "status": a.status,
            "entity_id": a.entity_id,
            "duration_ms": a.duration_ms,
            "details_json": a.details_json,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in records
    ]
    return ApiResponse(success=True, data=out)
