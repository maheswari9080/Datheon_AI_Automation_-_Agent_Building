# NEXUS Flow AI — Automation Layer & Visual Workflows

This directory contains production-ready, validated workflow definitions for visual cloud orchestration via **n8n** and **Make.com**.

---

## 1. n8n Workflow (`workflows/n8n/nexus_flow_hub.json`)

### Workflow Architecture
```
[Inbound Lead Webhook]
        │
        ▼
[Validate & Score Lead] (JavaScript Code Node)
        │
        ▼
[Consent Verification Filter] (If Node)
    ├── TRUE  ──► [NEXUS Flow API Client] ──► [Respond to Webhook]
    └── FALSE ──► [Disqualification Logger] ──► [Audit Dead-Letter Sink]
```

### Node Specifications
1. **Inbound Lead Webhook (`node-lead-webhook`)**:
   - **Method**: `POST`
   - **Path**: `/webhook/nexus-inbound-lead`
   - **Authentication**: Bearer Token or Webhook Signature
2. **Validate & Score Lead (`node-lead-validation`)**:
   - Normalizes email, cleans company strings, enforces numeric budget coercion.
   - Computes initial rule-based heuristic score ($0–40 budget, $0–30 company tier).
3. **Consent Verification Filter (`node-consent-filter`)**:
   - Evaluates boolean `consent === true`.
   - Branch False routes directly to the Disqualification Logger without alerting sales.
4. **NEXUS Flow Lead Ingest API (`node-api-post-lead`)**:
   - **URL**: `http://127.0.0.1:8000/api/v1/leads`
   - Triggers server-side AI talking points, Airtable sync, and Slack channel alert.
5. **Error Route & Dead-Letter Handling (`node-error-disqualified`)**:
   - Captures malformed payloads and non-consenting leads into an audit event log.

---

## 2. Make.com Blueprint (`workflows/make/nexus_flow_blueprint.json`)

### Scenario Modules
1. **Custom Webhook (`gateway:CustomWebHook`)**: Ingests form submissions from Typeform, Webflow, or HubSpot.
2. **JSON Parser (`json:ParseJSON`)**: Enforces typed schema validation.
3. **OpenAI Chat Completion (`openai:createChatCompletion`)**: Extracts business requirements and drafts talking points.
4. **Airtable Create Record (`airtable:createRecord`)**: Persists lead attributes into the Leads base.
5. **Slack Create Message (`slack:createMessage`)**: Posts rich mrkdwn alerts to `#sales-leads`.

---

## 3. How to Import
- **In n8n**: Open your n8n workspace → **Workflows** → **Import from File** → Select `nexus_flow_hub.json`.
- **In Make.com**: Open your Make organization → **Scenarios** → **Create a new scenario** → **Import Blueprint** → Select `nexus_flow_blueprint.json`.
