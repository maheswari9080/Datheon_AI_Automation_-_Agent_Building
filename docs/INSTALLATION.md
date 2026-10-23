# NEXUS Flow AI — Installation & Deployment Guide
> **Version 2.0.0** | Comprehensive Setup Manual for Windows, Linux & macOS

---

## 1. System Requirements

### Minimum Hardware
- **CPU**: 2 Cores (4 Cores recommended for high-concurrency PDF OCR parsing)
- **RAM**: 4 GB (8 GB recommended)
- **Disk Space**: 500 MB free space

### Software Prerequisites
- **Python**: 3.11 or 3.12 (Python 3.12.x tested and certified)
- **Package Manager**: `pip` (v23.0+)
- **Git**: 2.30+
- **Browser**: Modern Chromium, Firefox, or Safari for the Mission Control UI

---

## 2. Step-by-Step Installation

### Step 1: Clone Repository
```bash
# Clone over SSH or HTTPS
git clone git@github.com:maheswari9080/Datheon_AI_Automation_-_Agent_Building.git
cd Datheon_AI_Automation_-_Agent_Building
```

### Step 2: Create and Activate Virtual Environment

#### On Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(If PowerShell restricts script execution, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

#### On Linux / macOS (Bash/Zsh):
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Verify installed packages:
```bash
pip list
```

---

## 3. Configuration & Environment Setup

Copy the sample environment file to create your active `.env`:
```bash
cp .env.example .env
```

### Key Configuration Parameters

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `APP_MODE` | `demo` | Set to `demo` to run without API keys, or `live` for live external services. |
| `DATABASE_URL` | `sqlite:///nexus_flow.db` | Local SQLite database path or PostgreSQL connection URI. |
| `OPENAI_API_KEY` | *(empty)* | OpenAI key for LLM-based categorization and extraction. |
| `STRIPE_WEBHOOK_SECRET` | `whsec_test_secret_nexus_2026` | Secret used to verify Stripe HMAC signatures. |
| `AIRTABLE_API_KEY` | *(empty)* | Airtable personal access token. |
| `SLACK_WEBHOOK_URL` | *(empty)* | Incoming Slack webhook URL for notifications. |
| `GOOGLE_SHEETS_CREDENTIALS` | *(empty)* | Path to Google Service Account JSON file. |

---

## 4. Database Initialization

NEXUS Flow AI automatically initializes all required tables and relationships on initial startup. To explicitly run or verify database migrations:

```bash
# Verify SQLite table creation via Python
python -c "from nexus_flow.core.database import init_db; init_db(); print('Database tables verified successfully.')"
```

To populate the database with realistic demonstration records:
```bash
python scripts/automation_cli.py seed-demo
```

---

## 5. Verification Commands

### A. Run Automated Unit & Integration Tests
```bash
python -m pytest -v
```
**Expected Output**:
```
============================= test session starts =============================
collected 27 items

tests/test_adapters.py::test_airtable_adapter_mock PASSED                [  3%]
tests/test_adapters.py::test_slack_adapter_mock PASSED                   [  7%]
...
tests/test_support_engine.py::test_draft_only_enforcement PASSED         [100%]
============================= 27 passed in 2.23s ==============================
```

### B. Launch the Web Server & Mission Control Interface
```bash
python -m nexus_flow.main
```
The server will bind to `http://127.0.0.1:8000`:
- **Mission Control UI**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **API Documentation (Swagger UI)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Telemetry**: [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)

### C. Verify CLI Automation Tooling
```bash
python scripts/automation_cli.py --help
```

---

## 6. Docker Deployment (Optional)

To run NEXUS Flow AI as a self-contained container:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "-m", "nexus_flow.main"]
```

Build and execute:
```bash
docker build -t nexus-flow-ai:2.0 .
docker run -d -p 8000:8000 --name nexus_flow nexus-flow-ai:2.0
```

---

## 7. Troubleshooting

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| `Port 8000 already in use` | Another process is occupying the default port. | Run `uvicorn nexus_flow.main:app --port 8080` or kill the conflicting PID. |
| `Pydantic ValidationError` | Missing required payload field. | Check payload against OpenAPI schema at `/docs`. |
| `Stripe Signature Verification Failed` | Webhook signature mismatch. | Ensure `STRIPE_WEBHOOK_SECRET` in `.env` matches the Stripe signing secret. |
| `Permission denied (publickey)` | SSH key not attached to GitHub agent. | Ensure SSH agent is loaded or run `ssh -i ~/.ssh/id_ed25519_maheswari -T git@github.com`. |
