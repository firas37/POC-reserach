/* ============================================
   Zyga Research & Enrichment Agent — App Logic
   API calls, result rendering, agent trace panel
   ============================================ */

// ── Demo Scenarios ──────────────────────────
const DEMO_PROSPECTS = {
    high: {
        first_name: "Alex",
        last_name: "Rivera",
        title: "Head of Growth",
        company: "Rippling",
        domain: "rippling.com",
        linkedin_url: "",
    },
    medium: {
        first_name: "Marie",
        last_name: "Dupont",
        title: "Marketing Director",
        company: "Pennylane",
        domain: "pennylane.com",
        linkedin_url: "",
    },
    low: {
        first_name: "David",
        last_name: "Martin",
        title: "Freelance Consultant",
        company: "Self-employed",
        domain: "",
        linkedin_url: "",
    },
};

// ── DOM References ──────────────────────────
const form = document.getElementById("researchForm");
const submitBtn = document.getElementById("submitBtn");
const loadingSection = document.getElementById("loadingSection");
const resultsSection = document.getElementById("resultsSection");
const resultCard = document.getElementById("resultCard");
const errorSection = document.getElementById("errorSection");
const errorCard = document.getElementById("errorCard");
const traceContent = document.getElementById("traceContent");
const traceToggle = document.getElementById("traceToggle");
const tracePanel = document.getElementById("tracePanel");

// ── Trace Panel Toggle ──────────────────────
traceToggle.addEventListener("click", () => {
    tracePanel.classList.toggle("collapsed");
});

// ── Load Demo ───────────────────────────────
function loadDemo(scenario) {
    const prospect = DEMO_PROSPECTS[scenario];
    if (!prospect) return;

    document.getElementById("firstName").value = prospect.first_name;
    document.getElementById("lastName").value = prospect.last_name;
    document.getElementById("company").value = prospect.company;
    document.getElementById("title").value = prospect.title;
    document.getElementById("domain").value = prospect.domain;
    document.getElementById("linkedinUrl").value = prospect.linkedin_url;

    // Highlight active demo button
    document.querySelectorAll(".demo-btn").forEach((btn) => btn.classList.remove("active"));
    const activeBtn = document.getElementById(`demo-${scenario}`);
    if (activeBtn) activeBtn.classList.add("active");
}

// ── Form Submit ─────────────────────────────
async function handleSubmit(event) {
    event.preventDefault();
    const prospect = {
        first_name: document.getElementById("firstName").value.trim(),
        last_name: document.getElementById("lastName").value.trim(),
        company: document.getElementById("company").value.trim(),
        title: document.getElementById("title").value.trim() || null,
        domain: document.getElementById("domain").value.trim() || null,
        linkedin_url: document.getElementById("linkedinUrl").value.trim() || null,
    };

    await researchProspect(prospect);
}

// ── API Call ─────────────────────────────────
async function researchProspect(prospect) {
    showLoading();
    hideResults();
    hideError();

    // Animate loading steps
    const stepInterval = animateLoadingSteps();

    try {
        const response = await fetch("/api/research", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(prospect),
        });

        clearInterval(stepInterval);

        if (!response.ok) {
            const err = await response.json().catch(() => ({ detail: "Unknown error" }));
            throw new Error(err.detail || `HTTP ${response.status}`);
        }

        const result = await response.json();
        hideLoading();
        renderResult(result);
        renderAgentTrace(result);
    } catch (error) {
        clearInterval(stepInterval);
        hideLoading();
        showError(error.message);
    }
}

// ── Loading State ───────────────────────────
function showLoading() {
    loadingSection.style.display = "block";
    submitBtn.disabled = true;
    // Reset all steps
    document.querySelectorAll(".loading-step").forEach((step, i) => {
        step.classList.remove("active", "done");
        if (i === 0) step.classList.add("active");
    });
}

function hideLoading() {
    loadingSection.style.display = "none";
    submitBtn.disabled = false;
}

