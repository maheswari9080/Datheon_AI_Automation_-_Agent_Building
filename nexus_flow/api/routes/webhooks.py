"""Webhook ingestion routes for Stripe, external forms, and partner hooks."""

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session
from nexus_flow.db.session import get_db
from nexus_flow.engines.orchestration.service import OrchestrationEngine
from nexus_flow.engines.lead.service import LeadEngine
from nexus_flow.schemas.lead import LeadIngestRequest
from nexus_flow.schemas.common import ApiResponse

router = APIRouter(prefix="/webhooks", tags=["Webhooks Ingestion"])

@router.post("/stripe", response_model=ApiResponse[dict])
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(..., alias="Stripe-Signature"),
    db: Session = Depends(get_db),
):
    """
    Ingests and cryptographically verifies official Stripe webhook payloads.
    Requires valid Stripe-Signature HMAC-SHA256 header.
    """
    payload_bytes = await request.body()
    engine = OrchestrationEngine(db=db)
    try:
        res = engine.process_stripe_payment(payload_bytes, stripe_signature)
        return ApiResponse(success=True, message="Stripe webhook processed", data=res)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/leads", response_model=ApiResponse[dict], status_code=status.HTTP_201_CREATED)
def external_lead_webhook(
    req: LeadIngestRequest,
    db: Session = Depends(get_db),
):
    """Authenticated inbound lead webhook endpoint for external web forms (Typeform, HubSpot, Zapier)."""
    engine = LeadEngine(db=db)
    res = engine.process_lead(req)
    return ApiResponse(
        success=True,
        message="External lead webhook accepted",
        data={
            "lead_id": res["lead_id"],
            "score": res["score"],
            "priority": res["priority"],
            "status": res["status"],
            "airtable_record_id": res.get("airtable_record_id"),
        },
        execution_time_ms=res.get("execution_seconds", 0.0) * 1000,
    )
