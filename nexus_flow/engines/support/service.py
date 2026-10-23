"""Support Intelligence Engine: Email ingestion, prompt defense, 8-intent triage, and urgency scoring."""

import json
import uuid
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from nexus_flow.core.config import get_settings
from nexus_flow.core.constants import SupportIntent, SupportUrgency, SupportSentiment, EventType
from nexus_flow.core.logging import logger, log_audit_event
from nexus_flow.core.security import sanitize_untrusted_text
from nexus_flow.db.models import SupportTicketRecord, AuditEventRecord, ApprovalRequestRecord
from nexus_flow.schemas.support import SupportIngestRequest, SupportTicketResponse
from nexus_flow.adapters.email import EmailAdapter
from nexus_flow.adapters.slack import SlackAdapter
from nexus_flow.ai.client import AIClient
from nexus_flow.knowledge.engine import KnowledgeBaseEngine

class SupportEngine:
    """Manages AI-assisted customer email triage, grounded drafting, and human escalation."""

    def __init__(
        self,
        db: Session,
        email_adapter: Optional[EmailAdapter] = None,
        slack_adapter: Optional[SlackAdapter] = None,
        ai: Optional[AIClient] = None,
        kb: Optional[KnowledgeBaseEngine] = None,
    ):
        self.db = db
        self.settings = get_settings()
        self.email_adapter = email_adapter or EmailAdapter()
        self.slack_adapter = slack_adapter or SlackAdapter()
        self.ai = ai or AIClient()
        self.kb = kb or KnowledgeBaseEngine()

    def ingest_and_sanitize(self, req: SupportIngestRequest) -> Tuple[Dict[str, Any], bool]:
        """Ingests email, extracts safe metadata, and runs prompt-injection defensive filter."""
        msg_id = req.message_id or f"msg_{uuid.uuid4().hex[:12]}"
        clean_subject, subj_inj = sanitize_untrusted_text(req.subject)
        clean_body, body_inj = sanitize_untrusted_text(req.body)
        injection_flag = subj_inj or body_inj

        if injection_flag:
            logger.warning(f"SECURITY ALERT: Prompt injection attempt detected in email {msg_id} from {req.sender}")

        data = {
            "message_id": msg_id,
            "sender": str(req.sender).strip().lower(),
            "subject": clean_subject,
            "sanitized_body": clean_body,
            "raw_body": req.body,
            "injection_flag": injection_flag,
        }
        return data, injection_flag

    def classify_email(self, subject: str, sanitized_body: str) -> Dict[str, Any]:
        """
        Classifies email intent into 8 discrete categories,
        evaluating urgency separately from customer sentiment.
        """
        return self.ai.triage_support_ticket(subject, sanitized_body)
