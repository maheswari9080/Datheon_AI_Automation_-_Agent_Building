"""Pydantic schemas for Support Intelligence Engine."""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class SupportIngestRequest(BaseModel):
    message_id: Optional[str] = None
    sender: EmailStr
    subject: str = Field(..., min_length=1, max_length=500)
    body: str = Field(..., min_length=1, max_length=50000)

class GroundedDraftResponse(BaseModel):
    draft_body: str
    kb_references: List[str]
    citations_valid: bool
    policy_notes: Optional[str] = None

class SupportTicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    message_id: str
    sender: str
    subject: str
    sanitized_body: str
    intent: str
    urgency: str
    sentiment: str
    confidence: float
    draft_response: Optional[str] = None
    kb_references: List[str] = Field(default_factory=list)
    is_draft: bool
    prompt_injection_flag: bool
    requires_escalation: bool
    escalation_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class EscalationRequest(BaseModel):
    ticket_id: str
    reason: str
    assigned_to: Optional[str] = "Tier 2 Support Lead"
