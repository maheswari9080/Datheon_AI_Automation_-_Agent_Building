# NEXUS Flow AI — Integration Setup & Configuration
> **Version 2.0.0** | Provisioning External Services & Adapter Configuration

---

## 1. Overview of the Adapter Pattern

NEXUS Flow AI uses an enterprise Adapter Pattern that separates external vendor APIs from internal business logic. Every external integration supports two distinct modes:

- **`demo` mode (default)**: Simulates API calls locally, records operations in audit tables, and returns synthetic verified payloads. Zero external API keys or cloud subscriptions are required.
- **`live` mode**: Connects to production REST endpoints over TLS with authentication tokens, rate-limit retries, and error isolation.

To switch between modes, toggle `APP_MODE=demo` or `APP_MODE=live` in `.env`.

---

## 2. Service-by-Service Integration Guides

### 1. Airtable CRM Integration

#### Purpose
Used by the **Lead Intelligence Engine** and **Enterprise Orchestration Engine** to persist customer records, pipeline status, and project milestones.

#### Credentials Required
- `AIRTABLE_API_KEY`: Personal Access Token (PAT) with `data.records:read` and `data.records:write` scopes.
- `AIRTABLE_BASE_ID`: Target base identifier (starts with `app...`).
- `AIRTABLE_LEADS_TABLE`: Table name (defaults to `Leads`).
- `AIRTABLE_PROJECTS_TABLE`: Table name (defaults to `Projects`).

#### Table Schema Mapping
| Airtable Field | Type | Internal Model Equivalent |
| :--- | :--- | :--- |
| `Full Name` | Single line text | `Lead.full_name` |
| `Email` | Email | `Lead.email` |
| `Company` | Single line text | `Lead.company` |
| `Budget` | Currency (USD) | `Lead.budget` |
| `Score` | Number (Integer) | `Lead.score` |
| `Priority` | Single select | `Lead.priority` |
| `Talking Points` | Long text | `Lead.talking_points` |
| `Status` | Single select | `Lead.status` |

#### Mock Mode Behavior
When `APP_MODE=demo`, the adapter generates simulated Airtable IDs (`rec_demo_...`) and stores records in an in-memory dictionary.

---

### 2. Slack Enterprise Collaboration

#### Purpose
Used for real-time sales alerts, support escalations, and automated project channel collaboration.

#### Credentials Required
- `SLACK_WEBHOOK_URL`: Incoming Webhook URL (e.g., `https://hooks.slack.com/services/T00/B00/XXXX`).
- `SLACK_BOT_TOKEN`: Bot User OAuth Token (`xoxb-...`) with `channels:manage`, `chat:write`, `groups:write` scopes.

#### Channel Routing Rules
- **Sales Alerts**: Posted to `#leads-pipeline` or `#sales-urgent`.
- **Support Escalations**: Dispatched to `#support-escalations` when `requires_escalation=True`.
- **Project Provisioning**: Dynamically creates channels using the naming format:  
  `#proj-<project_code_lowercase>` (e.g., `#proj-prj-202610-1042`).

#### Mock Mode Behavior
In demo mode, alerts are rendered in the console log and the Command Center's recent events feed.

---

### 3. Stripe Payment Verification & Webhooks

#### Purpose
Authorizes project initiation only after verified invoice or retainer settlement.

#### Credentials Required
- `STRIPE_API_KEY`: Secret key (`sk_live_...` or `sk_test_...`).
- `STRIPE_WEBHOOK_SECRET`: Signing secret (`whsec_...`).

#### Cryptographic Signature Verification
Incoming webhooks from Stripe include a `Stripe-Signature` header in the format:
```
t=1729668000,v1=9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08
```

The adapter verifies this signature using HMAC-SHA256:
```python
expected_sig = hmac.new(
    secret.encode("utf-8"),
    f"{timestamp}.{raw_payload}".encode("utf-8"),
    hashlib.sha256
).hexdigest()
```
- Replays older than 300 seconds are rejected.
- Invalid signatures trigger an HTTP 400 with security audit alerts.

#### Testing with Stripe CLI
```bash
stripe listen --forward-to localhost:8000/api/v1/orchestration/stripe-webhook
```

---

### 4. Google Sheets Accounting Export

#### Purpose
Exports approved invoices from the **Invoice Intelligence Engine** to cloud accounting spreadsheets.

#### Credentials Required
- `GOOGLE_SHEETS_CREDENTIALS`: Path to Google Cloud Service Account JSON file (`credentials.json`).
- `GOOGLE_SHEETS_SPREADSHEET_ID`: 44-character target spreadsheet identifier.

#### OWASP Formula Injection Defense
Any field starting with `=, +, -, @, \t, \r` is prefixed with an apostrophe (`'`) to neutralize remote code execution and formula evaluation in spreadsheet software:
```python
def sanitize_cell_value(val: str) -> str:
    if val and str(val).startswith(("=", "+", "-", "@", "\t", "\r")):
        return f"'{val}"
    return str(val)
```

#### CSV Fallback Mode
When Google Cloud credentials are not configured, exports are written to:
`exports/google_sheets_mock.csv`.

---

### 5. Gmail / Outlook Draft Service

#### Purpose
Manages support ticket draft responses for human agent review.

#### Credentials Required
- `EMAIL_PROVIDER`: `gmail` or `outlook`.
- `GMAIL_CREDENTIALS_PATH`: Path to OAuth2 client credentials.
- `OUTLOOK_CLIENT_ID` / `OUTLOOK_TENANT_ID`: Azure App registration credentials.

#### Draft-Only Architectural Rule
> [!IMPORTANT]
> NEXUS Flow AI is architecturally restricted from sending automated outbound emails. All generated responses are saved with `is_draft=True` to require explicit human review before transmission.

---

### 6. OpenAI Cognitive Services

#### Purpose
Empowers lead summarization, 8-way support classification, and structured invoice parsing.

#### Credentials Required
- `OPENAI_API_KEY`: API key (`sk-...`).
- `OPENAI_MODEL`: `gpt-4o` (default) or `gpt-4o-mini`.

#### Deterministic Fallbacks
If the API key is not supplied, the platform automatically activates deterministic heuristic engines in `nexus_flow.ai.fallbacks`:
- Keyword and sentiment classification for support tickets.
- Regex extraction for invoice totals, tax, and line items.
- Mathematical decision scoring for leads.
