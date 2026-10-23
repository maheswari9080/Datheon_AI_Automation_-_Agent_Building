# NEXUS Flow AI — Enterprise Architecture Blueprint
> **Version 2.0.0** | Event-Driven Business Automation Architecture

---

## 1. Executive Summary

**NEXUS Flow AI** is designed as a decoupled, event-driven enterprise operations engine. The architecture adheres to clean domain boundaries, dependency inversion, and strict separation between presentation, application logic, persistence, and external service communication.

The central business lifecycle spans five interconnected phases:
```
[Customer Acquisition] ➔ [Intelligent Support] ➔ [Financial Document Processing] ➔ [Enterprise Operations] ➔ [Executive Intelligence]
```

---

## 2. High-Level System Architecture

```mermaid
graph TD
    subgraph "Clients & Ingestion Channels"
        Browser["Mission Control UI<br/>(Vanilla CSS / Responsive)"]
        CLIClient["Automation CLI Tooling"]
        Webhooks["Inbound Webhooks (Stripe / Forms)"]
        EmailFeeds["Email Feeds (Gmail / Outlook)"]
    end

    subgraph "API Gateway Layer (FastAPI)"
        Router["FastAPI Application Router"]
        CorsAudit["Audit & CORS Middleware"]
        AuthSecurity["Security & Rate Limiting"]
    end

    subgraph "Application Core & Intelligence Engines"
        LE["Lead Intelligence Engine"]
        SE["Support Intelligence Engine"]
        IE["Invoice Intelligence Engine"]
        OE["Enterprise Orchestration Engine"]
        CC["Command Center Aggregator"]
    end

    subgraph "AI & Cognition Layer"
        OpenAIWrap["OpenAI Client (Structured Outputs)"]
        Fallbacks["Deterministic Fallback Engine"]
        KBEngine["Grounded Knowledge Base (10+ Policies)"]
        Sanitizer["Prompt Injection Defense Filter"]
    end

    subgraph "External Integration Adapters"
        AirtableAdp["Airtable CRM Adapter"]
        SlackAdp["Slack Notification Adapter"]
        StripeAdp["Stripe HMAC Webhook Adapter"]
        SheetsAdp["Google Sheets / CSV Adapter"]
        EmailAdp["Email Draft Adapter"]
    end

    subgraph "Persistence Layer"
        SQLA["SQLAlchemy 2.0 ORM Engine"]
        SQLiteDB[(SQLite Local Storage)]
        PostgresDB[(PostgreSQL Enterprise Target)]
    end

    Browser & CLIClient & Webhooks & EmailFeeds --> Router
    Router --> CorsAudit --> AuthSecurity
    AuthSecurity --> LE & SE & IE & OE & CC

    LE & SE & IE & OE <--> OpenAIWrap
    OpenAIWrap -. Fallback on error .-> Fallbacks
    SE <--> KBEngine
    SE <--> Sanitizer

    LE --> AirtableAdp & SlackAdp
    SE --> EmailAdp & SlackAdp
    IE --> SheetsAdp
    OE --> StripeAdp & AirtableAdp & SlackAdp

    LE & SE & IE & OE & CC <--> SQLA
    SQLA --> SQLiteDB
    SQLA -. Migration Path .-> PostgresDB
```

---

## 3. Five Tier Architecture Layers

### Tier 1: Presentation & Telemetry Layer
- **Tech Stack**: HTML5, Vanilla CSS with custom glassmorphism design tokens, Modern JavaScript (ES6+).
- **Design Philosophy**: High-density operational mission-control inspired by aerospace and network operations centers (NOC).
- **Capabilities**:
  - Live/Demo mode toggle with visual status badges.
  - Sub-second pipeline metrics, execution latency charts, and recent audit feed.
  - Interactive approval drawers for high-consequence operations.
  - Zero external UI library bloat (100% self-contained Vanilla CSS).

