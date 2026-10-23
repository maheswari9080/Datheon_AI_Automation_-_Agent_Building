"""API routes for Enterprise Orchestration Engine."""

import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from nexus_flow.db.session import get_db
from nexus_flow.engines.orchestration.service import OrchestrationEngine
from nexus_flow.schemas.orchestration import CustomerIntakeRequest, ContractDraftRequest
from nexus_flow.schemas.common import ApiResponse

router = APIRouter(prefix="/orchestration", tags=["Enterprise Orchestration"])

def get_orchestration_engine(db: Session = Depends(get_db)) -> OrchestrationEngine:
    return OrchestrationEngine(db=db)

class ApprovalResolveRequest(BaseModel):
    action: str  # APPROVED or REJECTED
    resolved_by: str = "Authorized Executive"
    notes: Optional[str] = None

@router.post("/intake", response_model=ApiResponse[dict], status_code=status.HTTP_201_CREATED)
def intake_customer(req: CustomerIntakeRequest, engine: OrchestrationEngine = Depends(get_orchestration_engine)):
    try:
        res = engine.customer_intake(req)
        return ApiResponse(
            success=True,
            message="Customer intake completed successfully",
            data={
                "project_id": res["project_id"],
                "project_code": res["project_code"],
                "is_existing": res["is_existing"],
                "status": res["status"],
                "airtable_record_id": res.get("airtable_record_id"),
            },
            execution_time_ms=res.get("duration_ms"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects", response_model=ApiResponse[List[dict]])
def list_projects(
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=100),
    engine: OrchestrationEngine = Depends(get_orchestration_engine),
):
    projects = engine.list_projects(status=status_filter, limit=limit)
    out = [
        {
            "id": p.id,
            "project_code": p.project_code,
            "client_name": p.client_name,
            "client_email": p.client_email,
            "service_tier": p.service_tier,
            "status": p.status,
            "contract_status": p.contract_status,
            "payment_status": p.payment_status,
            "slack_channel": p.slack_channel,
            "airtable_record_id": p.airtable_record_id,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in projects
    ]
    return ApiResponse(success=True, data=out)

@router.post("/contracts", response_model=ApiResponse[dict], status_code=status.HTTP_201_CREATED)
def draft_contract(req: ContractDraftRequest, engine: OrchestrationEngine = Depends(get_orchestration_engine)):
    try:
        res = engine.prepare_contract_draft(req)
        return ApiResponse(
            success=True,
            message="Contract draft prepared and placed in human approval queue",
            data={
                "contract_id": res["contract_id"],
                "project_code": res["project_code"],
                "template_version": res["template_version"],
                "approval_status": res["approval_status"],
                "contract_text": res["contract_text"],
            },
        )
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/contracts/{contract_id}/approve", response_model=ApiResponse[dict])
def approve_contract(contract_id: str, engine: OrchestrationEngine = Depends(get_orchestration_engine)):
    try:
        res = engine.approve_contract(contract_id=contract_id)
        return ApiResponse(success=True, message="Contract approved successfully", data=res)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))

@router.post("/channels/{project_id}", response_model=ApiResponse[dict])
def provision_channel(project_id: str, engine: OrchestrationEngine = Depends(get_orchestration_engine)):
    try:
        res = engine.provision_collaboration_channel(project_id=project_id)
        return ApiResponse(success=True, message="Slack channel provisioned", data=res)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))

@router.get("/digest", response_model=ApiResponse[dict])
def get_executive_digest(engine: OrchestrationEngine = Depends(get_orchestration_engine)):
    digest = engine.generate_weekly_digest()
    return ApiResponse(success=True, message="Executive digest compiled from live records", data=digest)

@router.get("/approvals", response_model=ApiResponse[List[dict]])
def list_approvals(
    status_filter: Optional[str] = Query("PENDING", alias="status"),
    engine: OrchestrationEngine = Depends(get_orchestration_engine),
):
    items = engine.list_approvals(status=status_filter)
    out = [
        {
            "id": a.id,
            "entity_type": a.entity_type,
            "entity_id": a.entity_id,
            "title": a.title,
            "description": a.description,
            "status": a.status,
            "requested_by": a.requested_by,
            "resolved_by": a.resolved_by,
            "resolution_notes": a.resolution_notes,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in items
    ]
    return ApiResponse(success=True, data=out)

@router.post("/approvals/{approval_id}/resolve", response_model=ApiResponse[dict])
def resolve_approval(
    approval_id: str,
    req: ApprovalResolveRequest,
    engine: OrchestrationEngine = Depends(get_orchestration_engine),
):
    try:
        res = engine.resolve_approval(
            approval_id=approval_id,
            action=req.action,
            resolved_by=req.resolved_by,
            notes=req.notes,
        )
        return ApiResponse(success=True, message=f"Approval resolved as {req.action}", data=res)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
