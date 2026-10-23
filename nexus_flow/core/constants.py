"""System constants, status enumerations, and category definitions."""

from enum import Enum

class LeadStatus(str, Enum):
    NEW = "NEW"
    QUALIFIED = "QUALIFIED"
    DISQUALIFIED = "DISQUALIFIED"
    ROUTED = "ROUTED"
    CONTACTED = "CONTACTED"

class LeadPriority(str, Enum):
    HOT = "HOT"
    WARM = "WARM"
    COLD = "COLD"
    UNQUALIFIED = "UNQUALIFIED"

class SupportIntent(str, Enum):
    BILLING = "billing"
    TECHNICAL_SUPPORT = "technical_support"
    ACCOUNT_ACCESS = "account_access"
    ORDER_INQUIRIES = "order_inquiries"
    COMPLAINTS = "complaints"
    URGENT_INCIDENTS = "urgent_incidents"
    SPAM = "spam"
    UNKNOWN = "unknown"

class SupportUrgency(str, Enum):
    P1_CRITICAL = "P1_CRITICAL"
    P2_HIGH = "P2_HIGH"
    P3_MEDIUM = "P3_MEDIUM"
    P4_LOW = "P4_LOW"

class SupportSentiment(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    FRUSTRATED = "frustrated"
    HOSTILE = "hostile"

class InvoiceStatus(str, Enum):
    PENDING_EXTRACTION = "PENDING_EXTRACTION"
    EXTRACTED = "EXTRACTED"
    FLAGGED_DISCREPANCY = "FLAGGED_DISCREPANCY"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPORTED = "EXPORTED"

class ProjectStatus(str, Enum):
    INTAKE = "INTAKE"
    CONTRACT_DRAFTED = "CONTRACT_DRAFTED"
    CONTRACT_APPROVED = "CONTRACT_APPROVED"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"

class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ESCALATED = "ESCALATED"

class EventType(str, Enum):
    LEAD_INGESTED = "lead.ingested"
    LEAD_QUALIFIED = "lead.qualified"
    SUPPORT_EMAIL_INGESTED = "support.email_ingested"
    SUPPORT_DRAFT_GENERATED = "support.draft_generated"
    SUPPORT_ESCALATED = "support.escalated"
    INVOICE_UPLOADED = "invoice.uploaded"
    INVOICE_EXTRACTED = "invoice.extracted"
    INVOICE_APPROVED = "invoice.approved"
    INVOICE_EXPORTED = "invoice.exported"
    PROJECT_CREATED = "project.created"
    CONTRACT_GENERATED = "contract.generated"
    PAYMENT_VERIFIED = "payment.verified"
    PAYMENT_FAILED = "payment.failed"
    SLACK_CHANNEL_PROVISIONED = "slack.channel_provisioned"
    WORKFLOW_ERROR = "workflow.error"
