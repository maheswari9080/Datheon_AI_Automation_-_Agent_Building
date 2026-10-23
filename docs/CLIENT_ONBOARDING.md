# NEXUS Flow AI — Enterprise Client Onboarding Guide
> **Version 2.0.0** | Implementation Playbook for Enterprise Deployments

---

## 1. Onboarding Framework Overview

The **NEXUS Flow AI** client onboarding process is structured into five sequential phases to ensure seamless enterprise adoption, data governance, and risk mitigation:

```
Phase 1: Environment Provisioning ➔ Phase 2: Knowledge & Rule Ingestion ➔ Phase 3: Integration Wireup ➔ Phase 4: Staging Pilot ➔ Phase 5: Production Cutover
```

---

## 2. Phased Implementation Roadmap

### Phase 1: Environment Provisioning & Access Control (Week 1)
1. **Infrastructure Selection**:
   - Evaluate hosting target: On-Premises Docker container, AWS ECS/EKS, or Azure Container Instances.
   - Provision production PostgreSQL database instance.
2. **Repository & Secrets Configuration**:
   - Clone repository and populate `.env` using enterprise secret managers (HashiCorp Vault, AWS Secrets Manager, or Azure Key Vault).
   - Set up dedicated least-privilege IAM credentials for all cloud resources.
3. **Identity & Role-Based Access Control**:
   - Establish roles: `Executive Reviewer`, `Support Lead`, `Finance Manager`, `Operations Engineer`.

---

### Phase 2: Knowledge Base & Business Rules Ingestion (Week 2)
1. **Enterprise Knowledge Ingestion**:
   - Populate `nexus_flow/ai/knowledge_base.py` with client-specific corporate policies:
     - SLA response tiers (e.g., 1-hour response for Tier-1 incidents).
     - Standard refund policies and escalation thresholds.
     - Acceptable payment terms (Net 15 vs Net 30).
2. **Contract Template Customization**:
   - Review and customize the Master Service Agreement template (`MSA-v2.1`) in `nexus_flow/engines/orchestration/service.py`.
   - Lock down immutable legal clauses to prevent dynamic LLM modifications.
3. **Lead Suitability Calibration**:
   - Configure minimum budget thresholds (default: $10,000) and company size qualification scoring matrix in `nexus_flow/engines/lead/service.py`.

---

### Phase 3: Integration Wireup & Webhook Configuration (Week 3)
1. **Airtable CRM**:
   - Create client Airtable base using the provided schema template.
   - Configure `AIRTABLE_API_KEY`, `AIRTABLE_BASE_ID`, and table mapping in `.env`.
2. **Slack Enterprise Grid**:
   - Install the NEXUS Flow AI bot application to client workspace.
   - Create channels: `#leads-pipeline`, `#support-escalations`, `#finance-approvals`.
3. **Stripe Payment Gateway**:
   - Configure webhook endpoint in the Stripe Dashboard pointing to:  
     `https://<client-nexus-domain>/api/v1/orchestration/stripe-webhook`.
   - Subscribe to events: `payment_intent.succeeded`, `charge.refunded`.
   - Copy signing secret (`whsec_...`) to `STRIPE_WEBHOOK_SECRET`.
4. **Google Sheets / Accounting**:
   - Share accounting workbook with the Google Cloud Service Account email.
   - Verify formula injection escaping rules.

---

### Phase 4: Staging Pilot & Acceptance Testing (Week 4)
1. **Run Synthetic Test Suite**:
   ```bash
   python -m pytest -v
   ```
2. **Execute Repeatable Demo Scenarios**:
   - Follow the 10-step walkthrough in [docs/DEMO_SCENARIOS.md](DEMO_SCENARIOS.md).
   - Simulate payment callbacks using the Stripe CLI:
     ```bash
     stripe trigger payment_intent.succeeded
     ```
3. **SLA & Latency Audit**:
   - Verify that lead processing completes under 10 seconds.
   - Validate prompt injection defenses against simulated red-team inquiries.

---

### Phase 5: Production Cutover & Operational Governance (Go-Live)
1. **Switch Mode**: Set `APP_MODE=live` in production `.env`.
2. **Database Migration**: Ensure PostgreSQL schema is up to date:
   ```bash
   python scripts/automation_cli.py db-migrate --target postgresql
   ```
3. **Active Monitoring**:
   - Integrate `/api/v1/health` with enterprise monitoring tools (Datadog, Prometheus, New Relic).
   - Set up alerts for any unprocessed records in the `ApprovalRequest` queue exceeding 4 hours.

---

## 3. Escalation & Support Runbook

| Incident Type | First Responder | Escalation Trigger | Remediation Action |
| :--- | :--- | :--- | :--- |
| **Prompt Injection Attempt** | Support Lead | `prompt_injection_flag = True` | Review sanitized body; confirm attacker IP; block sender. |
| **Invoice Arithmetic Discrepancy** | Accounts Payable Lead | `is_arithmetic_valid = False` | Cross-examine PDF line items against extracted totals; reject or override. |
| **Stripe Signature Failure** | Security Engineer | HTTP 400 on webhook listener | Verify webhook signing secret; inspect network logs for unauthorized IP sources. |
| **High Latency (>10s on Leads)** | DevOps / SRE | Latency gauge in Command Center | Check OpenAI API status; ensure deterministic fallback engine is operating. |