### Tier 2: API & Gateway Layer
- **Tech Stack**: FastAPI async ASGI framework, Pydantic V2 data validation.
- **Responsibilities**:
  - Validates all incoming payloads before domain routing.
  - Enforces uniform API response envelopes (`ApiResponse[DataT]`).
  - Automatic OpenAPI 3.1 schema generation at `/docs`.
  - Comprehensive audit event logging for all mutative requests.

### Tier 3: Domain Intelligence Engines
Each engine operates as an independent micro-service with its own schema contracts and business rules:
1. **Lead Intelligence Engine (`nexus_flow.engines.lead`)**:
   - Ingests leads from web forms, webhooks, and CSV batch uploads.
   - Evaluates budget suitability and company size matrices.
   - Calculates dynamic scores (0–100) and priority tiers (`HIGH`, `MEDIUM`, `LOW`).
   - Generates customized sales talking points.
   - Dispatches records to Airtable CRM and notifies designated Slack channels.
   - Enforces a sub-10 second latency ceiling.

2. **Support Intelligence Engine (`nexus_flow.engines.support`)**:
   - Triage email inquiries into 8 distinct intent categories (`billing`, `technical_support`, `account_access`, `order_inquiries`, `complaints`, `urgent_incidents`, `spam`, `unknown`).
   - Decoupled sentiment and urgency evaluation.
   - Retrieves grounded context from `EnterpriseKnowledgeBase`.
   - **Architectural Invariant**: Never sends emails directly. Creates draft records with human escalation triggers.
   - Inspects body text through `sanitize_prompt_input` to block prompt injection attempts.

3. **Invoice Intelligence Engine (`nexus_flow.engines.invoice`)**:
   - Ingests PDF documents and receipts up to 20MB.
   - Extracts structured header fields (vendor, date, invoice number, currency).
   - Extracts line items (description, quantity, unit price, line total).
   - Performs rigid arithmetic reconciliation:
     $$\text{Calculated Total} = \text{Subtotal} - \text{Discount} + \text{Tax}$$
     $$\text{Variance} = |\text{Calculated Total} - \text{Extracted Total}| \le 0.01$$
   - Flags discrepancies, detects duplicate invoices, and exports approved data to Google Sheets with formula-injection sanitization.

4. **Enterprise Orchestration Engine (`nexus_flow.engines.orchestration`)**:
   - Customer onboarding with standardized project code generation (`PRJ-YYYYMM-XXXX`).
   - Contract drafting using immutable master service agreement templates (`MSA-v2.1`).
   - Stripe HMAC-SHA256 webhook signature verification.
   - Slack project collaboration channel provisioning.
   - Weekly executive intelligence digest synthesis.

5. **Command Center Aggregator (`nexus_flow.engines.command_center`)**:
   - Aggregates operational telemetry across all 4 engines.
   - Calculates system-wide latency benchmarks, approval queue states, and adapter health.

### Tier 4: AI & Heuristic Fallback Layer
- **Structured OpenAI Outputs**: Utilizes `gpt-4o` / `gpt-4o-mini` with strict JSON schema parsing.
- **Deterministic Heuristics (`fallbacks.py`)**: When OpenAI API keys are absent, rate-limited, or timed out, the system automatically falls back to regex-anchored heuristic engines:
  - Keyword intent classification with sentiment lexicon analysis.
  - Regex pattern matching for invoice amounts, dates, and line items.
  - Lead suitability scoring via mathematical decision trees.
- **Result**: Zero runtime crashes due to external AI unavailability.

### Tier 5: Persistence & Migration Layer
- **ORM**: SQLAlchemy 2.0 with unified declarative models.
- **Local Database**: SQLite (`nexus_flow.db`) with foreign key constraints, indexing, and connection pooling.
- **PostgreSQL Enterprise Target**: Ready for direct cutover by changing the connection string to `postgresql+psycopg2://user:password@host:5432/dbname`.

---

## 4. Entity Relationship Model (ERD)

