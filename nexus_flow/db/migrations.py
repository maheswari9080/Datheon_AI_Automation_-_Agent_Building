"""Database migrations and PostgreSQL DDL generation utility."""

from sqlalchemy.schema import CreateTable
from nexus_flow.db.session import engine, init_db, Base
from nexus_flow.db.models import (
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

def generate_postgres_ddl() -> str:
    """Generates standard PostgreSQL DDL statements for all registered tables."""
    from sqlalchemy.dialects import postgresql
    ddl_statements = []
    tables = [
        LeadRecord.__table__,
        SupportTicketRecord.__table__,
        InvoiceRecord.__table__,
        InvoiceLineItemRecord.__table__,
        ProjectRecord.__table__,
        ContractRecord.__table__,
        PaymentRecord.__table__,
        AuditEventRecord.__table__,
        ApprovalRequestRecord.__table__,
    ]
    for table in tables:
        ddl = str(CreateTable(table).compile(dialect=postgresql.dialect())).strip()
        ddl_statements.append(f"{ddl};")
    return "\n\n".join(ddl_statements)

if __name__ == "__main__":
    init_db()
    print("Local SQLite tables created successfully.")
    ddl = generate_postgres_ddl()
    with open("postgres_schema.sql", "w", encoding="utf-8") as f:
        f.write("-- NEXUS Flow AI PostgreSQL Production Schema\n")
        f.write("-- Generated for production migration\n\n")
        f.write(ddl)
    print("PostgreSQL migration schema generated in postgres_schema.sql.")
