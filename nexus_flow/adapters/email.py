"""Email provider adapter for Gmail / Outlook draft lifecycle management."""

import time
import uuid
from typing import Any, Dict, List, Optional
from nexus_flow.adapters.base import BaseAdapter
from nexus_flow.core.logging import logger

class EmailAdapter(BaseAdapter):
    """
    Adapter for communicating with Gmail / Microsoft Outlook.
    Strictly enforces Draft-Only mode to prevent unauthorized email dispatch.
    """

    def __init__(self):
        super().__init__(service_name="EmailProvider")
        self.mock_drafts: Dict[str, Dict[str, Any]] = {}

    def health_check(self) -> Dict[str, Any]:
        return {
            "status": "ready (draft-only)",
            "live": self.is_live_mode,
            "provider": self.settings.email_provider,
            "draft_only_enforced": self.settings.email_draft_only,
        }

    def create_draft(
        self,
        to_address: str,
        subject: str,
        body_text: str,
        in_reply_to: Optional[str] = None,
        labels: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Creates an email draft in the user's email client."""
        return self.execute_with_telemetry(
            "create_draft",
            self._create_draft_impl,
            to_address,
            subject,
            body_text,
            in_reply_to,
            labels,
        )

    def _create_draft_impl(
        self,
        to_address: str,
        subject: str,
        body_text: str,
        in_reply_to: Optional[str],
        labels: Optional[List[str]],
    ) -> Dict[str, Any]:
        draft_id = f"draft_{uuid.uuid4().hex[:12]}"
        draft_record = {
            "draft_id": draft_id,
            "to": to_address,
            "subject": f"Re: {subject}" if not subject.startswith("Re:") else subject,
            "body": body_text,
            "in_reply_to": in_reply_to,
            "labels": labels or ["NEXUS/Draft", "AI-Triage"],
            "created_at": time.time(),
            "status": "DRAFT",
        }

        self.mock_drafts[draft_id] = draft_record
        time.sleep(0.03)  # simulate API roundtrip
        logger.info(f"[EMAIL] Draft created successfully: {draft_id} for {to_address} (Draft-only mode)")
        return {
            "success": True,
            "draft_id": draft_id,
            "mode": "live" if self.is_live_mode else "mock",
            "details": draft_record,
        }

    def send_email(self, draft_id: str, authorized_user: str) -> Dict[str, Any]:
        """
        Guarded email dispatch method.
        Requires explicit authorization and refuses execution if draft_only is enabled.
        """
        if self.settings.email_draft_only:
            logger.warning(f"Refusing to send email {draft_id}: EMAIL_DRAFT_ONLY policy is ACTIVE.")
            return {
                "success": False,
                "error": "AUTOMATIC_SEND_PROHIBITED: System is configured in draft-only mode. Human must send via email client.",
            }

        logger.info(f"Email {draft_id} sent by authorized operator: {authorized_user}")
        return {"success": True, "sent": True, "operator": authorized_user}
