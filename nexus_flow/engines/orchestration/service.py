"""Enterprise Orchestration Engine: Customer intake, contract prep, Stripe reconciliation, Slack collab, and digests."""

import json
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from nexus_flow.core.config import get_settings
from nexus_flow.core.constants import ProjectStatus, EventType
from nexus_flow.core.logging import logger, log_audit_event
from nexus_flow.core.security import sanitize_untrusted_text
from nexus_flow.db.models import (
    ProjectRecord,
    ContractRecord,
    PaymentRecord,
    AuditEventRecord,
    ApprovalRequestRecord,
)
from nexus_flow.schemas.orchestration import CustomerIntakeRequest, ContractDraftRequest
from nexus_flow.adapters.airtable import AirtableAdapter
from nexus_flow.adapters.slack import SlackAdapter
from nexus_flow.adapters.stripe import StripeAdapter
from nexus_flow.ai.client import AIClient

class OrchestrationEngine:
    """End-to-end Enterprise Operations Orchestrator connecting intake to executive intelligence."""

    def __init__(
        self,
        db: Session,
        airtable: Optional[AirtableAdapter] = None,
        slack: Optional[SlackAdapter] = None,
        stripe: Optional[StripeAdapter] = None,
        ai: Optional[AIClient] = None,
    ):
        self.db = db
        self.settings = get_settings()
        self.airtable = airtable or AirtableAdapter()
        self.slack = slack or SlackAdapter()
        self.stripe = stripe or StripeAdapter()
        self.ai = ai or AIClient()

    def generate_project_code(self) -> str:
        """Generates deterministic unique project code: PRJ-YYYYMM-XXXX."""
        now = datetime.now(timezone.utc)
        suffix = uuid.uuid4().hex[:4].upper()
        return f"PRJ-{now.strftime('%Y%m')}-{suffix}"

    def customer_intake(self, req: CustomerIntakeRequest) -> Dict[str, Any]:
        """
        Validates client data, detects duplicate projects, allocates project ID,
        and provisions tracking records in Airtable and database.
        """
        start_time = time.perf_counter()
        clean_name, _ = sanitize_untrusted_text(req.client_name)
        clean_email = str(req.client_email).strip().lower()

        # Check existing active project
        existing = (
            self.db.query(ProjectRecord)
            .filter(
                ProjectRecord.client_email == clean_email,
                ProjectRecord.status != ProjectStatus.COMPLETED.value,
            )
            .first()
        )
        if existing:
            logger.info(f"Existing active project {existing.project_code} found for client {clean_email}")
            return {
                "project_id": existing.id,
                "project_code": existing.project_code,
                "is_existing": True,
                "status": existing.status,
                "record": existing,
            }

        project_code = self.generate_project_code()

        # Provision Airtable record
        at_payload = {
            "Project Code": project_code,
            "Client Name": clean_name,
            "Client Email": clean_email,
            "Service Tier": req.service_tier,
            "Status": ProjectStatus.INTAKE.value,
        }
        at_res = self.airtable.create_or_update_project(at_payload)

        # Database record
        project = ProjectRecord(
            project_code=project_code,
            client_name=clean_name,
            client_email=clean_email,
            service_tier=req.service_tier,
            status=ProjectStatus.INTAKE.value,
            contract_status="PENDING",
            payment_status="UNPAID",
            airtable_record_id=at_res.get("record_id"),
        )
        self.db.add(project)

        duration_ms = (time.perf_counter() - start_time) * 1000
        audit = AuditEventRecord(
            event_type=EventType.PROJECT_CREATED.value,
            action="CUSTOMER_INTAKE",
            status="SUCCESS",
            entity_id=project.id,
            duration_ms=round(duration_ms, 2),
            details_json=json.dumps({"project_code": project_code, "client": clean_email}),
        )
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(project)

        logger.info(f"Project initialized: {project_code} for {clean_name}")
        return {
            "project_id": project.id,
            "project_code": project_code,
            "is_existing": False,
            "status": project.status,
            "airtable_record_id": at_res.get("record_id"),
            "duration_ms": round(duration_ms, 2),
            "record": project,
        }
