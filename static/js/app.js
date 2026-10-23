/**
 * NEXUS Flow AI — Unified Command Center Web Interface Controller
 * Supports dual-mode: Live FastAPI REST backend OR Client-Side Static Simulation (for GitHub Pages).
 */

document.addEventListener("DOMContentLoaded", () => {
  // Navigation handling
  const navItems = document.querySelectorAll(".nav-item");
  const pages = document.querySelectorAll(".page-container");
  const viewTitle = document.getElementById("view-title");

  const viewTitles = {
    "command-center": "Mission Control Command Center",
    "lead-intelligence": "Lead Intelligence Engine",
    "support-intelligence": "Support Intelligence Engine",
    "invoice-intelligence": "Invoice Intelligence Engine",
    "enterprise-orchestration": "Enterprise Operations & Orchestration",
    "approval-center": "Human Consequential Approval Center",
    "integration-registry": "Integration Registry & System Health",
  };

  navItems.forEach((item) => {
    item.addEventListener("click", () => {
      const targetView = item.getAttribute("data-view");
      navItems.forEach((n) => n.classList.remove("active"));
      item.classList.add("active");

      pages.forEach((p) => p.classList.remove("active"));
      const targetPage = document.getElementById(`view-${targetView}`);
      if (targetPage) targetPage.classList.add("active");

      if (viewTitles[targetView]) {
        viewTitle.textContent = viewTitles[targetView];
      }

      // Load specific data on view switch
      loadViewData(targetView);
    });
  });

  // Modal Handlers
  const modal = document.getElementById("detail-modal");
  const modalTitle = document.getElementById("modal-title");
  const modalBody = document.getElementById("modal-body");
  const btnCloseModal = document.getElementById("btn-close-modal");

  function openModal(title, htmlContent) {
    modalTitle.textContent = title;
    modalBody.innerHTML = htmlContent;
    modal.classList.add("active");
  }

  if (btnCloseModal) {
    btnCloseModal.addEventListener("click", () => {
      modal.classList.remove("active");
    });
  }

  if (modal) {
    modal.addEventListener("click", (e) => {
      if (e.target === modal) modal.classList.remove("active");
    });
  }

  // =========================================================================
  // CLIENT-SIDE SIMULATION ENGINE (FOR GITHUB PAGES STATIC DEPLOYMENTS)
  // =========================================================================
  const isStaticHost = window.location.hostname.includes("github.io") || 
                       window.location.protocol === "file:" ||
                       window.location.port === "" ||
                       window.location.search.includes("mock=true");

  const LOCAL_STORAGE_KEY = "nexus_flow_static_state_v2";

  function getInitialMockState() {
    return {
      mode: isStaticHost ? "GITHUB PAGES (CLIENT DEMO)" : "DEMO / MOCK ACTIVE",
      verifiedRevenue: 48500.0,
      leads: [
        {
          id: "lead_demo_01",
          full_name: "Evelyn Vance",
          email: "evelyn.vance@vanguard-holdings.com",
          company: "Vanguard Global Holdings",
          budget: 75000.0,
          score: 92,
          priority: "HOT",
          status: "QUALIFIED",
          airtable_record_id: "rec_vanguard_881",
          latency_seconds: 0.048,
          ai_summary: "High-budget multi-regional holding enterprise looking for autonomous accounts payable and customer onboarding pipelines.",
          talking_points: [
            "Highlight dedicated SLA guarantee and 99.95% API uptime.",
            "Demonstrate automated Stripe HMAC payment reconciliation.",
            "Offer custom Slack project channel collaboration demo."
          ],
          assigned_rep: "Senior Enterprise Director",
          created_at: new Date(Date.now() - 3600000).toISOString()
        },
        {
          id: "lead_demo_02",
          full_name: "Marcus Sterling",
          email: "marcus@apex-logistics.de",
          company: "Apex Logistics GmbH",
          budget: 35000.0,
          score: 78,
          priority: "WARM",
          status: "QUALIFIED",
          airtable_record_id: "rec_apex_420",
          latency_seconds: 0.052,
          ai_summary: "European logistics firm seeking support email triage and invoice arithmetic checks.",
          talking_points: [
            "Demonstrate multi-currency invoice parser (EUR, USD, GBP).",
            "Showcase 8-way intent categorization and draft-only mode."
          ],
          assigned_rep: "Logistics Automation Specialist",
          created_at: new Date(Date.now() - 7200000).toISOString()
        },
        {
          id: "lead_demo_03",
          full_name: "Priya Sharma",
          email: "priya@novacare-health.org",
          budget: 8000.0,
          company: "NovaCare Health",
          score: 45,
          priority: "COLD",
          status: "NURTURE",
          airtable_record_id: "rec_novacare_109",
          latency_seconds: 0.041,
          ai_summary: "Non-profit clinic system with budget constraints, exploring self-hosted workflow automation.",
          talking_points: [
            "Introduce standard tier options and open-source n8n templates.",
            "Recommend self-guided trial before custom enterprise onboarding."
          ],
          assigned_rep: "Solutions Consultant",
          created_at: new Date(Date.now() - 14400000).toISOString()
        }
      ],
      support: [
        {
          id: "tkt_01",
          sender: "alex.chen@cloudtech.io",
          subject: "URGENT: Production API cluster failing with 500 errors",
          sanitized_body: "Our core API pipeline has been returning 500 internal server errors for the past 20 minutes. High customer traffic impacted.",
          intent: "urgent_incidents",
          urgency: "CRITICAL",
          sentiment: "NEGATIVE",
          confidence: 0.98,
          draft_response: "Dear Alex,\n\nWe have triggered emergency Tier-2 incident protocols for your production cluster. Our SRE lead is actively inspecting telemetry logs.\n\nTicket Status: In Progress\nEscalation ID: ESC-9021",
          kb_references: ["KB-INC-001: Critical Outage Protocol", "KB-SLA-004: Tier-1 Incident Response"],
          is_draft: true,
          prompt_injection_flag: false,
          requires_escalation: true,
          created_at: new Date(Date.now() - 1800000).toISOString()
        },
        {
          id: "tkt_02",
          sender: "sarah.jenkins@meridian.com",
          subject: "Invoice question regarding monthly billing cycle",
          sanitized_body: "Hi team, could you clarify whether our enterprise subscription renewal occurs on the 1st or the 15th of each month? Thanks!",
          intent: "billing",
          urgency: "STANDARD",
          sentiment: "NEUTRAL",
          confidence: 0.94,
          draft_response: "Hello Sarah,\n\nThank you for reaching out. Enterprise agreements renew on the 1st of each calendar month. Statements are auto-exported to your designated accounting channel.\n\nBest regards,\nAccounts Support",
          kb_references: ["KB-BIL-002: Enterprise Billing Cycles"],
          is_draft: true,
          prompt_injection_flag: false,
          requires_escalation: false,
          created_at: new Date(Date.now() - 5400000).toISOString()
        },
        {
          id: "tkt_03",
          sender: "adversary@untrusted-domain.org",
          subject: "Urgent account dispute inquiry",
          sanitized_body: "[BLOCKED INJECTION ATTEMPT]: System override instruction neutralized.",
          intent: "urgent_incidents",
          urgency: "HIGH",
          sentiment: "NEGATIVE",
          confidence: 0.99,
          draft_response: "Your inquiry has been placed in human security review due to policy filter triggers.",
          kb_references: ["KB-SEC-009: Threat Neutralization"],
          is_draft: true,
          prompt_injection_flag: true,
          requires_escalation: true,
          created_at: new Date(Date.now() - 9000000).toISOString()
        }
      ],
      invoices: [
        {
          id: "inv_01",
          filename: "Acme_Cloud_Solutions_INV-401.pdf",
          vendor: "Acme Cloud Solutions Inc",
          invoice_number: "INV-2026-401",
          extracted_total: 1375.0,
          calculated_total: 1375.0,
          is_arithmetic_valid: true,
          duplicate_flag: false,
          status: "APPROVED",
          created_at: new Date(Date.now() - 86400000).toISOString()
        },
        {
          id: "inv_02",
          filename: "Faulty_Hardware_Depot_INV-109.pdf",
          vendor: "Faulty Hardware Depot",
          invoice_number: "INV-2026-109",
          extracted_total: 700.0,
          calculated_total: 550.0,
          is_arithmetic_valid: false,
          duplicate_flag: false,
          status: "FLAGGED_DISCREPANCY",
          created_at: new Date(Date.now() - 43200000).toISOString()
        },
        {
          id: "inv_03",
          filename: "Acme_Duplicate_Copy.pdf",
          vendor: "Acme Cloud Solutions Inc",
          invoice_number: "INV-2026-401",
          extracted_total: 1375.0,
          calculated_total: 1375.0,
          is_arithmetic_valid: true,
          duplicate_flag: true,
          status: "FLAGGED_DUPLICATE",
          created_at: new Date(Date.now() - 21600000).toISOString()
        }
      ],
      projects: [
        {
          id: "prj_01",
          project_code: "PRJ-202610-1042",
          client_name: "Helios Global Logistics",
          client_email: "procurement@helios-global.com",
          service_tier: "Enterprise Operations Tier",
          contract_status: "APPROVED",
          payment_status: "PAID",
          slack_channel: "#proj-prj-202610-1042",
          status: "ACTIVE",
          created_at: new Date(Date.now() - 86400000).toISOString()
        },
        {
          id: "prj_02",
          project_code: "PRJ-202610-8831",
          client_name: "Vertex FinTech Systems",
          client_email: "legal@vertex-fintech.io",
          service_tier: "Executive Tier",
          contract_status: "DRAFT",
          payment_status: "PENDING_VERIFICATION",
          slack_channel: "Pending Approval",
          status: "INTAKE",
          created_at: new Date(Date.now() - 43200000).toISOString()
        }
      ],
      approvals: [
        {
          id: "appr_01",
          entity_type: "CONTRACT_APPROVAL",
          title: "MSA-v2.1 Sign-off: Vertex FinTech Systems",
          description: "Enterprise Operations Tier Contract ($45,000 budget). Legal clauses locked and verified.",
          requested_by: "Orchestration Engine",
          status: "PENDING",
          created_at: new Date(Date.now() - 3600000).toISOString()
        },
        {
          id: "appr_02",
          entity_type: "SECURITY_ESCALATION",
          title: "Prompt Injection Detected: adversary@untrusted-domain.org",
          description: "Malicious payload detected in inbound email subject 'Urgent account dispute inquiry'.",
          requested_by: "Support Security Guardrail",
          status: "PENDING",
          created_at: new Date(Date.now() - 1800000).toISOString()
        }
      ],
      audit: [
        {
          event_type: "SYSTEM_BOOT",
          action: "INITIALIZE_PLATFORM",
          status: "SUCCESS",
          entity_id: "SYS-INIT",
          duration_ms: 24,
          created_at: new Date().toISOString()
        },
        {
          event_type: "LEAD_INGEST",
          action: "QUALIFY_LEAD",
          status: "QUALIFIED_HOT",
          entity_id: "lead_demo_01",
          duration_ms: 48,
          created_at: new Date(Date.now() - 3600000).toISOString()
        },
        {
          event_type: "INVOICE_AUDIT",
          action: "ARITHMETIC_RECONCILIATION",
          status: "SUCCESS_MATCH",
          entity_id: "inv_01",
          duration_ms: 21,
          created_at: new Date(Date.now() - 7200000).toISOString()
        },
        {
          event_type: "SECURITY_GUARD",
          action: "PROMPT_INJECTION_BLOCKED",
          status: "FLAGGED_ESCALATED",
          entity_id: "tkt_03",
          duration_ms: 12,
          created_at: new Date(Date.now() - 9000000).toISOString()
        }
      ]
    };
  }

  function loadState() {
    try {
      const stored = localStorage.getItem(LOCAL_STORAGE_KEY);
      if (stored) return JSON.parse(stored);
    } catch (e) {
      console.warn("LocalStorage unavailable, using in-memory state.");
    }
    const fresh = getInitialMockState();
    saveState(fresh);
    return fresh;
  }

  function saveState(state) {
    try {
      localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(state));
    } catch (e) {
      // Ignored if storage disabled
    }
  }

  let clientState = loadState();

  // Client Simulation Dispatcher
  function simulateApi(endpoint, options = {}) {
    const method = (options.method || "GET").toUpperCase();
    console.log(`[ClientSimulation] ${method} ${endpoint}`);

    // Telemetry & Metrics
    if (endpoint.startsWith("/api/v1/metrics")) {
      return {
        success: true,
        data: {
          mode: clientState.mode,
          counts: {
            leads: clientState.leads.length,
            support_tickets: clientState.support.length,
            invoices: clientState.invoices.length,
            pending_approvals: clientState.approvals.filter(a => a.status === "PENDING").length
          },
          financials: {
            verified_revenue_usd: clientState.verifiedRevenue,
            total_invoice_spend_usd: clientState.invoices.reduce((a, b) => a + (b.extracted_total || 0), 0)
          },
          sla: {
            avg_lead_latency_seconds: 0.048,
            lead_sla_target_seconds: 10.0
          }
        }
      };
    }

    // Audit logs
    if (endpoint.startsWith("/api/v1/audit")) {
      return {
        success: true,
        data: clientState.audit.slice(0, 50)
      };
    }

    // Leads API
    if (endpoint.startsWith("/api/v1/leads")) {
      if (method === "GET") {
        const urlParams = new URLSearchParams(endpoint.split("?")[1] || "");
        const prio = urlParams.get("priority");
        const list = prio ? clientState.leads.filter(l => l.priority === prio) : clientState.leads;
        return { success: true, data: list };
      }
      if (method === "POST") {
        const body = JSON.parse(options.body || "{}");
        const score = body.budget >= 50000 ? 92 : (body.budget >= 15000 ? 76 : 48);
        const priority = score >= 80 ? "HOT" : (score >= 60 ? "WARM" : "COLD");
        const newLead = {
          id: `lead_${Date.now()}`,
          full_name: body.full_name || "Enterprise Lead",
          email: body.email || "prospect@domain.com",
          company: body.company || "Enterprise Corp",
          budget: parseFloat(body.budget || 0),
          company_size: body.company_size || "100+",
          score: score,
          priority: priority,
          status: "QUALIFIED",
          airtable_record_id: `rec_${Math.random().toString(36).substring(2, 9)}`,
          latency_seconds: 0.048,
          ai_summary: `Prospect ${body.full_name} from ${body.company} qualified with budget $${body.budget.toLocaleString()}.`,
          talking_points: [
            "Demonstrate automated accounts payable & invoice OCR.",
            "Highlight strict draft-only email governance and security.",
            "Offer direct walkthrough of custom Slack project integration."
          ],
          assigned_rep: "Solutions Architecture Team",
          created_at: new Date().toISOString()
        };
        clientState.leads.unshift(newLead);
        clientState.audit.unshift({
          event_type: "LEAD_INGEST",
          action: "QUALIFY_LEAD",
          status: `QUALIFIED_${priority}`,
          entity_id: newLead.id,
          duration_ms: 48,
          created_at: new Date().toISOString()
        });
        saveState(clientState);
        return { success: true, data: { ...newLead, execution_seconds: 0.048 } };
      }
    }

    // Support Tickets API
    if (endpoint.startsWith("/api/v1/support/tickets")) {
      if (method === "GET") {
        return { success: true, data: clientState.support };
      }
      if (method === "POST") {
        const body = JSON.parse(options.body || "{}");
        const lowerBody = (body.body || "").toLowerCase();
        const isInjection = lowerBody.includes("ignore previous") || lowerBody.includes("system prompt override") || lowerBody.includes("developer mode");
        
        let intent = "technical_support";
        let urgency = "STANDARD";
        if (lowerBody.includes("error") || lowerBody.includes("urgent") || lowerBody.includes("outage") || lowerBody.includes("crash")) {
          intent = "urgent_incidents";
          urgency = "URGENT";
        } else if (lowerBody.includes("refund") || lowerBody.includes("billing") || lowerBody.includes("charge")) {
          intent = "billing";
          urgency = "STANDARD";
        }

        const newTicket = {
          id: `tkt_${Date.now()}`,
          sender: body.sender,
          subject: body.subject,
          sanitized_body: isInjection ? "[BLOCKED PROMPT INJECTION]: Malicious override quarantined." : body.body,
          intent: isInjection ? "urgent_incidents" : intent,
          urgency: isInjection ? "HIGH" : urgency,
          sentiment: isInjection ? "NEGATIVE" : "NEUTRAL",
          confidence: 0.96,
          draft_response: isInjection
            ? "Your request has been routed to human security review due to policy violations."
            : `Hello,\n\nThank you for contacting support regarding "${body.subject}". We have verified this inquiry against our active policy guidelines and prepared this draft for agent review.\n\nResolution Priority: ${urgency}`,
          kb_references: isInjection ? ["KB-SEC-009: Threat Quarantine"] : ["KB-GEN-001: General Operations"],
          is_draft: true,
          prompt_injection_flag: isInjection,
          requires_escalation: isInjection || urgency === "URGENT",
          created_at: new Date().toISOString()
        };
        clientState.support.unshift(newTicket);
        if (newTicket.requires_escalation) {
          clientState.approvals.unshift({
            id: `appr_${Date.now()}`,
            entity_type: isInjection ? "SECURITY_ESCALATION" : "SUPPORT_ESCALATION",
            title: `Escalated Ticket: ${body.subject}`,
            description: `Sender: ${body.sender} | Reason: ${isInjection ? 'Prompt injection attack' : 'Urgent incident triage'}`,
            requested_by: "Support Engine",
            status: "PENDING",
            created_at: new Date().toISOString()
          });
        }
        clientState.audit.unshift({
          event_type: "SUPPORT_TRIAGE",
          action: isInjection ? "PROMPT_INJECTION_DEFENSE" : "DRAFT_GENERATED",
          status: isInjection ? "FLAGGED_INJECTION" : "SUCCESS",
          entity_id: newTicket.id,
          duration_ms: 32,
          created_at: new Date().toISOString()
        });
        saveState(clientState);
        return { success: true, data: newTicket };
      }
    }

    // Invoices API
    if (endpoint.startsWith("/api/v1/invoices")) {
      if (endpoint.endsWith("/approve")) {
        const id = endpoint.split("/")[4];
        const inv = clientState.invoices.find(i => i.id === id);
        if (inv) inv.status = "APPROVED";
        saveState(clientState);
        return { success: true, data: inv };
      }
      if (endpoint.endsWith("/export")) {
        const row = Math.floor(Math.random() * 40) + 12;
        return { success: true, data: { row_number: row, spreadsheet_id: "demo_spreadsheet_1042" } };
      }
      if (method === "GET") {
        return { success: true, data: clientState.invoices };
      }
      if (method === "POST" && endpoint.includes("/upload")) {
        const newInv = {
          id: `inv_${Date.now()}`,
          filename: "Uploaded_Invoice_Audit.pdf",
          vendor: "Enterprise Vendor Solutions LLC",
          invoice_number: `INV-${Date.now().toString().slice(-4)}`,
          extracted_total: 2475.0,
          calculated_total: 2475.0,
          is_arithmetic_valid: true,
          duplicate_flag: false,
          status: "APPROVED",
          created_at: new Date().toISOString()
        };
        clientState.invoices.unshift(newInv);
        clientState.audit.unshift({
          event_type: "INVOICE_AUDIT",
          action: "ARITHMETIC_CHECK",
          status: "SUCCESS_VALID",
          entity_id: newInv.id,
          duration_ms: 21,
          created_at: new Date().toISOString()
        });
        saveState(clientState);
        return { success: true, data: newInv };
      }
    }

    // Enterprise Orchestration
    if (endpoint.startsWith("/api/v1/orchestration/projects")) {
      return { success: true, data: clientState.projects };
    }
    if (endpoint.startsWith("/api/v1/orchestration/digest")) {
      return {
        success: true,
        data: {
          period_start: "2026-10-16",
          period_end: "2026-10-23",
          source_coverage: "100% Verified Telemetry Records",
          ai_executive_summary: "Strong weekly momentum: customer acquisition pipeline processed all leads under 100ms. Accounts payable verified 100% of standard invoices with zero undetected arithmetic errors. Stripe payment settlement verified via HMAC-SHA256 signatures with zero ledger discrepancies.",
          metrics: {
            leads_count: clientState.leads.length,
            qualified_leads: clientState.leads.filter(l => l.status === "QUALIFIED").length,
            urgent_tickets: clientState.support.filter(t => t.urgency === "CRITICAL" || t.urgency === "URGENT").length,
            verified_revenue: clientState.verifiedRevenue,
            total_invoice_spend: clientState.invoices.reduce((a, b) => a + (b.extracted_total || 0), 0)
          }
        }
      };
    }
    if (endpoint.startsWith("/api/v1/orchestration/approvals")) {
      if (endpoint.includes("/resolve")) {
        const id = endpoint.split("/")[5];
        const body = JSON.parse(options.body || "{}");
        const item = clientState.approvals.find(a => a.id === id);
        if (item) item.status = body.action || "APPROVED";
        saveState(clientState);
        return { success: true, data: item };
      }
      return {
        success: true,
        data: clientState.approvals.filter(a => a.status === "PENDING")
      };
    }

    if (endpoint.startsWith("/api/v1/health")) {
      return {
        success: true,
        data: {
          status: "healthy",
          mode: clientState.mode,
          uptime_seconds: 3600.0,
          database_connected: true,
          services: { airtable: "mock", slack: "mock", stripe: "verified", sheets: "mock" }
        }
      };
    }

    return { success: true, data: [] };
  }

  // Unified API Client Helper (Live or Simulation Fallback)
  async function apiFetch(endpoint, options = {}) {
    if (isStaticHost) {
      return simulateApi(endpoint, options);
    }
    try {
      const res = await fetch(endpoint, options);
      if (!res.ok) {
        // Fallback to simulation if endpoint not found
        if (res.status === 404) {
          return simulateApi(endpoint, options);
        }
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP Error ${res.status}`);
      }
      return await res.json();
    } catch (err) {
      console.warn(`[FastAPI Backend unreachable, switching to Client Simulation Engine for ${endpoint}]`, err);
      return simulateApi(endpoint, options);
    }
  }

  // View Dispatcher
  function loadViewData(view) {
    if (view === "command-center") fetchCommandCenterData();
    else if (view === "lead-intelligence") fetchLeads();
    else if (view === "support-intelligence") fetchSupportTickets();
    else if (view === "invoice-intelligence") fetchInvoices();
    else if (view === "enterprise-orchestration") fetchProjects();
    else if (view === "approval-center") fetchApprovals();
    else if (view === "integration-registry") fetchIntegrationHealth();
  }

  // 1. Command Center Telemetry
  async function fetchCommandCenterData() {
    try {
      const metricsRes = await apiFetch("/api/v1/metrics");
      if (metricsRes.success && metricsRes.data) {
        const d = metricsRes.data;
        document.getElementById("kpi-leads-count").textContent = d.counts.leads || 0;
        document.getElementById("kpi-leads-sub").textContent = `Avg SLA: ${d.sla.avg_lead_latency_seconds}s (Target <${d.sla.lead_sla_target_seconds}s)`;
        document.getElementById("kpi-support-count").textContent = d.counts.support_tickets || 0;
        document.getElementById("kpi-invoices-count").textContent = d.counts.invoices || 0;
        document.getElementById("kpi-revenue").textContent = `$${(d.financials.verified_revenue_usd || 0).toLocaleString(undefined, {minimumFractionDigits: 2})}`;
        document.getElementById("sidebar-approval-count").textContent = d.counts.pending_approvals || 0;
        document.getElementById("global-mode-pill").textContent = (d.mode || "DEMO").toUpperCase();
      }

      const auditRes = await apiFetch("/api/v1/audit?limit=8");
      const tbody = document.getElementById("telemetry-stream-body");
      if (auditRes.success && auditRes.data && auditRes.data.length > 0) {
        tbody.innerHTML = auditRes.data.map(ev => `
          <tr>
            <td><span class="tag tag-pending">${ev.event_type}</span></td>
            <td><strong>${ev.action}</strong></td>
            <td><span class="tag ${ev.status.startsWith('FAIL') || ev.status.includes('FLAG') ? 'tag-hot' : 'tag-success'}">${ev.status}</span></td>
            <td><code style="font-size:0.78rem;">${ev.entity_id || 'System'}</code></td>
            <td>${ev.duration_ms ? ev.duration_ms + 'ms' : 'N/A'}</td>
            <td style="color:var(--text-dim);">${new Date(ev.created_at).toLocaleTimeString()}</td>
          </tr>
        `).join("");
      }
    } catch (err) {
      console.error("Failed to load telemetry:", err);
    }
  }

  const btnRefresh = document.getElementById("btn-refresh-telemetry");
  if (btnRefresh) {
    btnRefresh.addEventListener("click", () => fetchCommandCenterData());
  }

  // 2. Lead Intelligence
  async function fetchLeads() {
    const priorityElem = document.getElementById("filter-lead-priority");
    const priority = priorityElem ? priorityElem.value : "";
    const url = priority ? `/api/v1/leads?priority=${priority}` : "/api/v1/leads";
    try {
      const res = await apiFetch(url);
      const tbody = document.getElementById("leads-table-body");
      if (res.success && res.data) {
        if (res.data.length === 0) {
          tbody.innerHTML = `<tr><td colspan="9" style="text-align:center;">No leads found.</td></tr>`;
          return;
        }
        tbody.innerHTML = res.data.map(lead => {
          const prioClass = lead.priority === 'HOT' ? 'tag-hot' : (lead.priority === 'WARM' ? 'tag-warm' : 'tag-cold');
          return `
            <tr>
              <td>
                <div style="font-weight:600;">${lead.full_name}</div>
                <div style="font-size:0.75rem; color:var(--text-dim);">${lead.email}</div>
              </td>
              <td>${lead.company || 'Unknown'}</td>
              <td>$${(lead.budget || 0).toLocaleString()}</td>
              <td><strong style="color:var(--accent-cyan);">${lead.score}</strong> / 100</td>
              <td><span class="tag ${prioClass}">${lead.priority}</span></td>
              <td><span class="tag tag-success">${lead.status}</span></td>
              <td><code>${lead.airtable_record_id || 'Mock Rec'}</code></td>
              <td>${lead.latency_seconds}s</td>
              <td>
                <button class="btn btn-primary btn-view-lead" data-id="${lead.id}" style="padding:4px 10px; font-size:0.75rem;">
                  Talking Points
                </button>
              </td>
            </tr>
          `;
        }).join("");

        // Attach modal listeners
        document.querySelectorAll(".btn-view-lead").forEach(btn => {
          btn.addEventListener("click", () => {
            const id = btn.getAttribute("data-id");
            const lead = res.data.find(l => l.id === id);
            if (lead) {
              const pointsHtml = (lead.talking_points || []).map(p => `<li>${p}</li>`).join("");
              openModal(`Lead Discovery: ${lead.company}`, `
                <div style="margin-bottom:12px;"><strong>AI Executive Summary:</strong><p>${lead.ai_summary || 'N/A'}</p></div>
                <div style="margin-bottom:12px;"><strong>Strategic Talking Points:</strong><ul style="padding-left:20px;">${pointsHtml}</ul></div>
                <div style="font-size:0.78rem; color:var(--text-dim);">Assigned Rep: ${lead.assigned_rep || 'Enterprise Director'} | Score: ${lead.score}/100</div>
              `);
            }
          });
        });
      }
    } catch (err) {
      console.error(err);
    }
  }

  const filterPriority = document.getElementById("filter-lead-priority");
  if (filterPriority) filterPriority.addEventListener("change", fetchLeads);

  const leadForm = document.getElementById("lead-intake-form");
  if (leadForm) {
    leadForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const payload = {
        full_name: document.getElementById("lead-name").value,
        email: document.getElementById("lead-email").value,
        company: document.getElementById("lead-company").value,
        budget: parseFloat(document.getElementById("lead-budget").value || 0),
        company_size: document.getElementById("lead-size").value,
        needs_description: document.getElementById("lead-needs").value,
        source: "command_center_simulator",
        consent: true,
      };
      try {
        const res = await apiFetch("/api/v1/leads", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        alert(`Lead Qualified! Score: ${res.data.score}/100 [${res.data.priority}] in ${res.data.execution_seconds}s`);
        fetchLeads();
        fetchCommandCenterData();
        leadForm.reset();
      } catch (err) {
        alert(`Failed to ingest lead: ${err.message}`);
      }
    });
  }

  // 3. Support Intelligence
  async function fetchSupportTickets() {
    try {
      const res = await apiFetch("/api/v1/support/tickets");
      const tbody = document.getElementById("support-table-body");
      if (res.success && res.data) {
        tbody.innerHTML = res.data.map(t => `
          <tr>
            <td>${t.sender}</td>
            <td><strong>${t.subject}</strong></td>
            <td><span class="tag tag-cold">${t.intent}</span></td>
            <td><span class="tag ${t.urgency.includes('CRITICAL') || t.urgency.includes('URGENT') ? 'tag-critical' : 'tag-warm'}">${t.urgency}</span></td>
            <td>${t.sentiment}</td>
            <td>
              ${t.prompt_injection_flag ? '<span class="tag tag-hot">🚨 Injection Defended</span>' : '<span class="tag tag-success">Clean</span>'}
            </td>
            <td>
              ${t.requires_escalation ? '<span class="tag tag-hot">Escalated</span>' : '<span class="tag tag-success">Standard</span>'}
            </td>
            <td>
              <button class="btn btn-primary btn-view-ticket" data-id="${t.id}" style="padding:4px 10px; font-size:0.75rem;">
                View Draft
              </button>
            </td>
          </tr>
        `).join("");

        document.querySelectorAll(".btn-view-ticket").forEach(btn => {
          btn.addEventListener("click", () => {
            const id = btn.getAttribute("data-id");
            const t = res.data.find(item => item.id === id);
            if (t) {
              openModal(`Draft Response: ${t.subject}`, `
                <div style="margin-bottom:12px;"><strong>Customer Message:</strong><p style="background:var(--bg-primary); padding:10px; border-radius:6px;">${t.sanitized_body}</p></div>
                <div style="margin-bottom:12px;"><strong>AI Grounded Draft (Draft-Only Mode):</strong><pre style="white-space:pre-wrap; background:var(--bg-primary); padding:12px; border-radius:6px; font-family:inherit;">${t.draft_response}</pre></div>
                <div style="font-size:0.78rem; color:var(--text-dim);">Evidence Citations: ${(t.kb_references || []).join(', ') || 'None'}</div>
              `);
            }
          });
        });
      }
    } catch (err) {
      console.error(err);
    }
  }

  const supportForm = document.getElementById("support-sim-form");
  if (supportForm) {
    supportForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const payload = {
        sender: document.getElementById("support-sender").value,
        subject: document.getElementById("support-subject").value,
        body: document.getElementById("support-body").value,
      };
      try {
        const res = await apiFetch("/api/v1/support/tickets", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        alert(`Ticket Triaged! Intent: ${res.data.intent} | Urgency: ${res.data.urgency}\nResponse safely saved in Mailbox Drafts.`);
        fetchSupportTickets();
        fetchCommandCenterData();
        supportForm.reset();
      } catch (err) {
        alert(`Support triage error: ${err.message}`);
      }
    });
  }

  // 4. Invoice Intelligence
  const dropzone = document.getElementById("invoice-dropzone");
  const fileInput = document.getElementById("invoice-file-input");

  if (dropzone && fileInput) {
    dropzone.addEventListener("click", () => fileInput.click());

    fileInput.addEventListener("change", async () => {
      if (fileInput.files.length > 0) {
        const file = fileInput.files[0];
        try {
          const res = await apiFetch("/api/v1/invoices/upload", {
            method: "POST",
          });
          if (res.success) {
            alert(`Invoice Processed! Vendor: ${res.data.vendor}\nCalculated: $${res.data.calculated_total} | Extracted: $${res.data.extracted_total}\nArithmetic Valid: ${res.data.is_arithmetic_valid}`);
            fetchInvoices();
            fetchCommandCenterData();
          }
        } catch (err) {
          alert(`Failed to upload invoice: ${err.message}`);
        }
      }
    });
  }

  async function fetchInvoices() {
    try {
      const res = await apiFetch("/api/v1/invoices");
      const tbody = document.getElementById("invoices-table-body");
      if (res.success && res.data) {
        tbody.innerHTML = res.data.map(inv => {
          const arithBadge = inv.is_arithmetic_valid ? '<span class="tag tag-success">MATCH (±$0.01)</span>' : '<span class="tag tag-hot">DISCREPANCY</span>';
          const dupBadge = inv.duplicate_flag ? '<span class="tag tag-hot">DUPLICATE</span>' : '<span class="tag tag-success">UNIQUE</span>';
          return `
            <tr>
              <td><code>${inv.filename}</code></td>
              <td>${inv.vendor || 'Unknown'}</td>
              <td>${inv.invoice_number || 'N/A'}</td>
              <td><strong>$${(inv.extracted_total || 0).toFixed(2)}</strong></td>
              <td>$${(inv.calculated_total || 0).toFixed(2)}</td>
              <td>${arithBadge}</td>
              <td>${dupBadge}</td>
              <td><span class="tag ${inv.status === 'APPROVED' ? 'tag-success' : 'tag-warm'}">${inv.status}</span></td>
              <td>
                ${inv.status !== 'APPROVED' ? `<button class="btn btn-primary btn-approve-inv" data-id="${inv.id}" style="padding:2px 8px; font-size:0.75rem;">Approve</button>` : ''}
                <button class="btn btn-export-inv" data-id="${inv.id}" style="padding:2px 8px; font-size:0.75rem;">Sheets Export</button>
              </td>
            </tr>
          `;
        }).join("");

        document.querySelectorAll(".btn-approve-inv").forEach(btn => {
          btn.addEventListener("click", async () => {
            const id = btn.getAttribute("data-id");
            await apiFetch(`/api/v1/invoices/${id}/approve`, { method: "POST" });
            fetchInvoices();
            fetchCommandCenterData();
          });
        });

        document.querySelectorAll(".btn-export-inv").forEach(btn => {
          btn.addEventListener("click", async () => {
            const id = btn.getAttribute("data-id");
            const res = await apiFetch(`/api/v1/invoices/${id}/export`, { method: "POST" });
            alert(`Exported to Google Sheets Row #${res.data.row_number}`);
            fetchInvoices();
          });
        });
      }
    } catch (err) {
      console.error(err);
    }
  }

  // 5. Enterprise Orchestration
  async function fetchProjects() {
    try {
      const res = await apiFetch("/api/v1/orchestration/projects");
      const tbody = document.getElementById("projects-table-body");
      if (res.success && res.data) {
        document.getElementById("kpi-orch-projects").textContent = res.data.length;
        document.getElementById("kpi-orch-active").textContent = res.data.filter(p => p.status === 'ACTIVE').length;

        tbody.innerHTML = res.data.map(p => `
          <tr>
            <td><code>${p.project_code}</code></td>
            <td><strong>${p.client_name}</strong></td>
            <td>${p.client_email}</td>
            <td>${p.service_tier}</td>
            <td><span class="tag ${p.contract_status === 'APPROVED' ? 'tag-success' : 'tag-pending'}">${p.contract_status}</span></td>
            <td><span class="tag ${p.payment_status === 'PAID' ? 'tag-success' : 'tag-warm'}">${p.payment_status}</span></td>
            <td><code>${p.slack_channel || 'Not created'}</code></td>
            <td><span class="tag tag-cold">${p.status}</span></td>
          </tr>
        `).join("");
      }
    } catch (err) {
      console.error(err);
    }
  }

  const btnDigest = document.getElementById("btn-generate-digest");
  if (btnDigest) {
    btnDigest.addEventListener("click", async () => {
      try {
        const res = await apiFetch("/api/v1/orchestration/digest");
        if (res.success && res.data) {
          const d = res.data;
          openModal("Weekly Executive Operational Briefing", `
            <div style="font-size:0.75rem; color:var(--text-dim); margin-bottom:12px;">Reporting Period: ${d.period_start} to ${d.period_end} | Coverage: ${d.source_coverage}</div>
            <div style="background:var(--bg-primary); padding:16px; border-radius:8px; line-height:1.7; margin-bottom:16px;">
              <p>${d.ai_executive_summary}</p>
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; font-size:0.82rem;">
              <div><strong>Qualified Leads:</strong> ${d.metrics.qualified_leads} / ${d.metrics.leads_count}</div>
              <div><strong>Urgent Tickets:</strong> ${d.metrics.urgent_tickets}</div>
              <div><strong>Verified Revenue:</strong> $${d.metrics.verified_revenue.toLocaleString()}</div>
              <div><strong>Total Invoice Spend:</strong> $${d.metrics.total_invoice_spend.toLocaleString()}</div>
            </div>
          `);
        }
      } catch (err) {
        alert(`Failed to generate digest: ${err.message}`);
      }
    });
  }

  // 6. Approval Center
  async function fetchApprovals() {
    try {
      const res = await apiFetch("/api/v1/orchestration/approvals?status=PENDING");
      const tbody = document.getElementById("approvals-table-body");
      if (res.success && res.data) {
        const countBadge = document.getElementById("approval-queue-count-badge");
        if (countBadge) countBadge.textContent = `${res.data.length} Pending`;
        const sidebarCount = document.getElementById("sidebar-approval-count");
        if (sidebarCount) sidebarCount.textContent = res.data.length;

        if (res.data.length === 0) {
          tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;">No pending approvals in queue.</td></tr>`;
          return;
        }

        tbody.innerHTML = res.data.map(appr => `
          <tr>
            <td><span class="tag tag-hot">${appr.entity_type}</span></td>
            <td><strong>${appr.title}</strong></td>
            <td style="max-width:300px; white-space:pre-wrap; font-size:0.78rem;">${appr.description}</td>
            <td>${appr.requested_by}</td>
            <td>${new Date(appr.created_at).toLocaleTimeString()}</td>
            <td>
              <button class="btn btn-primary btn-resolve-appr" data-id="${appr.id}" data-action="APPROVED" style="padding:4px 10px; font-size:0.75rem;">Approve</button>
              <button class="btn btn-danger btn-resolve-appr" data-id="${appr.id}" data-action="REJECTED" style="padding:4px 10px; font-size:0.75rem;">Reject</button>
            </td>
          </tr>
        `).join("");

        document.querySelectorAll(".btn-resolve-appr").forEach(btn => {
          btn.addEventListener("click", async () => {
            const id = btn.getAttribute("data-id");
            const action = btn.getAttribute("data-action");
            await apiFetch(`/api/v1/orchestration/approvals/${id}/resolve`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ action: action, resolved_by: "Command Center Admin" }),
            });
            fetchApprovals();
            fetchCommandCenterData();
          });
        });
      }
    } catch (err) {
      console.error(err);
    }
  }

  // 7. Integration Registry
  async function fetchIntegrationHealth() {
    try {
      const auditRes = await apiFetch("/api/v1/audit?limit=50");
      if (auditRes.success && auditRes.data) {
        const tbody = document.getElementById("audit-full-table-body");
        if (tbody) {
          tbody.innerHTML = auditRes.data.map(ev => `
            <tr>
              <td><code>${ev.event_type}</code></td>
              <td><strong>${ev.action}</strong></td>
              <td><span class="tag ${ev.status.startsWith('FAIL') || ev.status.includes('FLAG') ? 'tag-hot' : 'tag-success'}">${ev.status}</span></td>
              <td><code style="font-size:0.75rem;">${ev.entity_id || 'System'}</code></td>
              <td>${new Date(ev.created_at).toLocaleString()}</td>
            </tr>
          `).join("");
        }
      }
    } catch (err) {
      console.error(err);
    }
  }

  // Initial Boot
  fetchCommandCenterData();
});
