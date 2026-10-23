"""Database persistence layer with SQLAlchemy 2.0 models and sessions."""

from nexus_flow.db.session import engine, SessionLocal, get_db, init_db
from nexus_flow.db.models import (
    Base,
    LeadRecord,
    SupportTicketRecord,
    InvoiceRecord,
    InvoiceLineItemRecord,
    ProjectRecord,
    ContractRecord,
    PaymentRecord,
    AuditEventRecord,
    ApprovalRequestRecord,
)

__all__ = [
    "engine",
    "SessionLocal",
    "get_db",
    "init_db",
    "Base",
    "LeadRecord",
    "SupportTicketRecord",
    "InvoiceRecord",
    "InvoiceLineItemRecord",
    "ProjectRecord",
    "ContractRecord",
    "PaymentRecord",
    "AuditEventRecord",
    "ApprovalRequestRecord",
]