function animateLoadingSteps() {
    const steps = document.querySelectorAll(".loading-step");
    let currentStep = 0;

    return setInterval(() => {
        if (currentStep < steps.length) {
            steps[currentStep].classList.remove("active");
            steps[currentStep].classList.add("done");
            currentStep++;
            if (currentStep < steps.length) {
                steps[currentStep].classList.add("active");
            }
        }
    }, 3000);
}

// ── Render Result ───────────────────────────
function renderResult(result) {
    const scoreClass = getScoreClass(result.icp_score);
    const initials = getInitials(result.name);

    const contactHTML = buildContactHTML(result);
    const hooksHTML = buildHooksHTML(result.personalization_hooks);

    resultCard.innerHTML = `
        <!-- Header -->
        <div class="result-header">
            <div class="result-profile">
                <div class="result-avatar">${initials}</div>
                <div>
                    <div class="result-name">${esc(result.name)}</div>
                    <div class="result-title-company">${esc(result.title || "")}${result.title && result.company ? " · " : ""}${esc(result.company)}</div>
                </div>
            </div>
            <div class="icp-badge ${scoreClass}">
                <span class="icp-score-value">${result.icp_score}</span>
                <span class="icp-label">ICP Score</span>
            </div>
        </div>

        <!-- Body -->
        <div class="result-body">
            <div class="result-field">
                <span class="result-field-label">Industry</span>
                <span class="result-field-value">${esc(result.industry || "—")}</span>
            </div>
            <div class="result-field">
                <span class="result-field-label">Company Size</span>
                <span class="result-field-value">${esc(result.company_size || "—")}</span>
            </div>
            <div class="result-field full-width">
                <span class="result-field-label">ICP Reasoning</span>
                <span class="result-field-value">${esc(result.icp_reasoning)}</span>
            </div>
            <div class="result-field full-width">
                <span class="result-field-label">Research Summary</span>
                <span class="result-field-value">${esc(result.research_summary || "—")}</span>
            </div>
            <div class="result-field full-width">
                <span class="result-field-label">Personalization Hooks</span>
                <div class="result-field-value">${hooksHTML || "—"}</div>
            </div>
            <div class="result-field full-width">
                <span class="result-field-label">Contact Data</span>
                <div class="result-field-value" id="contactDataContainer">${contactHTML}</div>
            </div>
        </div>

        <!-- Footer -->
        <div class="result-footer">
            <span class="result-action">💡 ${esc(result.recommended_action || "No action recommended")}</span>
        </div>
    `;

    resultsSection.style.display = "block";
}

function buildContactHTML(result) {
    if (result.icp_score >= 60) {
        // Store data on the button using data attributes for safe event handling
        const btn = document.createElement("button");
        btn.className = "enrich-btn";
        btn.innerHTML = `
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
            </svg>
            Enrich Contact (1 Credit)
        `;
        // We return the HTML string, but set up the listener after render
        const name = result.name || "";
        const domain = document.getElementById("domain").value || "";
        const linkedin = document.getElementById("linkedinUrl").value || "";

        // Use a global callback to wire up after innerHTML is set
        window._pendingEnrich = { name, domain, linkedin };

        return `<button class="enrich-btn" id="enrichBtn">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
            </svg>
            Enrich Contact (1 Credit)
        </button>`;
    } else {
        return `<span style="color: var(--text-muted);">Score too low for enrichment (< 60)</span>`;
    }
}

// Wire up enrich button after result is rendered
const resultsObserver = new MutationObserver(() => {
    const enrichBtn = document.getElementById("enrichBtn");
    if (enrichBtn && window._pendingEnrich) {
        const { name, domain, linkedin } = window._pendingEnrich;
        enrichBtn.addEventListener("click", () => {
            handleEnrich(name, domain, linkedin);
        });
        window._pendingEnrich = null;
    }
});
resultsObserver.observe(document.getElementById("resultCard"), { childList: true, subtree: true });

