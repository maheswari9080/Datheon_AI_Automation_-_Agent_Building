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

# Standard authorized corporate legal templates
CONTRACT_TEMPLATES = {
    "MSA-v2.1": """MASTER SERVICES AGREEMENT (MSA-v2.1)
This Master Services Agreement is entered into as of {effective_date} by and between:
Service Provider: NEXUS Flow AI Operations Hub
Client: {client_name} ({client_email})
Project Identifier: {project_code}

1. SCOPE OF SERVICES:
The Service Provider agrees to deliver enterprise automation engineering services under the '{service_tier}' plan.

2. COMPENSATION & PAYMENT TERMS:
Invoicing is executed under Net-30 payment terms via Stripe or verified ACH. All amounts are subject to audit reconciliation.

3. CONFIDENTIALITY & DATA PROTECTION:
Both parties agree to treat all business information, workflow configurations, and customer communications as confidential.

4. LIMITATION OF LIABILITY:
Neither party shall be liable for indirect, incidental, or consequential damages.

DISCLAIMER: This document is an automated operational draft and requires human legal counsel review prior to binding execution.
Signatory Client: ___________________________
Signatory Provider: _________________________
""",
    "SOW-v2.1": """STATEMENT OF WORK (SOW-v2.1)
Project: {project_code}
Client: {client_name}
Tier: {service_tier}
Effective Date: {effective_date}

Deliverables:
- Autonomous Lead & Support Intelligence Pipeline setup
- Automated Financial Document Processing (Invoice Engine)
- Unified Command Center Telemetry configuration

Signatures Required: [ ] Approved
"""
}

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

        at_payload = {
            "Project Code": project_code,
            "Client Name": clean_name,
            "Client Email": clean_email,
            "Service Tier": req.service_tier,
            "Status": ProjectStatus.INTAKE.value,
        }
        at_res = self.airtable.create_or_update_project(at_payload)

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

    def prepare_contract_draft(self, req: ContractDraftRequest) -> Dict[str, Any]:
        """
        Populates approved legal template without inventing clauses.
        Enforces human review by locking status in PENDING.
        """
        project = self.db.query(ProjectRecord).filter(ProjectRecord.id == req.project_id).first()
        if not project:
            raise ValueError(f"Project {req.project_id} not found")

        template_key = req.template_version or "MSA-v2.1"
        template = CONTRACT_TEMPLATES.get(template_key, CONTRACT_TEMPLATES["MSA-v2.1"])

        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        contract_text = template.format(
            effective_date=now_str,
            client_name=project.client_name,
            client_email=project.client_email,
            project_code=project.project_code,
            service_tier=project.service_tier,
        )

        missing_fields = []
        if "@" not in project.client_email:
            missing_fields.append("client_email")

        contract = ContractRecord(
            project_id=project.id,
            template_version=template_key,
            contract_text=contract_text,
            missing_fields=json.dumps(missing_fields),
            approval_status="PENDING",  # strictly requires human signoff
        )
        self.db.add(contract)
        project.contract_status = "DRAFTED"
        project.status = ProjectStatus.CONTRACT_DRAFTED.value

        # Register human approval request
        approval = ApprovalRequestRecord(
            entity_type="contract_approval",
            entity_id=contract.id,
            title=f"Contract Approval: {project.project_code} ({template_key})",
            description=f"Client: {project.client_name} ({project.client_email})\nTier: {project.service_tier}",
            status="PENDING",
            requested_by="Contract Preparation Engine",
        )
        self.db.add(approval)
        self.db.commit()
        self.db.refresh(contract)

        logger.info(f"Contract draft generated: {contract.id} for project {project.project_code}")
        return {
            "contract_id": contract.id,
            "project_code": project.project_code,
            "template_version": template_key,
            "approval_status": contract.approval_status,
            "contract_text": contract_text,
            "record": contract,
        }

    def approve_contract(self, contract_id: str, approved_by: str = "Legal Counsel") -> Dict[str, Any]:
        """Approves a contract draft, advancing project to PAYMENT_PENDING."""
        contract = self.db.query(ContractRecord).filter(ContractRecord.id == contract_id).first()
        if not contract:
            raise ValueError(f"Contract {contract_id} not found")

        contract.approval_status = "APPROVED"
        contract.approved_by = approved_by
        contract.approved_at = datetime.now(timezone.utc)

        project = self.db.query(ProjectRecord).filter(ProjectRecord.id == contract.project_id).first()
        if project:
            project.contract_status = "APPROVED"
            project.status = ProjectStatus.PAYMENT_PENDING.value

        # Resolve approval request
        app = (
            self.db.query(ApprovalRequestRecord)
            .filter(
                ApprovalRequestRecord.entity_type == "contract_approval",
                ApprovalRequestRecord.entity_id == contract_id,
            )
            .first()
        )
        if app:
            app.status = "APPROVED"
            app.resolved_by = approved_by
            app.resolved_at = datetime.now(timezone.utc)

        self.db.commit()
        logger.info(f"Contract {contract_id} approved by {approved_by}")
        return {"success": True, "contract_id": contract_id, "approval_status": "APPROVED"}