```mermaid
erDiagram
    LEAD_RECORDS {
        string id PK
        string email
        string full_name
        string company
        float budget
        string company_size
        int score
        string priority
        string status
        string airtable_record_id
        boolean slack_notified
        float latency_seconds
        datetime created_at
    }

    SUPPORT_TICKETS {
        string id PK
        string message_id
        string sender
        string subject
        text sanitized_body
        string intent
        string urgency
        string sentiment
        float confidence
        text draft_response
        boolean is_draft
        boolean prompt_injection_flag
        boolean requires_escalation
        string escalation_reason
        datetime created_at
    }

    INVOICE_RECORDS {
        string id PK
        string filename
        string vendor
        string invoice_number
        string invoice_date
        string currency
        float subtotal
        float discount
        float tax_amount
        float calculated_total
        float extracted_total
        boolean is_arithmetic_valid
        boolean duplicate_flag
        string status
        string payment_status
        int google_sheets_row
        datetime created_at
    }

    LINE_ITEMS {
        string id PK
        string invoice_id FK
        string description
        float quantity
        float unit_price
        float line_total
    }

    PROJECT_RECORDS {
        string id PK
        string project_code UK
        string client_name
        string client_email
        string service_tier
        string status
        string contract_status
        string payment_status
        string slack_channel
        string airtable_record_id
        datetime created_at
    }

    CONTRACT_RECORDS {
        string id PK
        string project_id FK
        string template_version
        text contract_text
        string approval_status
        string approved_by
        datetime approved_at
        datetime created_at
    }

    PAYMENT_LEDGER {
        string id PK
        string event_id UK
        string project_id FK
        string stripe_customer_id
        float amount
        string currency
        string payment_status
        boolean signature_verified
        string idempotency_key
        datetime created_at
    }

    APPROVAL_REQUESTS {
        string id PK
        string entity_type
        string entity_id
        string requested_action
        string status
        string requested_by
        string approved_by
        datetime created_at
    }

    AUDIT_EVENTS {
        string id PK
        string event_type
        string action
        string status
        string entity_id
        float duration_ms
        text details_json
        datetime created_at
    }

    INVOICE_RECORDS ||--o{ LINE_ITEMS : "contains"
    PROJECT_RECORDS ||--o{ CONTRACT_RECORDS : "governs"
    PROJECT_RECORDS ||--o{ PAYMENT_LEDGER : "settles"
```

---

## 5. External Integration Boundaries

All third-party services connect exclusively through the `BaseAdapter` interface:

| Service | Adapter Class | Live Protocol | Mock Behavior |
| :--- | :--- | :--- | :--- |
| **Airtable** | `AirtableAdapter` | REST API (Bearer Token) | In-memory simulated record store with synthetic IDs (`rec_...`). |
| **Slack** | `SlackAdapter` | Incoming Webhooks / Web API | Logs structured message payloads to standard output and returns success. |
| **Stripe** | `StripeAdapter` | HMAC-SHA256 Webhook Verification | Validates `t=...,v1=...` signatures; supports test signing secret `whsec_test_secret_nexus_2026`. |
| **Google Sheets**| `GoogleSheetsAdapter`| Google Drive & Sheets API V4 | Exports to local `exports/google_sheets_mock.csv` with formula sanitization. |
| **Gmail / Outlook**| `EmailAdapter` | SMTP/IMAP & Microsoft Graph API | Stores simulated drafts in local ledger with enforced draft-only mode. |

---

## 6. PostgreSQL Enterprise Migration Path

When transitioning from SQLite to PostgreSQL in production environments:
1. Update `.env`:
   ```bash
   DATABASE_URL=postgresql+psycopg2://nexus_admin:SecurePass2026@pg-cluster.internal:5432/nexus_flow_production
   ```
2. Install the PostgreSQL binary driver:
   ```bash
   pip install psycopg2-binary
   ```
3. Run Alembic or SQLite-to-PostgreSQL schema migration:
   ```bash
   python scripts/automation_cli.py db-migrate --target postgresql
   ```
4. All models use ANSI-compliant types (`String`, `Float`, `Boolean`, `DateTime`, `Text`, `JSON`), ensuring 100% schema parity without table alterations.
