/**
 * PaisaPilot AI – Core Application Logic
 * Single Page Application Router, CRUD Operations, AI Service Client,
 * Filter Engine, and Theme Management.
 */

const App = {
  currentTab: "dashboard",
  transactions: [],
  summary: null,
  spending: null,
  aiStatus: null,
  activeFilterType: "all",

  categoryIcons: {
    "Food": "🍔",
    "Travel": "🚗",
    "Shopping": "🛍️",
    "Education": "📚",
    "Bills": "⚡",
    "Health": "🩺",
    "Entertainment": "🎬",
    "Salary": "💰",
    "Other": "🏷️"
  },

  async init() {
    this.initTheme();
    this.bindEvents();
    this.setDefaultDate();
    await this.refreshAllData();

    // Check if initial hash is set (e.g. #transactions)
    const hash = window.location.hash.replace("#", "");
    if (["dashboard", "transactions", "analysis", "advisor"].includes(hash)) {
      this.switchTab(hash);
    }
  },

  // -------------------------------------------------------------
  // Theme Management
  // -------------------------------------------------------------
  initTheme() {
    const savedTheme = localStorage.getItem("paisapilot_theme") || "dark";
    document.documentElement.setAttribute("data-theme", savedTheme);
    localStorage.setItem("paisapilot_theme", savedTheme);
    this.updateThemeIcon(savedTheme);
  },

  toggleTheme() {
    const current = document.documentElement.getAttribute("data-theme") || "dark";
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("paisapilot_theme", next);
    this.updateThemeIcon(next);
    ChartManager.updateTheme();
  },

  updateThemeIcon(theme) {
    const iconBtn = document.getElementById("themeToggleBtn");
    if (iconBtn) {
      iconBtn.innerHTML = theme === "dark" 
        ? `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>`
        : `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>`;
    }
  },

  // -------------------------------------------------------------
  // Navigation & Tabs
  // -------------------------------------------------------------
  switchTab(tabId) {
    this.currentTab = tabId;
    window.location.hash = tabId;

    // Update sidebar navigation
    document.querySelectorAll(".nav-item").forEach(item => {
      item.classList.toggle("active", item.getAttribute("data-tab") === tabId);
    });

    // Update tab panes
    document.querySelectorAll(".tab-pane").forEach(pane => {
      pane.classList.toggle("active", pane.id === `tab-${tabId}`);
    });

    // Update page header title
    const titleMap = {
      "dashboard": { title: "Financial Dashboard", subtitle: "Live snapshot of your income, expenses, and savings" },
      "transactions": { title: "Transaction Management", subtitle: "Track, filter, and categorize financial records" },
      "analysis": { title: "Spending Pattern Analysis", subtitle: "Understand your financial distribution and budget benchmarks" },
      "advisor": { title: "AI Savings Advisor", subtitle: "Personalized intelligent recommendations powered by Gemini AI" }
    };

    const header = titleMap[tabId] || titleMap["dashboard"];
    document.getElementById("pageTitle").textContent = header.title;
    document.getElementById("pageSubtitle").textContent = header.subtitle;

    // Trigger tab specific actions
    if (tabId === "analysis") {
      this.renderSpendingSection();
    } else if (tabId === "advisor" && !this.advisorLoaded) {
      this.fetchRecommendations();
    }

    // Close mobile drawer if open
    document.getElementById("sidebar").classList.remove("open");
  },

  // -------------------------------------------------------------
  // Event Listeners
  // -------------------------------------------------------------
  bindEvents() {
    // Navigation items
    document.querySelectorAll(".nav-item").forEach(item => {
      item.addEventListener("click", (e) => {
        e.preventDefault();
        const tab = item.getAttribute("data-tab");
        this.switchTab(tab);
      });
    });

    // Mobile menu button
    const mobileBtn = document.getElementById("mobileMenuBtn");
    if (mobileBtn) {
      mobileBtn.addEventListener("click", () => {
        document.getElementById("sidebar").classList.toggle("open");
      });
    }

    // Theme toggle
    document.getElementById("themeToggleBtn")?.addEventListener("click", () => this.toggleTheme());

    // Add Transaction Modal
    document.getElementById("openAddModalBtn")?.addEventListener("click", () => this.openAddModal());
    document.getElementById("closeAddModalBtn")?.addEventListener("click", () => this.closeAddModal());
    document.getElementById("cancelAddBtn")?.addEventListener("click", () => this.closeAddModal());
    document.getElementById("addTransactionModal")?.addEventListener("click", (e) => {
      if (e.target.id === "addTransactionModal") this.closeAddModal();
    });

    // Transaction Type Radio selection
    document.querySelectorAll(".type-radio-label").forEach(label => {
      label.addEventListener("click", () => {
        document.querySelectorAll(".type-radio-label").forEach(l => l.classList.remove("checked"));
        label.classList.add("checked");
        const radio = label.querySelector("input[type='radio']");
        if (radio) radio.checked = true;
      });
    });

    // Transaction form submission
    document.getElementById("addTransactionForm")?.addEventListener("submit", (e) => this.handleAddTransaction(e));

    // AI Categorize Button in form
    document.getElementById("aiCategorizeBtn")?.addEventListener("click", () => this.triggerAiCategorize());

    // Auto-detect category on description blur if description has at least 3 chars
    const descInput = document.getElementById("txDescription");
    descInput?.addEventListener("blur", () => {
      if (descInput.value.trim().length >= 3) {
        this.triggerAiCategorize(false); // subtle auto-detect without noisy error
      }
    });

    // Search and Filters
    document.getElementById("txSearch")?.addEventListener("input", this.debounce(() => this.filterTransactions(), 250));
    document.getElementById("txCategoryFilter")?.addEventListener("change", () => this.filterTransactions());
    document.getElementById("txSort")?.addEventListener("change", () => this.filterTransactions());

    // Filter Type buttons
    document.querySelectorAll(".type-toggle-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".type-toggle-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        this.activeFilterType = btn.getAttribute("data-type");
        this.filterTransactions();
      });
    });

    // Reset Sample Data
    document.getElementById("resetDataBtn")?.addEventListener("click", () => this.handleResetData());

    // API Key Modal
    document.getElementById("aiStatusPill")?.addEventListener("click", () => this.openApiKeyModal());
    document.getElementById("closeApiKeyModalBtn")?.addEventListener("click", () => this.closeApiKeyModal());
    document.getElementById("apiKeyModal")?.addEventListener("click", (e) => {
      if (e.target.id === "apiKeyModal") this.closeApiKeyModal();
    });
    document.getElementById("saveApiKeyBtn")?.addEventListener("click", () => this.handleSaveApiKey());

    // AI Advisor Refresh Button
    document.getElementById("generateAiAdviceBtn")?.addEventListener("click", () => this.fetchRecommendations(true));
  },

  setDefaultDate() {
    const dateInput = document.getElementById("txDate");
    if (dateInput) {
      dateInput.value = new Date().toISOString().split("T")[0];
    }
  },

  // -------------------------------------------------------------
  // Data Fetching & Sync
  // -------------------------------------------------------------
  async refreshAllData() {
    try {
      await Promise.all([
        this.fetchStatus(),
        this.fetchSummary(),
        this.fetchTransactions(),
        this.fetchSpending()
      ]);
      // Keep spending analysis & charts automatically synchronized (Requirement 5)
      this.renderSpendingSection();
      // Invalidate cached recommendations flag so switching to advisor uses updated data
      this.advisorLoaded = false;
    } catch (err) {
      console.error("Failed to load initial data:", err);
      this.showToast("Error loading financial data.", "error");
    }
  },

  async fetchStatus() {
    const res = await fetch("/api/status");
    const data = await res.json();
    this.aiStatus = data.ai;
    this.updateAiStatusBadge();
  },

  updateAiStatusBadge() {
    const pill = document.getElementById("aiStatusPill");
    if (!pill || !this.aiStatus) return;

    pill.className = `ai-status-pill ${this.aiStatus.badge_class}`;
    pill.innerHTML = `
      <span class="status-dot"></span>
      <span>${this.aiStatus.badge_text}</span>
    `;
    pill.title = `${this.aiStatus.engine} – Click to configure API Key`;
  },

  async fetchSummary() {
    const res = await fetch("/api/summary");
    this.summary = await res.json();
    this.renderDashboardSummary();
  },

  renderDashboardSummary() {
    if (!this.summary) return;

    // Currency values
    document.getElementById("dashTotalIncome").textContent = this.formatINR(this.summary.total_income);
    document.getElementById("dashTotalExpenses").textContent = this.formatINR(this.summary.total_expenses);
    document.getElementById("dashAvailableBalance").textContent = this.formatINR(this.summary.available_balance);
    document.getElementById("dashMonthlySavings").textContent = this.formatINR(this.summary.monthly_savings);

    // Savings rate badge
    const rateEl = document.getElementById("dashSavingsRateBadge");
    if (rateEl) {
      rateEl.textContent = `${this.summary.savings_rate}% Savings Rate`;
      rateEl.className = `badge-rate ${this.summary.health_color}`;
    }

    // Health status label
    const healthStatusEl = document.getElementById("dashHealthStatus");
    if (healthStatusEl) {
      healthStatusEl.textContent = `Status: ${this.summary.health_status}`;
    }

    // Quick AI Snapshot Text
    const snapshotEl = document.getElementById("aiSnapshotText");
    if (snapshotEl) {
      if (this.summary.total_income === 0 && this.summary.total_expenses === 0) {
        snapshotEl.textContent = "Welcome to PaisaPilot AI! Add your first income or expense transaction to unlock real-time financial tracking.";
      } else if (this.summary.available_balance < 0) {
        snapshotEl.innerHTML = `<strong>Attention Required:</strong> Expenses exceed income by <strong>${this.formatINR(Math.abs(this.summary.available_balance))}</strong>. Review discretionary expenses in the AI Advisor.`;
      } else {
        snapshotEl.innerHTML = `You have saved <strong>${this.summary.savings_rate}%</strong> of your income so far! Available liquidity stands at <strong>${this.formatINR(this.summary.available_balance)}</strong>.`;
      }
    }
  },

  async fetchTransactions() {
    const res = await fetch("/api/transactions?sort=date_desc");
    const data = await res.json();
    this.transactions = data.transactions || [];
    this.renderTransactionsTable(this.transactions);
    this.renderRecentTransactions();
  },

  async fetchSpending() {
    const res = await fetch("/api/spending");
    this.spending = await res.json();
    
    // Render Dashboard Charts
    ChartManager.renderDashboardIncomeExpense(this.summary);
    ChartManager.renderDashboardCategoryDoughnut(this.spending.categories);

    // Also fetch timeline for richer chart if available
    try {
      const timeRes = await fetch("/api/timeline");
      const timeData = await timeRes.json();
      if (timeData.timeline && timeData.timeline.length > 0) {
        ChartManager.renderDashboardIncomeExpense(this.summary, timeData.timeline);
      }
    } catch (e) {
      console.warn("Timeline fetch error:", e);
    }
  },

  // -------------------------------------------------------------
  // Transactions Management UI
  // -------------------------------------------------------------
  renderTransactionsTable(items) {
    const tbody = document.getElementById("transactionsTableBody");
    const emptyState = document.getElementById("txEmptyState");
    const countBadge = document.getElementById("txFilteredCount");

    if (!tbody) return;
    tbody.innerHTML = "";

    if (countBadge) {
      countBadge.textContent = `${items.length} Transaction${items.length === 1 ? '' : 's'}`;
    }

    if (!items || items.length === 0) {
      emptyState.style.display = "block";
      return;
    }
    emptyState.style.display = "none";

    items.forEach(tx => {
      const tr = document.createElement("tr");
      const icon = this.categoryIcons[tx.category] || "🏷️";
      const isIncome = tx.type === "income";
      const formattedAmount = (isIncome ? "+ " : "- ") + this.formatINR(tx.amount);
      const amountClass = isIncome ? "amount-income" : "amount-expense";

      tr.innerHTML = `
        <td style="color: var(--text-muted); font-size: 0.82rem; white-space: nowrap;">${this.formatDate(tx.date)}</td>
        <td style="font-weight: 600;">${this.escapeHtml(tx.description)}</td>
        <td>
          <span class="category-badge category-${tx.category}">
            <span>${icon}</span>
            <span>${tx.category}</span>
          </span>
        </td>
        <td>
          <span class="badge-rate ${isIncome ? 'success' : 'danger'}">
            ${isIncome ? 'Income' : 'Expense'}
          </span>
        </td>
        <td class="${amountClass}" style="text-align: right; white-space: nowrap;">
          ${formattedAmount}
        </td>
        <td style="text-align: center;">
          <button class="delete-btn" title="Delete Transaction" onclick="App.handleDeleteTransaction(${tx.id})">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6"></polyline>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
            </svg>
          </button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  },

  renderRecentTransactions() {
    const tbody = document.getElementById("dashRecentTableBody");
    if (!tbody) return;
    tbody.innerHTML = "";

    const recent = this.transactions.slice(0, 5);
    if (recent.length === 0) {
      tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; padding: 24px; color: var(--text-muted);">No transactions recorded yet.</td></tr>`;
      return;
    }

    recent.forEach(tx => {
      const tr = document.createElement("tr");
      const icon = this.categoryIcons[tx.category] || "🏷️";
      const isIncome = tx.type === "income";
      const formattedAmount = (isIncome ? "+ " : "- ") + this.formatINR(tx.amount);
      const amountClass = isIncome ? "amount-income" : "amount-expense";

      tr.innerHTML = `
        <td style="font-weight: 600;">${this.escapeHtml(tx.description)}</td>
        <td>
          <span class="category-badge category-${tx.category}">
            <span>${icon}</span>
            <span>${tx.category}</span>
          </span>
        </td>
        <td style="color: var(--text-muted); font-size: 0.8rem;">${this.formatDate(tx.date)}</td>
        <td class="${amountClass}" style="text-align: right;">${formattedAmount}</td>
      `;
      tbody.appendChild(tr);
    });
  },

  filterTransactions() {
    const search = document.getElementById("txSearch")?.value.toLowerCase().trim() || "";
    const category = document.getElementById("txCategoryFilter")?.value || "";
    const sort = document.getElementById("txSort")?.value || "date_desc";

    let filtered = [...this.transactions];

    // Filter by type
    if (this.activeFilterType !== "all") {
      filtered = filtered.filter(t => t.type === this.activeFilterType);
    }

    // Filter by category
    if (category) {
      filtered = filtered.filter(t => t.category === category);
    }

    // Filter by search
    if (search) {
      filtered = filtered.filter(t => 
        t.description.toLowerCase().includes(search) || 
        t.category.toLowerCase().includes(search)
      );
    }

    // Sort
    if (sort === "date_asc") {
      filtered.sort((a, b) => new Date(a.date) - new Date(b.date));
    } else if (sort === "date_desc") {
      filtered.sort((a, b) => new Date(b.date) - new Date(a.date));
    } else if (sort === "amount_desc") {
      filtered.sort((a, b) => b.amount - a.amount);
    } else if (sort === "amount_asc") {
      filtered.sort((a, b) => a.amount - b.amount);
    }

    this.renderTransactionsTable(filtered);
  },

  // -------------------------------------------------------------
  // Add Transaction Modal & AI Categorization
  // -------------------------------------------------------------
  openAddModal() {
    const modal = document.getElementById("addTransactionModal");
    if (!modal) return;
    this.setDefaultDate();
    document.getElementById("txDescription").value = "";
    document.getElementById("txAmount").value = "";
    document.getElementById("txCategory").value = "Other";
    document.getElementById("aiCategorizeNote").textContent = "";

    // Reset radio to expense
    document.querySelectorAll(".type-radio-label").forEach(l => l.classList.remove("checked"));
    const expLabel = document.querySelector(".type-radio-label.expense-label");
    if (expLabel) {
      expLabel.classList.add("checked");
      expLabel.querySelector("input").checked = true;
    }

    modal.classList.add("open");
    setTimeout(() => document.getElementById("txDescription").focus(), 100);
  },

  closeAddModal() {
    document.getElementById("addTransactionModal")?.classList.remove("open");
  },

  async triggerAiCategorize(showToastOnSuccess = true) {
    const descInput = document.getElementById("txDescription");
    const noteEl = document.getElementById("aiCategorizeNote");
    const catSelect = document.getElementById("txCategory");
    const btn = document.getElementById("aiCategorizeBtn");

    const description = descInput?.value.trim();
    if (!description) {
      if (showToastOnSuccess) this.showToast("Please enter a transaction description first.", "info");
      return;
    }

    if (btn) btn.disabled = true;
    if (noteEl) noteEl.innerHTML = `<span>✨ Categorizing with AI...</span>`;

    try {
      const res = await fetch("/api/categorize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ description })
      });
      const data = await res.json();

      if (data.category && catSelect) {
        catSelect.value = data.category;
        
        const isLive = !data.is_fallback;
        const sourceLabel = isLive ? "Gemini AI" : "Rule-Based Engine";
        const icon = this.categoryIcons[data.category] || "🏷️";

        noteEl.innerHTML = `<span style="color: var(--primary); font-weight: 600;">✨ Auto-selected ${icon} ${data.category} via ${sourceLabel} (${data.reasoning || 'Matched pattern'})</span>`;
        if (showToastOnSuccess) {
          this.showToast(`AI categorized as '${data.category}'`, "info");
        }
      }
    } catch (err) {
      console.error("AI Categorize error:", err);
      if (noteEl) noteEl.textContent = "";
    } finally {
      if (btn) btn.disabled = false;
    }
  },

  async handleAddTransaction(e) {
    e.preventDefault();
    const description = document.getElementById("txDescription").value.trim();
    const amount = parseFloat(document.getElementById("txAmount").value);
    const date = document.getElementById("txDate").value;
    const category = document.getElementById("txCategory").value;
    const typeRadio = document.querySelector("input[name='txType']:checked");
    const type = typeRadio ? typeRadio.value : "expense";

    if (!description) {
      this.showToast("Description is required.", "error");
      return;
    }

    if (isNaN(amount) || amount <= 0) {
      this.showToast("Please enter a valid positive amount.", "error");
      return;
    }

    try {
      const res = await fetch("/api/transactions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ description, amount, date, type, category })
      });
      const data = await res.json();

      if (data.success) {
        this.closeAddModal();
        this.showToast("Transaction added successfully!", "success");
        await this.refreshAllData();
      } else {
        this.showToast(data.error || "Failed to add transaction.", "error");
      }
    } catch (err) {
      this.showToast("Network error while adding transaction.", "error");
    }
  },

  async handleDeleteTransaction(txId) {
    if (!confirm(`Are you sure you want to delete transaction #${txId}?`)) {
      return;
    }

    try {
      const res = await fetch(`/api/transactions/${txId}`, { method: "DELETE" });
      const data = await res.json();
      if (data.success) {
        this.showToast(data.message, "success");
        await this.refreshAllData();
      } else {
        this.showToast(data.error || "Could not delete transaction.", "error");
      }
    } catch (err) {
      this.showToast("Error deleting transaction.", "error");
    }
  },

  async handleResetData() {
    if (!confirm("Reset database to initial sample college transactions? All custom records will be replaced with realistic demo data.")) {
      return;
    }

    try {
      const res = await fetch("/api/reset", { method: "POST" });
      const data = await res.json();
      if (data.success) {
        this.showToast(data.message, "success");
        await this.refreshAllData();
      }
    } catch (err) {
      this.showToast("Error resetting sample data.", "error");
    }
  },

  // -------------------------------------------------------------
  // Spending Analysis UI
  // -------------------------------------------------------------
  renderSpendingSection() {
    if (!this.spending) return;

    const topCat = this.spending.highest_spending_category;
    document.getElementById("topSpendCatName").textContent = topCat.category || "None";
    document.getElementById("topSpendAmount").textContent = this.formatINR(topCat.amount);
    document.getElementById("topSpendPct").textContent = `${topCat.percentage}% of total expenses`;

    // Discretionary calculation
    const budget = this.spending.budget_breakdown;
    document.getElementById("analysisNeedsPct").textContent = `${budget.needs.percentage}% (${this.formatINR(budget.needs.amount)})`;
    document.getElementById("analysisWantsPct").textContent = `${budget.wants.percentage}% (${this.formatINR(budget.wants.amount)})`;
    document.getElementById("analysisSavingsPct").textContent = `${budget.savings.percentage}% (${this.formatINR(budget.savings.amount)})`;

    // Progress bar fills
    document.getElementById("fillNeeds").style.width = `${Math.min(100, budget.needs.percentage)}%`;
    document.getElementById("fillWants").style.width = `${Math.min(100, budget.wants.percentage)}%`;
    document.getElementById("fillSavings").style.width = `${Math.min(100, budget.savings.percentage)}%`;

    // Category progress list
    const listEl = document.getElementById("categoryBreakdownList");
    if (listEl) {
      listEl.innerHTML = "";
      if (this.spending.categories.length === 0) {
        listEl.innerHTML = `<p style="color:var(--text-muted); font-size:0.88rem;">No expense categories recorded yet.</p>`;
      } else {
        this.spending.categories.forEach(c => {
          const icon = this.categoryIcons[c.category] || "🏷️";
          const row = document.createElement("div");
          row.className = "cat-item-row";
          row.innerHTML = `
            <div class="cat-item-info">
              <span class="cat-item-title">
                <span>${icon}</span>
                <span>${c.category}</span>
                <span style="color:var(--text-muted); font-size:0.75rem;">(${c.count} tx)</span>
              </span>
              <span class="cat-item-amount">${this.formatINR(c.amount)} <span style="color:var(--text-muted); font-weight:500;">(${c.percentage}%)</span></span>
            </div>
            <div class="budget-progress-track">
              <div class="budget-progress-fill" style="width: ${c.percentage}%; background-color: ${ChartManager.categoryColors[c.category] || '#6C5CE7'};"></div>
            </div>
          `;
          listEl.appendChild(row);
        });
      }
    }

    // Render Analysis Charts
    ChartManager.renderAnalysisDoughnut(this.spending.categories);
    ChartManager.renderAnalysisBarChart(this.spending.categories);
  },

  // -------------------------------------------------------------
  // AI Savings Advisor UI
  // -------------------------------------------------------------
  async fetchRecommendations(force = false) {
    const btn = document.getElementById("generateAiAdviceBtn");
    const container = document.getElementById("aiRecommendationsContainer");
    if (btn) btn.disabled = true;

    if (container) {
      container.innerHTML = `
        <div style="text-align: center; padding: 48px 24px; color: var(--text-muted);">
          <div class="status-dot" style="width: 14px; height: 14px; margin: 0 auto 16px auto; background-color: var(--primary);"></div>
          <h4 style="color: var(--text-main); margin-bottom: 6px;">Analyzing Your Financial Records...</h4>
          <p style="font-size: 0.88rem;">Evaluating category distributions, savings velocity, and generating personalized advice.</p>
        </div>
      `;
    }

    try {
      const res = await fetch("/api/recommendations", { method: "POST" });
      const data = await res.json();
      this.advisorLoaded = true;
      this.renderAdvisorResults(data.recommendations);
    } catch (err) {
      console.error("Advisor Error:", err);
      if (container) {
        container.innerHTML = `<p style="color: var(--danger); text-align: center;">Error generating recommendations.</p>`;
      }
    } finally {
      if (btn) btn.disabled = false;
    }
  },

  renderAdvisorResults(recs) {
    const container = document.getElementById("aiRecommendationsContainer");
    if (!container || !recs) return;

    const isFallback = recs.is_fallback;
    const engineTag = isFallback
      ? `<span class="engine-pill" style="color: #B45309; background-color: var(--warning-light);"><span class="status-dot" style="display:inline-block; width:6px; height:6px; margin-right:4px;"></span> ${recs.engine}</span>`
      : `<span class="engine-pill" style="color: var(--success); background-color: var(--success-light);"><span class="status-dot" style="display:inline-block; width:6px; height:6px; margin-right:4px;"></span> ${recs.engine}</span>`;

    let tipsHtml = "";
    if (recs.recommendations && recs.recommendations.length > 0) {
      recs.recommendations.forEach(tip => {
        const impactClass = tip.impact ? `impact-${tip.impact.toLowerCase()}` : "impact-medium";
        const icon = this.categoryIcons[tip.category] || "💡";
        tipsHtml += `
          <div class="tip-card">
            <div class="tip-card-header">
              <span class="category-badge category-${tip.category || 'Other'}">
                <span>${icon}</span>
                <span>${tip.category || 'General'}</span>
              </span>
              <span class="impact-badge ${impactClass}">${tip.impact || 'Actionable'}</span>
            </div>
            <div class="tip-title">${this.escapeHtml(tip.title)}</div>
            <div class="tip-desc">${this.escapeHtml(tip.description)}</div>
          </div>
        `;
      });
    }

    container.innerHTML = `
      <div class="ai-advisor-results">
        <!-- Score & Verdict Row -->
        <div class="ai-summary-card-row">
          <div class="health-score-card">
            <div class="score-circle">
              <span class="score-number">${recs.score || 80}</span>
              <span class="score-label">Score / 100</span>
            </div>
            <span class="score-rating-badge">${recs.rating || 'Healthy'}</span>
          </div>

          <div class="verdict-card">
            <div class="verdict-header">
              <h3 style="font-size: 1.1rem; font-weight: 700;">Executive Financial Verdict</h3>
              ${engineTag}
            </div>
            <p class="verdict-body">${this.escapeHtml(recs.executive_summary || '')}</p>
            
            <div class="savings-potential-banner">
              <span>Estimated Achievable Monthly Savings</span>
              <span class="savings-potential-amount">+ ${this.formatINR(recs.potential_monthly_savings || 0)}</span>
            </div>
          </div>
        </div>

        <!-- 30-Day Savings Challenge -->
        ${recs.monthly_challenge ? `
          <div class="challenge-box">
            <div class="challenge-icon">🎯</div>
            <div class="challenge-content">
              <h4>Recommended 30-Day Savings Challenge</h4>
              <p>${this.escapeHtml(recs.monthly_challenge)}</p>
            </div>
          </div>
        ` : ''}

        <!-- Recommendations Grid -->
        <div>
          <h3 style="font-size: 1.15rem; font-weight: 700; margin-bottom: 16px;">Tailored Action Steps</h3>
          <div class="tips-grid">
            ${tipsHtml}
          </div>
        </div>
      </div>
    `;
  },

  // -------------------------------------------------------------
  // API Key Management Modal
  // -------------------------------------------------------------
  openApiKeyModal() {
    const modal = document.getElementById("apiKeyModal");
    if (!modal) return;
    const desc = document.getElementById("apiKeyEngineDesc");
    if (desc && this.aiStatus) {
      desc.textContent = `Current Mode: ${this.aiStatus.engine}`;
    }
    modal.classList.add("open");
  },

  closeApiKeyModal() {
    document.getElementById("apiKeyModal")?.classList.remove("open");
  },

  async handleSaveApiKey() {
    const input = document.getElementById("geminiApiKeyInput");
    const key = input ? input.value.trim() : "";
    const saveBtn = document.getElementById("saveApiKeyBtn");

    if (saveBtn) saveBtn.disabled = true;

    try {
      const res = await fetch("/api/update-api-key", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ api_key: key })
      });
      const data = await res.json();
      this.aiStatus = data.ai;
      this.updateAiStatusBadge();
      this.closeApiKeyModal();
      this.showToast(data.message, "success");

      // Reload recommendations with fresh engine
      if (this.currentTab === "advisor") {
        this.fetchRecommendations(true);
      }
    } catch (err) {
      this.showToast("Error updating API configuration.", "error");
    } finally {
      if (saveBtn) saveBtn.disabled = false;
    }
  },

  // -------------------------------------------------------------
  // Utilities & Helpers
  // -------------------------------------------------------------
  formatINR(amount) {
    return "₹" + Number(amount || 0).toLocaleString("en-IN", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  },

  formatDate(dateStr) {
    if (!dateStr) return "";
    try {
      const [year, month, day] = dateStr.split("-");
      const d = new Date(year, month - 1, day);
      return d.toLocaleDateString("en-IN", { month: "short", day: "numeric", year: "numeric" });
    } catch (e) {
      return dateStr;
    }
  },

  escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  },

  debounce(func, wait) {
    let timeout;
    return (...args) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(this, args), wait);
    };
  },

  showToast(message, type = "info") {
    const container = document.getElementById("toastContainer");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.textContent = message;

    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateX(100%)";
      toast.style.transition = "all 0.3s ease";
      setTimeout(() => toast.remove(), 300);
    }, 3200);
  }
};

// Expose globally for inline onclick handlers
window.App = App;

// Auto-run on DOM ready
document.addEventListener("DOMContentLoaded", () => App.init());

