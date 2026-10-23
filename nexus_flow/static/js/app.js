/**
 * NEXUS Flow AI — Unified Command Center Web Interface Controller
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

  btnCloseModal.addEventListener("click", () => {
    modal.classList.remove("active");
  });

  modal.addEventListener("click", (e) => {
    if (e.target === modal) modal.classList.remove("active");
  });

  // API Client Helper
  async function apiFetch(endpoint, options = {}) {
    try {
      const res = await fetch(endpoint, options);
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP Error ${res.status}`);
      }
      return await res.json();
    } catch (err) {
      console.error(`API Fetch Error [${endpoint}]:`, err);
      throw err;
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
            <td><span class="tag ${ev.status.startsWith('FAIL') ? 'tag-hot' : 'tag-success'}">${ev.status}</span></td>
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

  document.getElementById("btn-refresh-telemetry").addEventListener("click", () => {
    fetchCommandCenterData();
  });

  // 2. Lead Intelligence
  async function fetchLeads() {
    const priority = document.getElementById("filter-lead-priority").value;
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

  document.getElementById("filter-lead-priority").addEventListener("change", fetchLeads);

  document.getElementById("lead-intake-form").addEventListener("submit", async (e) => {
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
    } catch (err) {
      alert(`Failed to ingest lead: ${err.message}`);
    }
  });

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
            <td><span class="tag ${t.urgency.includes('CRITICAL') ? 'tag-critical' : 'tag-warm'}">${t.urgency}</span></td>
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

  document.getElementById("support-sim-form").addEventListener("submit", async (e) => {
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
      alert(`Ticket Triaged! Intent: ${res.data.intent} | Urgency: ${res.data.urgency}\nDraft Saved in Mailbox.`);
      fetchSupportTickets();
      fetchCommandCenterData();
    } catch (err) {
      alert(`Support triage error: ${err.message}`);
    }
  });

  // 4. Invoice Intelligence
  const dropzone = document.getElementById("invoice-dropzone");
  const fileInput = document.getElementById("invoice-file-input");

  dropzone.addEventListener("click", () => fileInput.click());

  fileInput.addEventListener("change", async () => {
    if (fileInput.files.length > 0) {
      const file = fileInput.files[0];
      const formData = new FormData();
      formData.append("file", file);

      try {
        const res = await fetch("/api/v1/invoices/upload", {
          method: "POST",
          body: formData,
        });
        const data = await res.json();
        if (data.success) {
          alert(`Invoice Processed! Vendor: ${data.data.vendor}\nCalculated Sum: $${data.data.calculated_total}\nExtracted Total: $${data.data.extracted_total}\nArithmetic Valid: ${data.data.is_arithmetic_valid}`);
          fetchInvoices();
          fetchCommandCenterData();
        } else {
          alert(`Error: ${data.detail || "Processing failed"}`);
        }
      } catch (err) {
        alert(`Failed to upload invoice: ${err.message}`);
      }
    }
  });

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

  document.getElementById("btn-generate-digest").addEventListener("click", async () => {
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

  // 6. Approval Center
  async function fetchApprovals() {
    try {
      const res = await apiFetch("/api/v1/orchestration/approvals?status=PENDING");
      const tbody = document.getElementById("approvals-table-body");
      if (res.success && res.data) {
        document.getElementById("approval-queue-count-badge").textContent = `${res.data.length} Pending`;
        document.getElementById("sidebar-approval-count").textContent = res.data.length;

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
      const healthRes = await apiFetch("/api/v1/health");
      const auditRes = await apiFetch("/api/v1/audit?limit=50");

      if (auditRes.success && auditRes.data) {
        const tbody = document.getElementById("audit-full-table-body");
        tbody.innerHTML = auditRes.data.map(ev => `
          <tr>
            <td><code>${ev.event_type}</code></td>
            <td><strong>${ev.action}</strong></td>
            <td><span class="tag ${ev.status.startsWith('FAIL') ? 'tag-hot' : 'tag-success'}">${ev.status}</span></td>
            <td><code style="font-size:0.75rem;">${ev.details_json || '{}'}</code></td>
            <td>${new Date(ev.created_at).toLocaleString()}</td>
          </tr>
        `).join("");
      }
    } catch (err) {
      console.error(err);
    }
  }

  // Initial Boot
  fetchCommandCenterData();
});
