"""Lead Intelligence Engine: Ingestion, normalization, validation, scoring, and routing."""

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

    def calculate_score(
        self, budget: float, company_size: str, missing_fields: List[str], consent: bool
    ) -> Tuple[int, str, str, str]:
        """
        Evaluates qualification heuristics.
        Returns: (score, priority, status, assigned_rep)
        """
        if not consent:
            return 0, LeadPriority.UNQUALIFIED.value, LeadStatus.DISQUALIFIED.value, "Unassigned"

        score = 0

        # 1. Budget Score (0-40)
        if budget >= 50000:
            score += 40
        elif budget >= 20000:
            score += 30
        elif budget >= 5000:
            score += 20
        elif budget >= 1000:
            score += 10
        else:
            score += 0

        # 2. Company Size Score (0-30)
        size_str = company_size.lower()
        if any(k in size_str for k in ["500+", "1000+", "enterprise"]):
            score += 30
        elif any(k in size_str for k in ["51-200", "201-500", "mid-market"]):
            score += 25
        elif any(k in size_str for k in ["11-50", "growth"]):
            score += 15
        else:
            score += 10

        # 3. Completeness Score (0-30)
        penalty = len(missing_fields) * 8
        completeness = max(0, 30 - penalty)
        score += completeness

        # Priority and Rep Routing
        if score >= 75:
            priority = LeadPriority.HOT.value
            status = LeadStatus.QUALIFIED.value
            rep = "Enterprise Director - Sarah Jenkins"
        elif score >= 50:
            priority = LeadPriority.WARM.value
            status = LeadStatus.QUALIFIED.value
            rep = "Senior Account Exec - Marcus Vance"
        elif score >= 25:
            priority = LeadPriority.COLD.value
            status = LeadStatus.NEW.value
            rep = "Inbound SDR - Elena Rostova"
        else:
            priority = LeadPriority.UNQUALIFIED.value
            status = LeadStatus.DISQUALIFIED.value
            rep = "Automated Marketing Nurture"

        return score, priority, status, rep

    def process_lead(self, req: LeadIngestRequest) -> Dict[str, Any]:
        """
        Executes end-to-end lead workflow:
        Validation -> Deduplication -> Rule Scoring -> AI Synthesis -> Airtable Sync -> Slack Alert.
        Tracks SLA latency with a target of under 10 seconds.
        """
        start_time = time.perf_counter()

        # Step 1: Validation & Normalization
        norm_data, missing_fields = self.normalize_and_validate(req)

        # Step 2: Deduplication Check
        existing = self.check_duplicate(norm_data["email"], norm_data["company"])
        if existing:
            elapsed = time.perf_counter() - start_time
            logger.info(f"Duplicate lead detected for {norm_data['email']}. Returning existing record.")
            return {
                "lead_id": existing.id,
                "is_duplicate": True,
                "score": existing.score,
                "priority": existing.priority,
                "status": existing.status,
                "execution_seconds": round(elapsed, 3),
                "record": existing,
            }

        # Step 3: Heuristic Business Rule Scoring
        score, priority, status, assigned_rep = self.calculate_score(
            norm_data["budget"], norm_data["company_size"], missing_fields, norm_data["consent"]
        )

        # Step 4: AI Strategic Analysis
        ai_res = self.ai.analyze_lead(
            company=norm_data["company"],
            budget=norm_data["budget"],
            company_size=norm_data["company_size"],
            needs=norm_data["needs_description"],
        )
        ai_summary = ai_res.get("summary", "Inbound sales inquiry.")
        talking_points = ai_res.get("talking_points", [])

        # Step 5: External Sync - Airtable
        airtable_payload = {
            "Email": norm_data["email"],
            "Name": norm_data["full_name"],
            "Company": norm_data["company"],
            "Budget": norm_data["budget"],
            "Score": score,
            "Priority": priority,
            "Status": status,
            "Assigned Rep": assigned_rep,
        }
        airtable_res = self.airtable.create_or_update_lead(airtable_payload)
        airtable_id = airtable_res.get("record_id")

        # Step 6: External Sync - Slack Alert
        channel = self.settings.slack_sales_channel if priority in ["HOT", "WARM"] else self.settings.slack_default_channel
        slack_msg = (
            f"*Company:* {norm_data['company']} | *Contact:* {norm_data['full_name']} ({norm_data['email']})\n"
            f"*Budget:* ${norm_data['budget']:,.2f} | *Score:* {score}/100 ({priority})\n"
            f"*Assigned Rep:* {assigned_rep}\n"
            f"*AI Summary:* {ai_summary}"
        )
        slack_res = self.slack.send_notification(
            channel=channel,
            title=f"New Lead Qualified: {norm_data['company']} [{priority}]",
            message=slack_msg,
            priority=priority,
            metadata={
                "Score": f"{score}/100",
                "Budget": f"${norm_data['budget']:,.2f}",
                "Rep": assigned_rep,
                "Airtable": airtable_id or "Synced",
            },
        )

        # Step 7: Latency & Persistence
        elapsed_seconds = time.perf_counter() - start_time
        content_hash = compute_content_hash(f"{norm_data['email']}:{norm_data['company']}")

        lead_record = LeadRecord(
            email=norm_data["email"],
            full_name=norm_data["full_name"],
            company=norm_data["company"],
            phone=norm_data["phone"],
            budget=norm_data["budget"],
            company_size=norm_data["company_size"],
            needs_description=norm_data["needs_description"],
            source=norm_data["source"],
            consent=norm_data["consent"],
            score=score,
            priority=priority,
            status=status,
            confidence=0.95,
            ai_summary=ai_summary,
            talking_points=json.dumps(talking_points),
            missing_fields=json.dumps(missing_fields),
            airtable_record_id=airtable_id,
            slack_notified=slack_res.get("success", False),
            latency_seconds=round(elapsed_seconds, 3),
            content_hash=content_hash,
        )
        self.db.add(lead_record)

        audit = AuditEventRecord(
            event_type=EventType.LEAD_QUALIFIED.value,
            action="QUALIFY_AND_ROUTE",
            status="SUCCESS",
            entity_id=lead_record.id,
            duration_ms=round(elapsed_seconds * 1000, 2),
            details_json=json.dumps({
                "score": score,
                "priority": priority,
                "sla_met": elapsed_seconds < self.settings.lead_sla_max_seconds,
            }),
        )
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(lead_record)

        logger.info(
            f"Lead {lead_record.id} processed in {elapsed_seconds:.2f}s (SLA target: <{self.settings.lead_sla_max_seconds}s)"
        )

        return {
            "lead_id": lead_record.id,
            "is_duplicate": False,
            "score": score,
            "priority": priority,
            "status": status,
            "assigned_rep": assigned_rep,
            "ai_summary": ai_summary,
            "talking_points": talking_points,
            "missing_fields": missing_fields,
            "airtable_record_id": airtable_id,
            "slack_notified": slack_res.get("success", False),
            "execution_seconds": round(elapsed_seconds, 3),
            "sla_met": elapsed_seconds < self.settings.lead_sla_max_seconds,
            "record": lead_record,
        }

    def list_leads(self, priority: Optional[str] = None, status: Optional[str] = None, limit: int = 50) -> List[LeadRecord]:
        query = self.db.query(LeadRecord)
        if priority:
            query = query.filter(LeadRecord.priority == priority.upper())
        if status:
            query = query.filter(LeadRecord.status == status.upper())
        return query.order_by(LeadRecord.created_at.desc()).limit(limit).all()

    def get_lead(self, lead_id: str) -> Optional[LeadRecord]:
        return self.db.query(LeadRecord).filter(LeadRecord.id == lead_id).first()
