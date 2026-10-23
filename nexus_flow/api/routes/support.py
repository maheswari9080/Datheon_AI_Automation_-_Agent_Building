"""API routes for Support Intelligence Engine."""

import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from nexus_flow.db.session import get_db
from nexus_flow.engines.support.service import SupportEngine
from nexus_flow.schemas.support import SupportIngestRequest
from nexus_flow.schemas.common import ApiResponse

router = APIRouter(prefix="/support", tags=["Support Intelligence"])

def get_support_engine(db: Session = Depends(get_db)) -> SupportEngine:
    return SupportEngine(db=db)

@router.post("/tickets", response_model=ApiResponse[dict], status_code=status.HTTP_201_CREATED)
def create_support_ticket(req: SupportIngestRequest, engine: SupportEngine = Depends(get_support_engine)):
    try:
        res = engine.process_ticket(req)
        return ApiResponse(
            success=True,
            message="Support email ingested, classified, and grounded draft prepared",
            data={
                "ticket_id": res["ticket_id"],
                "message_id": res["message_id"],
                "intent": res["intent"],
                "urgency": res["urgency"],
                "sentiment": res["sentiment"],
                "draft_body": res["draft_body"],
                "kb_references": res["kb_references"],
                "prompt_injection_flag": res["prompt_injection_flag"],
                "requires_escalation": res["requires_escalation"],
                "escalation_reason": res["escalation_reason"],
                "is_draft": res["is_draft"],
            },
            execution_time_ms=res["duration_ms"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tickets", response_model=ApiResponse[List[dict]])
def list_support_tickets(
    intent: Optional[str] = Query(None),
    urgency: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    engine: SupportEngine = Depends(get_support_engine),
):
    tickets = engine.list_tickets(intent=intent, urgency=urgency, limit=limit)
    out = []
    for t in tickets:
        kb_refs = json.loads(t.kb_references) if t.kb_references else []
        out.append({
            "id": t.id,
            "message_id": t.message_id,
            "sender": t.sender,
            "subject": t.subject,
            "sanitized_body": t.sanitized_body,
            "intent": t.intent,
            "urgency": t.urgency,
            "sentiment": t.sentiment,
            "confidence": t.confidence,
            "draft_response": t.draft_response,
            "kb_references": kb_refs,
            "is_draft": t.is_draft,
            "prompt_injection_flag": t.prompt_injection_flag,
            "requires_escalation": t.requires_escalation,
            "escalation_reason": t.escalation_reason,
            "created_at": t.created_at.isoformat() if t.created_at else None,
        })
    return ApiResponse(success=True, data=out)

@router.get("/tickets/{ticket_id}", response_model=ApiResponse[dict])
def get_support_ticket(ticket_id: str, engine: SupportEngine = Depends(get_support_engine)):
    t = engine.get_ticket(ticket_id)
    if not t:
        raise HTTPException(status_code=404, detail="Support ticket not found")
    kb_refs = json.loads(t.kb_references) if t.kb_references else []
    return ApiResponse(
        success=True,
        data={
            "id": t.id,
            "message_id": t.message_id,
            "sender": t.sender,
            "subject": t.subject,
            "sanitized_body": t.sanitized_body,
            "intent": t.intent,
            "urgency": t.urgency,
            "sentiment": t.sentiment,
            "draft_response": t.draft_response,
            "kb_references": kb_refs,
            "requires_escalation": t.requires_escalation,
            "escalation_reason": t.escalation_reason,
            "created_at": t.created_at.isoformat() if t.created_at else None,
        },
    )

@router.get("/kb", response_model=ApiResponse[List[dict]])
def list_knowledge_articles(engine: SupportEngine = Depends(get_support_engine)):
    return ApiResponse(success=True, data=engine.kb.articles)
