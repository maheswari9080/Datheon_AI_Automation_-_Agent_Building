"""Pydantic V2 data validation contracts for NEXUS Flow AI."""

from nexus_flow.schemas.common import (
    ApiResponse,
    HealthCheckResponse,
    ErrorDetail,
    AuditEventSchema,
)
from nexus_flow.schemas.lead import (
    LeadIngestRequest,
    LeadQualificationResult,
    LeadResponse,
)
from nexus_flow.schemas.support import (
    SupportIngestRequest,
    SupportTicketResponse,
    GroundedDraftResponse,
)
from nexus_flow.schemas.invoice import (
    LineItemCreate,
    ExtractedInvoiceData,
    ArithmeticValidationResult,
    InvoiceResponse,
)
from nexus_flow.schemas.orchestration import (
    CustomerIntakeRequest,
    ProjectResponse,
    ContractDraftRequest,
    ContractResponse,
    ExecutiveDigestResponse,
)

__all__ = [
    "ApiResponse",
    "HealthCheckResponse",
    "ErrorDetail",
    "AuditEventSchema",
    "LeadIngestRequest",
    "LeadQualificationResult",
    "LeadResponse",
    "SupportIngestRequest",
    "SupportTicketResponse",
    "GroundedDraftResponse",
    "LineItemCreate",
    "ExtractedInvoiceData",
    "ArithmeticValidationResult",
    "InvoiceResponse",
    "CustomerIntakeRequest",
    "ProjectResponse",
    "ContractDraftRequest",
    "ContractResponse",
    "ExecutiveDigestResponse",
]
