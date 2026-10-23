"""Pydantic schemas for Enterprise Orchestration Engine."""

from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class CustomerIntakeRequest(BaseModel):
    client_name: str = Field(..., min_length=2, max_length=255)
    client_email: EmailStr
    service_tier: str = Field(default="Enterprise Operations Tier")
    scope_summary: Optional[str] = None
    estimated_budget: Optional[float] = 10000.0

class ProjectResponse(BaseModel):
    id: str
    project_code: str
    client_name: str
    client_email: str
    service_tier: str
    status: str
    contract_status: str
    payment_status: str
    slack_channel: Optional[str] = None
    airtable_record_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ContractDraftRequest(BaseModel):
    project_id: str
    template_version: Optional[str] = "MSA-v2.1"
    special_terms: Optional[str] = None

class ContractResponse(BaseModel):
    id: str
    project_id: str
    template_version: str
    contract_text: str
    missing_fields: List[str] = Field(default_factory=list)
    approval_status: str
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class StripeWebhookPayload(BaseModel):
    id: str
    type: str
    data: Dict[str, Any]

class ExecutiveDigestResponse(BaseModel):
    period_start: str
    period_end: str
    generated_at: str
    source_coverage: str
    metrics: Dict[str, Any]
    ai_executive_summary: str
    pending_approvals_count: int
    system_health_status: str
