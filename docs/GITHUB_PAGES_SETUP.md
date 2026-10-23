# NEXUS Flow AI — GitHub Pages Hosting & Deployment Manual
> **Live Web Application Hosting Guide** | Automated GitHub Actions & Branch Deployment

---

## 🌐 Live Web URL
Once enabled, your full Mission Control Command Center web interface is accessible at:

**`https://maheswari9080.github.io/Datheon_AI_Automation_-_Agent_Building/`**

---

## 🚀 How to Enable GitHub Pages (1-Minute Setup)

Follow these exact steps in your GitHub repository:

### Step 1: Open GitHub Repository Settings
1. Navigate to your repository: [github.com/maheswari9080/Datheon_AI_Automation_-_Agent_Building](https://github.com/maheswari9080/Datheon_AI_Automation_-_Agent_Building)
2. Click the **Settings** tab in the top navigation bar.
3. In the left-hand sidebar under **Code and automation**, click **Pages** (or go directly to `https://github.com/maheswari9080/Datheon_AI_Automation_-_Agent_Building/settings/pages`).

---

### Step 2: Select Your Publishing Source

You have **two fully supported deployment options**:

#### Option A: GitHub Actions (Recommended — Fully Automated CI/CD)
1. Under **Build and deployment**, locate the **Source** dropdown.
2. Select **`GitHub Actions`**.
3. That's it! The pre-configured `.github/workflows/deploy-pages.yml` workflow will automatically:
   - Run the 27-test automated verification suite.
   - Assemble the static distribution (HTML, CSS, JS, visual assets, docs, and 404 SPA fallback).
   - Deploy directly to GitHub Pages.
4. To trigger immediately: Go to the **Actions** tab ➔ Click **Deploy NEXUS Flow AI to GitHub Pages** in the left menu ➔ Click **Run workflow** ➔ Select branch `main` ➔ Click **Run workflow**.

---

#### Option B: Deploy from a Branch (`gh-pages`)
If you prefer branch-based hosting without workflow runners:
1. Under **Build and deployment**, locate the **Source** dropdown.
2. Select **`Deploy from a branch`**.
3. Under **Branch**:
   - Select **`gh-pages`** from the branch dropdown.
   - Select **`/ (root)`** from the folder dropdown.
4. Click **Save**.
5. GitHub Pages will begin building and publishing your site immediately (typically live within 30–60 seconds).

---

## ⚡ What is Deployed on GitHub Pages?

GitHub Pages hosts the complete **Mission Control Command Center** web application:

| Feature / Engine | Behavior on GitHub Pages |
| :--- | :--- |
| **Command Center** | Live telemetry KPIs, real-time latency tracker, recent audit stream, and mode status badge (`GITHUB PAGES (CLIENT DEMO)`). |
| **Lead Intelligence** | Interactive lead qualification form, dynamic 0–100 scoring, AI sales talking points, and pipeline filters. |
| **Support Intelligence** | Email triage simulator, 8-way intent categorization, grounded KB draft generator, and prompt-injection defense check. |
| **Invoice Intelligence** | PDF file audit, line-item calculator, strict $\pm \$0.01$ arithmetic verification, and Google Sheets export simulator. |
| **Enterprise Orchestration** | Customer intake, `PRJ-YYYYMM-XXXX` project generator, MSA contract review, Stripe payment simulator, and Weekly Executive Digest. |
| **Approval Center** | Interactive Human-in-the-Loop approval drawer to approve or reject escalated tickets and contracts. |
| **Visual Assets** | Ultra-crisp light-theme graphics, architecture infographics, and vector cards. |

---

## 🔄 Dual-Mode Architecture

The web interface controller in `nexus_flow/static/js/app.js` is engineered with automatic environment detection:

1. **Static / GitHub Pages Mode**:
   - Detects `*.github.io` domain or static hosting.
   - Seamlessly routes all API calls to the built-in client-side reactive simulation engine.
   - Pre-seeds realistic enterprise data and persists changes across browser sessions via `localStorage`.
   - **Zero 404 errors, zero broken buttons, zero external backend requirement**.

2. **Full-Stack / FastAPI Mode**:
   - When run locally via `python -m nexus_flow.main` or on a cloud container, connects to live FastAPI REST endpoints (`/api/v1/...`) and SQLAlchemy 2.0 SQLite/PostgreSQL persistence.

---

## 🛠️ Local Static Testing
To test the exact static bundle locally before pushing:

```bash
# 1. Build the static distribution
python scripts/build_pages.py

# 2. Serve with any static web server
python -m http.server 8080 --directory _site
```
Then visit `http://127.0.0.1:8080` in your browser.
