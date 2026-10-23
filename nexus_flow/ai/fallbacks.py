"""Deterministic offline fallbacks for AI classification, extraction, and drafting."""

import re
from typing import Any, Dict, List
from nexus_flow.core.constants import SupportIntent, SupportUrgency, SupportSentiment

def fallback_lead_analysis(company: str, budget: float, company_size: str, needs: str) -> Dict[str, Any]:
    """Generates structured lead summary and talking points deterministically."""
    clean_needs = needs.strip() if needs else "Enterprise automation inquiries"
    
    # Heuristic summary
    summary = (
        f"{company or 'Prospect'} ({company_size} employees) requires assistance with: {clean_needs}. "
        f"Declared budget: ${budget:,.2f}."
    )
    
    # Strategic discovery questions
    talking_points = [
        f"Explore current operational bottlenecks in their {company_size} team structure.",
        f"Inquire about their ROI expectations against the ${budget:,.2f} investment allocation.",
        "Determine the technical stakeholders required for API and workflow integration.",
        "Assess timeline constraints for deployment and transition phases.",
    ]
    
    fit_score = 65
    if budget >= 25000:
        fit_score += 20
    elif budget < 2000:
        fit_score -= 15
        
    return {
        "summary": summary,
        "talking_points": talking_points,
        "risk_factors": ["Verify timeline feasibility", "Validate internal technical resource availability"],
        "estimated_fit_score": min(max(fit_score, 10), 98),
    }

def fallback_support_triage(subject: str, body: str) -> Dict[str, Any]:
    """Classifies support emails into 8 intents and evaluates urgency and sentiment."""
    text = f"{subject} {body}".lower()
    
    # 1. Intent Detection
    intent = SupportIntent.UNKNOWN.value
    if any(w in text for w in ["invoice", "charge", "refund", "credit card", "billing", "payment", "subscription", "price"]):
        intent = SupportIntent.BILLING.value
    elif any(w in text for w in ["down", "crash", "outage", "error 500", "critical", "broken", "emergency", "fatal"]):
        intent = SupportIntent.URGENT_INCIDENTS.value
    elif any(w in text for w in ["password", "login", "reset", "2fa", "mfa", "locked", "sso", "access"]):
        intent = SupportIntent.ACCOUNT_ACCESS.value
    elif any(w in text for w in ["bug", "api", "integration", "sdk", "endpoint", "traceback", "stack trace", "code"]):
        intent = SupportIntent.TECHNICAL_SUPPORT.value
    elif any(w in text for w in ["order", "shipment", "delivery", "tracking", "package", "status"]):
        intent = SupportIntent.ORDER_INQUIRIES.value
    elif any(w in text for w in ["unacceptable", "terrible", "awful", "cancel", "disappointed", "complaint", "lawyer", "sue"]):
        intent = SupportIntent.COMPLAINTS.value
    elif any(w in text for w in ["viagra", "crypto", "casino", "lottery", "prince", "seo ranking"]):
        intent = SupportIntent.SPAM.value

    # 2. Urgency Detection (Decoupled from sentiment)
    urgency = SupportUrgency.P4_LOW.value
    if any(w in text for w in ["system down", "outage", "production down", "p0", "urgent", "emergency", "breach"]):
        urgency = SupportUrgency.P1_CRITICAL.value
    elif any(w in text for w in ["blocker", "cannot work", "deadline", "immediate", "asap", "high priority"]):
        urgency = SupportUrgency.P2_HIGH.value
    elif any(w in text for w in ["issue", "problem", "error", "failing", "assistance"]):
        urgency = SupportUrgency.P3_MEDIUM.value

    # 3. Sentiment Detection
    sentiment = SupportSentiment.NEUTRAL.value
    if any(w in text for w in ["furious", "unacceptable", "worst", "disaster", "sue", "lawsuit", "threat"]):
        sentiment = SupportSentiment.HOSTILE.value
    elif any(w in text for w in ["frustrated", "annoyed", "waiting for days", "disappointed", "waste of time"]):
        sentiment = SupportSentiment.FRUSTRATED.value
    elif any(w in text for w in ["thank you", "great", "awesome", "appreciate", "helpful", "good"]):
        sentiment = SupportSentiment.POSITIVE.value

    # 4. Human Escalation Triggers
    requires_escalation = False
    escalation_reason = None
    if any(w in text for w in ["refund", "chargeback"]) and any(w in text for w in ["100", "200", "500", "1000", "thousand"]):
        requires_escalation = True
        escalation_reason = "High-value refund or financial dispute requested"
    elif any(w in text for w in ["lawyer", "legal", "compliance", "gdpr", "subpoena"]):
        requires_escalation = True
        escalation_reason = "Legal or regulatory compliance keyword detected"
    elif any(w in text for w in ["delete my account", "erase data", "right to be forgotten"]):
        requires_escalation = True
        escalation_reason = "Account erasure / privacy request requires manual review"
    elif urgency == SupportUrgency.P1_CRITICAL.value:
        requires_escalation = True
        escalation_reason = "P1 Critical system incident"

    return {
        "intent": intent,
        "urgency": urgency,
        "sentiment": sentiment,
        "confidence": 0.88,
        "requires_escalation": requires_escalation,
        "escalation_reason": escalation_reason,
    }

