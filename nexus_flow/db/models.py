"""SQLAlchemy database models for NEXUS Flow AI."""

import json
import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from nexus_flow.db.session import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class LeadRecord(Base):
    __tablename__ = "leads"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    company = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    budget = Column(Float, nullable=True, default=0.0)
    company_size = Column(String(50), nullable=True)
    needs_description = Column(Text, nullable=True)
    source = Column(String(100), default="web_form")
    consent = Column(Boolean, default=True)

    # Qualification Results
    score = Column(Integer, default=0)
    priority = Column(String(50), default="UNQUALIFIED")
    status = Column(String(50), default="NEW")
    confidence = Column(Float, default=1.0)
    ai_summary = Column(Text, nullable=True)
    talking_points = Column(Text, nullable=True)  # JSON-encoded list
    missing_fields = Column(Text, nullable=True)  # JSON-encoded list

    # External Sync Metadata
    airtable_record_id = Column(String(100), nullable=True)
    slack_notified = Column(Boolean, default=False)
    latency_seconds = Column(Float, default=0.0)

    content_hash = Column(String(64), index=True, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

class SupportTicketRecord(Base):
    __tablename__ = "support_tickets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    message_id = Column(String(255), unique=True, index=True, nullable=False)
    sender = Column(String(255), nullable=False)
    subject = Column(String(500), nullable=False)
    raw_body = Column(Text, nullable=False)
    sanitized_body = Column(Text, nullable=False)

    # Classification
    intent = Column(String(50), default="unknown")
    urgency = Column(String(50), default="P4_LOW")
    sentiment = Column(String(50), default="neutral")
    confidence = Column(Float, default=1.0)

    # Response & Grounding
    draft_response = Column(Text, nullable=True)
    kb_references = Column(Text, nullable=True)  # JSON-encoded list
    is_draft = Column(Boolean, default=True)

    # Guardrails & Escalation
    prompt_injection_flag = Column(Boolean, default=False)
    requires_escalation = Column(Boolean, default=False)
    escalation_reason = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

class InvoiceRecord(Base):
    __tablename__ = "invoices"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    filename = Column(String(255), nullable=False)
    vendor = Column(String(255), nullable=True)
    invoice_number = Column(String(100), nullable=True, index=True)
    invoice_date = Column(String(50), nullable=True)
    currency = Column(String(10), default="USD")

    # Financial Extracted vs Computed Amounts
    subtotal = Column(Float, default=0.0)
    discount = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    extracted_total = Column(Float, default=0.0)
    calculated_total = Column(Float, default=0.0)
    is_arithmetic_valid = Column(Boolean, default=True)
    discrepancy_notes = Column(Text, nullable=True)
    duplicate_flag = Column(Boolean, default=False)

    status = Column(String(50), default="PENDING_EXTRACTION")
    payment_status = Column(String(50), default="UNPAID")
    google_sheets_row = Column(Integer, nullable=True)

    line_items = relationship("InvoiceLineItemRecord", back_populates="invoice", cascade="all, delete-orphan")
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

class InvoiceLineItemRecord(Base):
    __tablename__ = "invoice_line_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    invoice_id = Column(String(36), ForeignKey("invoices.id"), nullable=False)
    description = Column(String(500), nullable=False)
    quantity = Column(Float, default=1.0)
    unit_price = Column(Float, default=0.0)
    line_total = Column(Float, default=0.0)

    invoice = relationship("InvoiceRecord", back_populates="line_items")

class ProjectRecord(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_code = Column(String(50), unique=True, index=True, nullable=False)
    client_name = Column(String(255), nullable=False)
    client_email = Column(String(255), nullable=False)
    service_tier = Column(String(100), default="Standard Automation")
    status = Column(String(50), default="INTAKE")

    contract_status = Column(String(50), default="PENDING")
    payment_status = Column(String(50), default="UNPAID")
    slack_channel = Column(String(100), nullable=True)
    airtable_record_id = Column(String(100), nullable=True)

    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

class ContractRecord(Base):
    __tablename__ = "contracts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    template_version = Column(String(50), default="MSA-v2.1")
    contract_text = Column(Text, nullable=False)
    missing_fields = Column(Text, nullable=True)  # JSON-encoded list
    approval_status = Column(String(50), default="PENDING")
    approved_by = Column(String(255), nullable=True)
    approved_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

class PaymentRecord(Base):
    __tablename__ = "payments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    stripe_event_id = Column(String(255), unique=True, index=True, nullable=False)
    project_id = Column(String(36), nullable=True)
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String(10), default="usd")
    status = Column(String(50), default="verified")
    signature_verified = Column(Boolean, default=True)
    raw_payload = Column(Text, nullable=True)

    created_at = Column(DateTime, default=utc_now)

class AuditEventRecord(Base):
    __tablename__ = "audit_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    event_type = Column(String(100), index=True, nullable=False)
    action = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)
    entity_id = Column(String(100), nullable=True)
    duration_ms = Column(Float, nullable=True)
    details_json = Column(Text, nullable=True)

    created_at = Column(DateTime, default=utc_now)

class ApprovalRequestRecord(Base):
    __tablename__ = "approval_requests"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    entity_type = Column(String(50), nullable=False)  # invoice, contract, refund, escalation
    entity_id = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="PENDING")  # PENDING, APPROVED, REJECTED
    requested_by = Column(String(100), default="System")
    resolved_by = Column(String(100), nullable=True)
    resolution_notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=utc_now)
    resolved_at = Column(DateTime, nullable=True)
