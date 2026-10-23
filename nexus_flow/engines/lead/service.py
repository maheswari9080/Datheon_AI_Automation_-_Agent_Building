"""Lead Intelligence Engine: Ingestion, normalization, validation, and deduplication."""

import json
import time
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from nexus_flow.core.config import get_settings
from nexus_flow.core.constants import LeadPriority, LeadStatus, EventType
from nexus_flow.core.logging import logger, log_audit_event
from nexus_flow.core.security import compute_content_hash, sanitize_untrusted_text
from nexus_flow.db.models import LeadRecord, AuditEventRecord
from nexus_flow.schemas.lead import LeadIngestRequest, LeadQualificationResult, LeadResponse
from nexus_flow.adapters.airtable import AirtableAdapter
from nexus_flow.adapters.slack import SlackAdapter
from nexus_flow.ai.client import AIClient

class LeadEngine:
    """Orchestrates multi-source inbound lead processing, scoring, and external routing."""

    def __init__(
        self,
        db: Session,
        airtable: Optional[AirtableAdapter] = None,
        slack: Optional[SlackAdapter] = None,
        ai: Optional[AIClient] = None,
    ):
        self.db = db
        self.settings = get_settings()
        self.airtable = airtable or AirtableAdapter()
        self.slack = slack or SlackAdapter()
        self.ai = ai or AIClient()

    def normalize_and_validate(self, req: LeadIngestRequest) -> Tuple[Dict[str, Any], List[str]]:
        """Cleanses input fields, enforces sanitization, and detects missing information."""
        missing_fields = []
        clean_email = str(req.email).strip().lower()
        clean_name, _ = sanitize_untrusted_text(req.full_name)
        clean_company, _ = sanitize_untrusted_text(req.company or "")
        clean_phone, _ = sanitize_untrusted_text(req.phone or "")
        clean_needs, _ = sanitize_untrusted_text(req.needs_description or "")

        if not req.budget or req.budget <= 0:
            missing_fields.append("budget")
        if not req.company:
            missing_fields.append("company")
        if not req.phone:
            missing_fields.append("phone")
        if not req.needs_description:
            missing_fields.append("needs_description")

        normalized = {
            "email": clean_email,
            "full_name": clean_name,
            "company": clean_company or "Unknown Company",
            "phone": clean_phone or "N/A",
            "budget": float(req.budget or 0.0),
            "company_size": req.company_size or "1-10",
            "needs_description": clean_needs,
            "source": req.source,
            "consent": req.consent,
        }
        return normalized, missing_fields

    def check_duplicate(self, email: str, company: str) -> Optional[LeadRecord]:
        """Detects whether an identical lead submission occurred within the last 24 hours."""
        content_hash = compute_content_hash(f"{email}:{company}")
        time_threshold = datetime.now(timezone.utc) - timedelta(hours=24)
        
        return (
            self.db.query(LeadRecord)
            .filter(
                LeadRecord.content_hash == content_hash,
                LeadRecord.created_at >= time_threshold,
            )
            .first()
        )
