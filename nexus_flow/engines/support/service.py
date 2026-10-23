"""Support Intelligence Engine: Email ingestion, triage, grounded drafting, and escalation."""

import json
import uuid
import time
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

    def retrieve_grounding_evidence(self, query: str, intent: str) -> List[Dict[str, Any]]:
        """Retrieves approved knowledge base articles relevant to the inquiry."""
        return self.kb.search(query=query, category=intent, top_k=2)

    def generate_grounded_draft(
        self, ticket_data: Dict[str, Any], kb_articles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Drafts a response strictly grounded in verified documentation, enforcing draft-only mode."""
        draft_result = self.ai.draft_grounded_support_response(ticket_data, kb_articles)

        # Register draft in email adapter (enforces draft-only)
        self.email_adapter.create_draft(
            to_address=ticket_data["sender"],
            subject=ticket_data["subject"],
            body_text=draft_result["draft_body"],
            in_reply_to=ticket_data["message_id"],
            labels=["NEXUS/Support-Draft", f"Intent/{ticket_data.get('intent', 'general')}"],
        )

        return draft_result

    def process_ticket(self, req: SupportIngestRequest) -> Dict[str, Any]:
        """
        End-to-end Support workflow:
        Ingestion -> Prompt Sanitization -> 8-Way Classification -> KB Grounding -> Draft Creation -> Escalation Routing.
        """
        start_time = time.perf_counter()

        # Step 1: Ingestion & Security Filter
        ticket_data, injection_flag = self.ingest_and_sanitize(req)

        # Step 2: Intent, Urgency, & Sentiment Triage
        triage_res = self.classify_email(ticket_data["subject"], ticket_data["sanitized_body"])
        intent = triage_res.get("intent", SupportIntent.UNKNOWN.value)
        urgency = triage_res.get("urgency", SupportUrgency.P4_LOW.value)
        sentiment = triage_res.get("sentiment", SupportSentiment.NEUTRAL.value)
        confidence = float(triage_res.get("confidence", 0.9))

        ticket_data["intent"] = intent
        ticket_data["urgency"] = urgency
        ticket_data["sentiment"] = sentiment

        # Step 3: Grounded Knowledge Retrieval
        kb_articles = self.retrieve_grounding_evidence(
            f"{ticket_data['subject']} {ticket_data['sanitized_body']}", intent
        )

        # Step 4: Grounded Response Drafting (Draft-Only Mode)
        draft_res = self.generate_grounded_draft(ticket_data, kb_articles)
        draft_body = draft_res["draft_body"]
        kb_refs = draft_res["kb_references"]

        # Step 5: Escalation Guardrails Evaluation
        requires_escalation = triage_res.get("requires_escalation", False)
        escalation_reason = triage_res.get("escalation_reason")

        if injection_flag:
            requires_escalation = True
            escalation_reason = "Security: Suspected prompt injection attempt detected."

        # Step 6: Database Persistence
        ticket_record = SupportTicketRecord(
            message_id=ticket_data["message_id"],
            sender=ticket_data["sender"],
            subject=ticket_data["subject"],
            raw_body=ticket_data["raw_body"],
            sanitized_body=ticket_data["sanitized_body"],
            intent=intent,
            urgency=urgency,
            sentiment=sentiment,
            confidence=confidence,
            draft_response=draft_body,
            kb_references=json.dumps(kb_refs),
            is_draft=True,  # Enforces draft-only
            prompt_injection_flag=injection_flag,
            requires_escalation=requires_escalation,
            escalation_reason=escalation_reason,
        )
        self.db.add(ticket_record)

        # If escalation triggered, register an approval request and dispatch priority alert
        if requires_escalation:
            approval = ApprovalRequestRecord(
                entity_type="support_escalation",
                entity_id=ticket_record.id,
                title=f"Support Escalation [{urgency}]: {ticket_data['subject'][:60]}",
                description=f"Reason: {escalation_reason}\nSender: {ticket_data['sender']}\nIntent: {intent}",
                status="PENDING",
                requested_by="Support Intelligence Engine",
            )
            self.db.add(approval)

            self.slack_adapter.send_notification(
                channel=self.settings.slack_support_channel,
                title=f"Support Escalation: {ticket_data['subject'][:50]}",
                message=f"*Sender:* {ticket_data['sender']}\n*Urgency:* {urgency} | *Intent:* {intent}\n*Reason:* {escalation_reason}",
                priority="CRITICAL" if urgency == SupportUrgency.P1_CRITICAL.value else "HIGH",
                metadata={"Urgency": urgency, "Sentiment": sentiment, "Ticket ID": ticket_record.id},
            )

        duration_ms = (time.perf_counter() - start_time) * 1000
        audit = AuditEventRecord(
            event_type=EventType.SUPPORT_DRAFT_GENERATED.value,
            action="TRIAGE_AND_DRAFT",
            status="SUCCESS",
            entity_id=ticket_record.id,
            duration_ms=round(duration_ms, 2),
            details_json=json.dumps({
                "intent": intent,
                "urgency": urgency,
                "sentiment": sentiment,
                "requires_escalation": requires_escalation,
                "draft_only": True,
            }),
        )
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(ticket_record)

        logger.info(
            f"Support ticket {ticket_record.id} processed in {duration_ms:.2f}ms (Intent={intent}, Urgency={urgency})"
        )

        return {
            "ticket_id": ticket_record.id,
            "message_id": ticket_data["message_id"],
            "intent": intent,
            "urgency": urgency,
            "sentiment": sentiment,
            "draft_body": draft_body,
            "kb_references": kb_refs,
            "prompt_injection_flag": injection_flag,
            "requires_escalation": requires_escalation,
            "escalation_reason": escalation_reason,
            "is_draft": True,
            "duration_ms": round(duration_ms, 2),
            "record": ticket_record,
        }

    def list_tickets(
        self, intent: Optional[str] = None, urgency: Optional[str] = None, limit: int = 50
    ) -> List[SupportTicketRecord]:
        query = self.db.query(SupportTicketRecord)
        if intent:
            query = query.filter(SupportTicketRecord.intent == intent)
        if urgency:
            query = query.filter(SupportTicketRecord.urgency == urgency.upper())
        return query.order_by(SupportTicketRecord.created_at.desc()).limit(limit).all()

    def get_ticket(self, ticket_id: str) -> Optional[SupportTicketRecord]:
        return self.db.query(SupportTicketRecord).filter(SupportTicketRecord.id == ticket_id).first()