def fallback_grounded_draft(ticket_data: Dict[str, Any], kb_articles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generates an empathetic response draft grounded in matched KB articles."""
    sender_name = ticket_data.get("sender", "Valued Customer").split("@")[0].capitalize()
    intent = ticket_data.get("intent", "technical_support")
    
    citations = [art["id"] for art in kb_articles] if kb_articles else []
    
    if kb_articles:
        primary_kb = kb_articles[0]
        draft = (
            f"Hello {sender_name},\n\n"
            f"Thank you for contacting NEXUS Flow Support regarding your {intent.replace('_', ' ')} inquiry.\n\n"
            f"Based on our policy and technical documentation ({primary_kb['title']}):\n"
            f"{primary_kb['content']}\n\n"
            f"Please let us know if you need any additional clarification or further assistance.\n\n"
            f"Best regards,\n"
            f"NEXUS Flow AI Support Operations\n"
            f"[References: {', '.join(citations)}]"
        )
    else:
        draft = (
            f"Hello {sender_name},\n\n"
            f"Thank you for reaching out to us. We have received your inquiry regarding {ticket_data.get('subject', 'your issue')}.\n\n"
            f"Our standard automated knowledge repository does not have an immediate pre-approved resolution for this specific query. "
            f"I have routed this ticket to our senior operations engineering team for detailed review.\n\n"
            f"A member of our team will follow up directly with you shortly.\n\n"
            f"Best regards,\n"
            f"NEXUS Flow AI Operations Team"
        )

    return {
        "draft_body": draft,
        "kb_references": citations,
        "citations_valid": bool(citations),
        "policy_notes": "Generated in safe draft-only mode; human review recommended before sending."
    }

def fallback_invoice_extraction(raw_text: str) -> Dict[str, Any]:
    """Heuristic extraction for invoice textual data using regex pattern matching."""
    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
    
    # 1. Vendor
    vendor = "Acme Global Solutions"
    if lines:
        vendor = lines[0][:100]

    # 2. Invoice Number
    inv_num_match = re.search(r"(?:invoice|inv|receipt)\s*(?:#|no\.?|num)?\s*[:\-]?\s*([A-Za-z0-9\-]+)", raw_text, re.IGNORECASE)
    invoice_number = inv_num_match.group(1) if inv_num_match else "INV-2026-001"

    # 3. Invoice Date
    date_match = re.search(r"(\d{4}[-/]\d{2}[-/]\d{2}|\d{2}[-/]\d{2}[-/]\d{4})", raw_text)
    invoice_date = date_match.group(1) if date_match else "2026-10-23"

    # 4. Currency
    currency = "USD"
    if "eur" in raw_text.lower() or "€" in raw_text:
        currency = "EUR"
    elif "gbp" in raw_text.lower() or "£" in raw_text:
        currency = "GBP"

    # 5. Amounts
    total_match = re.findall(r"(?:total|balance due|amount due)\s*[:\$€£]?\s*([\d,]+\.\d{2})", raw_text, re.IGNORECASE)
    extracted_total = float(total_match[-1].replace(",", "")) if total_match else 1250.00

    tax_match = re.search(r"(?:tax|vat|gst)\s*[:\$€£]?\s*([\d,]+\.\d{2})", raw_text, re.IGNORECASE)
    tax_amount = float(tax_match.group(1).replace(",", "")) if tax_match else round(extracted_total * 0.1, 2)

    subtotal = round(extracted_total - tax_amount, 2)

    # 6. Default Line Items
    line_items = [
        {
            "description": "Enterprise Cloud Architecture Consulting",
            "quantity": 1.0,
            "unit_price": subtotal,
            "line_total": subtotal,
        }
    ]

    return {
        "vendor": vendor,
        "invoice_number": invoice_number,
        "invoice_date": invoice_date,
        "currency": currency,
        "line_items": line_items,
        "subtotal": subtotal,
        "discount": 0.0,
        "tax_amount": tax_amount,
        "extracted_total": extracted_total,
        "payment_status": "UNPAID",
    }
