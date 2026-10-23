"""API routes for Lead Intelligence Engine."""

import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from nexus_flow.db.session import get_db
from nexus_flow.engines.lead.service import LeadEngine
from nexus_flow.schemas.lead import LeadIngestRequest, LeadResponse
from nexus_flow.schemas.common import ApiResponse

router = APIRouter(prefix="/leads", tags=["Lead Intelligence"])

def get_lead_engine(db: Session = Depends(get_db)) -> LeadEngine:
    return LeadEngine(db=db)

@router.post("", response_model=ApiResponse[dict], status_code=status.HTTP_201_CREATED)
def ingest_lead(req: LeadIngestRequest, engine: LeadEngine = Depends(get_lead_engine)):
    try:
        res = engine.process_lead(req)
        return ApiResponse(
            success=True,
            message="Lead ingested and processed successfully",
            data={
                "lead_id": res["lead_id"],
                "score": res["score"],
                "priority": res["priority"],
                "status": res["status"],
                "assigned_rep": res.get("assigned_rep"),
                "ai_summary": res.get("ai_summary"),
                "talking_points": res.get("talking_points", []),
                "missing_fields": res.get("missing_fields", []),
                "execution_seconds": res.get("execution_seconds"),
                "sla_met": res.get("sla_met"),
            },
            execution_time_ms=res.get("execution_seconds", 0.0) * 1000,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=ApiResponse[List[dict]])
def list_leads(
    priority: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=100),
    engine: LeadEngine = Depends(get_lead_engine),
):
    records = engine.list_leads(priority=priority, status=status_filter, limit=limit)
    out = []
    for r in records:
        talking_points = json.loads(r.talking_points) if r.talking_points else []
        missing_fields = json.loads(r.missing_fields) if r.missing_fields else []
        out.append({
            "id": r.id,
            "email": r.email,
            "full_name": r.full_name,
            "company": r.company,
            "phone": r.phone,
            "budget": r.budget,
            "company_size": r.company_size,
            "needs_description": r.needs_description,
            "source": r.source,
            "consent": r.consent,
            "score": r.score,
            "priority": r.priority,
            "status": r.status,
            "confidence": r.confidence,
            "ai_summary": r.ai_summary,
            "talking_points": talking_points,
            "missing_fields": missing_fields,
            "airtable_record_id": r.airtable_record_id,
            "slack_notified": r.slack_notified,
            "latency_seconds": r.latency_seconds,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })
    return ApiResponse(success=True, data=out)

@router.get("/{lead_id}", response_model=ApiResponse[dict])
def get_lead(lead_id: str, engine: LeadEngine = Depends(get_lead_engine)):
    r = engine.get_lead(lead_id)
    if not r:
        raise HTTPException(status_code=404, detail="Lead not found")
    talking_points = json.loads(r.talking_points) if r.talking_points else []
    missing_fields = json.loads(r.missing_fields) if r.missing_fields else []
    return ApiResponse(
        success=True,
        data={
            "id": r.id,
            "email": r.email,
            "full_name": r.full_name,
            "company": r.company,
            "budget": r.budget,
            "score": r.score,
            "priority": r.priority,
            "status": r.status,
            "ai_summary": r.ai_summary,
            "talking_points": talking_points,
            "missing_fields": missing_fields,
            "airtable_record_id": r.airtable_record_id,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        },
    )