async function handleEnrich(fullName, domain, linkedinUrl) {
    const container = document.getElementById("contactDataContainer");
    container.innerHTML = `<span style="color: var(--text-muted);">
        <div class="loading-spinner" style="width:20px;height:20px;border-width:2px;display:inline-block;vertical-align:middle;margin-right:8px;"></div>
        Enriching via FullEnrich waterfall (15+ vendors)...
    </span>`;

    // Split full name back into first/last for the API
    const parts = fullName.split(" ");
    const firstName = parts[0] || "";
    const lastName = parts.slice(1).join(" ") || "";

    try {
        const response = await fetch("/api/enrich", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                first_name: firstName,
                last_name: lastName,
                domain: domain || "",
                linkedin_url: linkedinUrl || null
            }),
        });

        if (!response.ok) {
            const err = await response.json().catch(() => ({ detail: "Unknown error" }));
            throw new Error(err.detail || `HTTP ${response.status}`);
        }

        const enrichResult = await response.json();

        let html = `<div class="contact-row">`;
        if (enrichResult.email) {
            html += `<div class="contact-item">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="2" y="4" width="20" height="16" rx="2"/><path d="M22 7l-10 7L2 7"/>
                </svg>
                ${esc(enrichResult.email)}
            </div>`;
        }
        if (enrichResult.phone) {
            html += `<div class="contact-item">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 16.92z"/>
                </svg>
                ${esc(enrichResult.phone)}
            </div>`;
        }
        if (!enrichResult.email && !enrichResult.phone) {
            html += `<span style="color: var(--text-muted);">No contact data found</span>`;
        }
        html += `</div>`;

        container.innerHTML = html;

    } catch (error) {
        container.innerHTML = `<span style="color: var(--red);">Enrichment Failed: ${esc(error.message)}</span>`;
    }
}

function buildHooksHTML(hooks) {
    if (!hooks || hooks.length === 0) return "";
    return `<div class="hooks-list">${hooks.map((h) => `<span class="hook-tag">${esc(h)}</span>`).join("")}</div>`;
}

// ── Render Agent Trace ──────────────────────
function renderAgentTrace(result) {
    const tools = result.tools_used || [];
    if (tools.length === 0) {
        traceContent.innerHTML = `
            <div class="trace-empty">
                <p>No tool calls were recorded for this query.</p>
            </div>`;
        return;
    }

    let html = "";

    tools.forEach((tool, i) => {
        html += `
            <div class="trace-step">
                <div class="trace-step-number">${i + 1}</div>
                <div class="trace-step-info">
                    <div class="trace-step-tool">${esc(tool)}</div>
                    <div class="trace-step-detail">${getToolDescription(tool)}</div>
                </div>
            </div>`;
    });

    // Summary
    html += `
            <div class="trace-summary">
                <div class="trace-summary-label">Summary</div>
                <div class="trace-summary-row">
                    <span>Total tool calls</span>
                    <span>${tools.length}</span>
                </div>
            </div>`;

    traceContent.innerHTML = html;

    // Expand trace panel if collapsed
    tracePanel.classList.remove("collapsed");
}

function getToolDescription(tool) {
    const lower = tool.toLowerCase();
    if (lower.includes("linkup_search") && lower.includes("deep"))
        return "Deep multi-source web research for detailed insights";
    if (lower.includes("linkup_search"))
        return "Standard web search for basic prospect info";
    if (lower.includes("linkup_fetch"))
        return "Fetched specific URL content";
    if (lower.includes("enrich_contact"))
        return "Contact enrichment via FullEnrich (15+ vendors)";
    if (lower.includes("check_credits"))
        return "Checked remaining FullEnrich credits";
    return "Tool execution completed";
}

// ── Error Handling ──────────────────────────
function showError(message) {
    errorCard.innerHTML = `<strong>Research Failed</strong> ${esc(message)}`;
    errorSection.style.display = "block";
}

function hideError() {
    errorSection.style.display = "none";
}

function hideResults() {
    resultsSection.style.display = "none";
}

// ── Utilities ───────────────────────────────
function getScoreClass(score) {
    if (score >= 70) return "green";
    if (score >= 50) return "orange";
    return "red";
}

function getInitials(name) {
    if (!name) return "?";
    return name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2);
}

function esc(str) {
    if (!str) return "";
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}
