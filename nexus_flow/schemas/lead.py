"""Pydantic schemas for the Lead Intelligence Engine."""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class LeadIngestRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    company: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=50)
    budget: Optional[float] = Field(default=0.0, ge=0.0)
    company_size: Optional[str] = Field(default="1-10", max_length=50)
    needs_description: Optional[str] = Field(default=None, max_length=5000)
    source: str = Field(default="web_form", max_length=100)
    consent: bool = Field(default=True)

class LeadQualificationResult(BaseModel):
    score: int = Field(ge=0, le=100)
    priority: str
    status: str
    confidence: float
    rationale: str
    ai_summary: str
    talking_points: List[str]
    missing_fields: List[str]
    assigned_rep: str

class LeadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    full_name: str
    company: Optional[str] = None
    phone: Optional[str] = None
    budget: Optional[float] = 0.0
    company_size: Optional[str] = None
    needs_description: Optional[str] = None
    source: str
    consent: bool
    score: int
    priority: str
    status: str
    confidence: float
    ai_summary: Optional[str] = None
    talking_points: List[str] = Field(default_factory=list)
    missing_fields: List[str] = Field(default_factory=list)
    airtable_record_id: Optional[str] = None
    slack_notified: bool
    latency_seconds: float
    created_at: datetime
    updated_at: datetime

