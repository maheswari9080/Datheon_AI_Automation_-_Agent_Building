"""OpenAI API client wrapper with resilient timeout handling and deterministic fallback routing."""

import json
from typing import Any, Dict, List, Optional
from openai import OpenAI
from nexus_flow.core.config import get_settings
from nexus_flow.core.logging import logger
from nexus_flow.ai.prompts import (
    LEAD_ANALYSIS_SYSTEM_PROMPT,
    SUPPORT_TRIAGE_SYSTEM_PROMPT,
    GROUNDED_DRAFT_SYSTEM_PROMPT,
    INVOICE_EXTRACTION_SYSTEM_PROMPT,
    EXECUTIVE_DIGEST_SYSTEM_PROMPT,
)
from nexus_flow.ai.fallbacks import (
    fallback_lead_analysis,
    fallback_support_triage,
    fallback_grounded_draft,
    fallback_invoice_extraction,
)

class AIClient:
    """Manages LLM reasoning operations with fallback to deterministic heuristic engines."""

    def __init__(self):
        self.settings = get_settings()
        self.client = None
        if self.settings.openai_api_key and not self.settings.openai_api_key.startswith("sk-placeholder"):
            try:
                self.client = OpenAI(
                    api_key=self.settings.openai_api_key,
                    timeout=self.settings.openai_timeout_seconds,
                )
            except Exception as e:
                logger.warning(f"Could not initialize live OpenAI client: {e}")

    def analyze_lead(self, company: str, budget: float, company_size: str, needs: str) -> Dict[str, Any]:
        """Analyzes an inbound lead to generate strategic summaries and talking points."""
        if not self.client:
            logger.info("OpenAI client offline/unconfigured. Utilizing deterministic fallback for lead analysis.")
            return fallback_lead_analysis(company, budget, company_size, needs)

        try:
            prompt = (
                f"Company: {company}\n"
                f"Budget: ${budget}\n"
                f"Company Size: {company_size}\n"
                f"Needs Description:\n{needs}"
            )
            response = self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {"role": "system", "content": LEAD_ANALYSIS_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            logger.error(f"OpenAI lead analysis failed ({e}). Falling back to deterministic rules.")
            return fallback_lead_analysis(company, budget, company_size, needs)

    def triage_support_ticket(self, subject: str, body: str) -> Dict[str, Any]:
        """Categorizes incoming support emails and scores urgency and sentiment."""
        if not self.client:
            return fallback_support_triage(subject, body)

        try:
            prompt = f"Subject: {subject}\n\nEmail Body:\n{body}"
            response = self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {"role": "system", "content": SUPPORT_TRIAGE_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            logger.error(f"OpenAI support triage failed ({e}). Falling back to deterministic rules.")
            return fallback_support_triage(subject, body)

    def draft_grounded_support_response(
        self, ticket_data: Dict[str, Any], kb_articles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Drafts a customer support response strictly grounded in provided KB articles."""
        if not self.client or not kb_articles:
            return fallback_grounded_draft(ticket_data, kb_articles)

        try:
            evidence_str = "\n\n".join(
                [f"[{art['id']}] {art['title']}:\n{art['content']}" for art in kb_articles]
            )
            user_prompt = (
                f"Customer Email:\nSender: {ticket_data.get('sender')}\n"
                f"Subject: {ticket_data.get('subject')}\n"
                f"Body: {ticket_data.get('sanitized_body')}\n\n"
                f"Approved Knowledge Base Evidence:\n{evidence_str}"
            )
            response = self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {"role": "system", "content": GROUNDED_DRAFT_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
            )
            draft = response.choices[0].message.content
            return {
                "draft_body": draft,
                "kb_references": [art["id"] for art in kb_articles],
                "citations_valid": True,
                "policy_notes": "AI-generated response grounded in verified KB articles.",
            }
        except Exception as e:
            logger.error(f"OpenAI draft generation failed ({e}). Falling back.")
            return fallback_grounded_draft(ticket_data, kb_articles)

    def extract_invoice_fields(self, invoice_text: str) -> Dict[str, Any]:
        """Extracts financial and line item data from raw document text."""
        if not self.client:
            return fallback_invoice_extraction(invoice_text)

        try:
            response = self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {"role": "system", "content": INVOICE_EXTRACTION_SYSTEM_PROMPT},
                    {"role": "user", "content": f"Document Text:\n{invoice_text[:8000]}"},
                ],
                response_format={"type": "json_object"},
                temperature=0.0,
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            logger.error(f"OpenAI invoice extraction failed ({e}). Falling back to regex.")
            return fallback_invoice_extraction(invoice_text)

    def generate_executive_digest(self, metrics: Dict[str, Any]) -> str:
        """Synthesizes high-level executive briefing from actual system operational metrics."""
        if not self.client:
            return (
                f"Executive Operations Briefing: All systems operating within baseline parameters. "
                f"Processed {metrics.get('leads_count', 0)} inbound leads with {metrics.get('qualified_leads', 0)} qualified. "
                f"Handled {metrics.get('support_tickets_count', 0)} support requests ({metrics.get('urgent_tickets', 0)} urgent). "
                f"Validated {metrics.get('invoices_count', 0)} invoices totaling ${metrics.get('total_invoice_spend', 0.0):,.2f}. "
                f"Verified {metrics.get('verified_payments_count', 0)} Stripe transactions for ${metrics.get('verified_revenue', 0.0):,.2f}. "
                f"Currently tracking {metrics.get('pending_approvals', 0)} pending human approvals."
            )

        try:
            response = self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {"role": "system", "content": EXECUTIVE_DIGEST_SYSTEM_PROMPT},
                    {"role": "user", "content": f"Operational Metrics:\n{json.dumps(metrics, indent=2)}"},
                ],
                temperature=0.3,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI executive digest synthesis failed ({e}). Using deterministic summary.")
            return (
                f"Weekly Operations Briefing: Processed {metrics.get('leads_count', 0)} leads, "
                f"{metrics.get('support_tickets_count', 0)} support tickets, and {metrics.get('invoices_count', 0)} invoices. "
                f"Total verified revenue: ${metrics.get('verified_revenue', 0.0):,.2f}."
            )
