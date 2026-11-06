/**
 * PaisaPilot AI – Charts Engine
 * Configures and updates Chart.js instances for:
 * 1. Income vs Expense visualizer
 * 2. Category spending doughnut
 * 3. Spending analysis bar & doughnut
 * Supports dynamic light/dark mode color updates.
 */

const ChartManager = {
  charts: {},

  // Category color palette matching our design system
  categoryColors: {
    "Food": "#F97316",          // Orange
    "Travel": "#3B82F6",        // Blue
    "Shopping": "#EC4899",      // Pink
    "Education": "#6366F1",     // Indigo
    "Bills": "#F59E0B",         // Amber
    "Health": "#10B981",        // Emerald
    "Entertainment": "#8B5CF6", // Purple
    "Salary": "#22C55E",        // Green
    "Other": "#94A3B8"          // Slate Grey
  },

  getThemeColors() {
    const isDark = document.documentElement.getAttribute("data-theme") === "dark";
    return {
      textColor: isDark ? "#A0AEC0" : "#64748B",
      headingColor: isDark ? "#F8FAFC" : "#0F172A",
      gridColor: isDark ? "rgba(255, 255, 255, 0.08)" : "rgba(15, 23, 42, 0.06)",
      cardBg: isDark ? "#131B2E" : "#FFFFFF"
    };
  },

  formatINR(amount) {
    return "₹" + Number(amount || 0).toLocaleString("en-IN", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  },

  /**
   * Initializes or updates the Dashboard Income vs Expense chart.
   */
  renderDashboardIncomeExpense(summary, timeline = []) {
    const ctx = document.getElementById("dashIncomeExpenseChart");
    if (!ctx) return;

    const theme = this.getThemeColors();
    if (this.charts.dashIncomeExpense) {
      this.charts.dashIncomeExpense.destroy();
    }

    // If timeline exists and has > 1 month, show monthly; otherwise show current summary
    let labels = [];
    let incomeData = [];
    let expenseData = [];

    if (timeline && timeline.length > 0) {
      labels = timeline.map(t => t.month);
      incomeData = timeline.map(t => t.income);
      expenseData = timeline.map(t => t.expense);
    } else {
      labels = ["Current Period"];
      incomeData = [summary.total_income];
      expenseData = [summary.total_expenses];
    }

    this.charts.dashIncomeExpense = new Chart(ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Total Income",
            data: incomeData,
            backgroundColor: "#10B981",
            borderRadius: 8,
            maxBarThickness: 36
          },
          {
            label: "Total Expenses",
            data: expenseData,
            backgroundColor: "#EF4444",
            borderRadius: 8,
            maxBarThickness: 36
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "top",
            labels: {
              color: theme.headingColor,
              font: { family: "'Plus Jakarta Sans', sans-serif", weight: "600", size: 12 },
              usePointStyle: true,
              boxWidth: 8
            }
          },
          tooltip: {
            callbacks: {
              label: (context) => ` ${context.dataset.label}: ${this.formatINR(context.raw)}`
            }
          }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { color: theme.textColor, font: { family: "'Plus Jakarta Sans', sans-serif" } }
          },
          y: {
            grid: { color: theme.gridColor },
            ticks: {
              color: theme.textColor,
              font: { family: "'Plus Jakarta Sans', sans-serif" },
              callback: (val) => "₹" + Number(val).toLocaleString("en-IN")
            }
          }
        }
      }
    });
  },

  /**
   * Initializes or updates the Dashboard Category Doughnut.
   */
  renderDashboardCategoryDoughnut(categories = []) {
    const ctx = document.getElementById("dashCategoryDoughnut");
    if (!ctx) return;

    const theme = this.getThemeColors();
    if (this.charts.dashCategoryDoughnut) {
      this.charts.dashCategoryDoughnut.destroy();
    }

    if (!categories || categories.length === 0) {
      this.charts.dashCategoryDoughnut = new Chart(ctx, {
        type: "doughnut",
        data: {
          labels: ["No Expenses Recorded"],
          datasets: [{
            data: [1],
            backgroundColor: [theme.cardBg === "#FFFFFF" ? "#E2E8F0" : "#23304C"],
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: "70%",
          plugins: {
            legend: {
              position: "bottom",
              labels: {
                color: theme.textColor,
                font: { family: "'Plus Jakarta Sans', sans-serif", size: 11 },
                usePointStyle: true,
                boxWidth: 8
              }
            },
            tooltip: { enabled: false }
          }
        }
      });
      return;
    }

    const labels = categories.map(c => c.category);
    const data = categories.map(c => c.amount);
    const bgColors = categories.map(c => this.categoryColors[c.category] || "#94A3B8");

    this.charts.dashCategoryDoughnut = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: labels,
        datasets: [{
          data: data,
          backgroundColor: bgColors,
          borderWidth: 2,
          borderColor: theme.cardBg,
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: "70%",
        plugins: {
          legend: {
            position: "bottom",
            labels: {
              color: theme.headingColor,
              font: { family: "'Plus Jakarta Sans', sans-serif", size: 11, weight: "500" },
              usePointStyle: true,
              boxWidth: 8,
              padding: 12
            }
          },
          tooltip: {
            callbacks: {
              label: (context) => {
                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                const pct = total > 0 ? ((context.raw / total) * 100).toFixed(1) : 0;
                return ` ${context.label}: ${this.formatINR(context.raw)} (${pct}%)`;
              }
            }
          }
        }
      }
    });
  },

  /**
   * Initializes or updates the Spending Analysis Category Doughnut.
   */
  renderAnalysisDoughnut(categories = []) {
    const ctx = document.getElementById("analysisDoughnutChart");
    if (!ctx) return;

    const theme = this.getThemeColors();
    if (this.charts.analysisDoughnut) {
      this.charts.analysisDoughnut.destroy();
    }

    if (!categories || categories.length === 0) {
      this.charts.analysisDoughnut = new Chart(ctx, {
        type: "doughnut",
        data: {
          labels: ["No Expenses Recorded"],
          datasets: [{
            data: [1],
            backgroundColor: [theme.cardBg === "#FFFFFF" ? "#E2E8F0" : "#23304C"],
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: "65%",
          plugins: {
            legend: {
              position: "bottom",
              labels: {
                color: theme.textColor,
                font: { family: "'Plus Jakarta Sans', sans-serif", size: 11 },
                usePointStyle: true,
                boxWidth: 8
              }
            },
            tooltip: { enabled: false }
          }
        }
      });
      return;
    }

    const labels = categories.map(c => c.category);
    const data = categories.map(c => c.amount);
    const bgColors = categories.map(c => this.categoryColors[c.category] || "#94A3B8");

    this.charts.analysisDoughnut = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: labels,
        datasets: [{
          data: data,
          backgroundColor: bgColors,
          borderWidth: 2,
          borderColor: theme.cardBg,
          hoverOffset: 8
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: "65%",
        plugins: {
          legend: {
            position: "bottom",
            labels: {
              color: theme.headingColor,
              font: { family: "'Plus Jakarta Sans', sans-serif", size: 11, weight: "500" },
              usePointStyle: true,
              boxWidth: 8,
              padding: 12
            }
          },
          tooltip: {
            callbacks: {
              label: (context) => {
                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                const pct = total > 0 ? ((context.raw / total) * 100).toFixed(1) : 0;
                return ` ${context.label}: ${this.formatINR(context.raw)} (${pct}%)`;
              }
            }
          }
        }
      }
    });
  },

  /**
   * Initializes or updates the Spending Analysis Horizontal Bar Chart.
   */
  renderAnalysisBarChart(categories = []) {
    const ctx = document.getElementById("analysisBarChart");
    if (!ctx) return;

    const theme = this.getThemeColors();
    if (this.charts.analysisBar) {
      this.charts.analysisBar.destroy();
    }

    if (!categories || categories.length === 0) {
      this.charts.analysisBar = new Chart(ctx, {
        type: "bar",
        data: {
          labels: ["No Expenses Recorded"],
          datasets: [{
            data: [0],
            backgroundColor: ["#94A3B8"],
            borderRadius: 6
          }]
        },
        options: {
          indexAxis: "y",
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { grid: { color: theme.gridColor }, ticks: { color: theme.textColor } },
            y: { grid: { display: false }, ticks: { color: theme.textColor } }
          }
        }
      });
      return;
    }

    // Sort categories descending by amount
    const sorted = [...categories].sort((a, b) => b.amount - a.amount);
    const labels = sorted.map(c => c.category);
    const data = sorted.map(c => c.amount);
    const bgColors = sorted.map(c => this.categoryColors[c.category] || "#94A3B8");

    this.charts.analysisBar = new Chart(ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [{
          label: "Total Spent",
          data: data,
          backgroundColor: bgColors,
          borderRadius: 6,
          maxBarThickness: 24
        }]
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (context) => ` Spent: ${this.formatINR(context.raw)}`
            }
          }
        },
        scales: {
          x: {
            grid: { color: theme.gridColor },
            ticks: {
              color: theme.textColor,
              font: { family: "'Plus Jakarta Sans', sans-serif" },
              callback: (val) => "₹" + Number(val).toLocaleString("en-IN")
            }
          },
          y: {
            grid: { display: false },
            ticks: { color: theme.headingColor, font: { family: "'Plus Jakarta Sans', sans-serif", weight: "600" } }
          }
        }
      }
    });
  },

  /**
   * Re-renders all charts to adapt to light/dark mode switch.
   */
  updateTheme() {
    Object.values(this.charts).forEach(chart => {
      if (chart) {
        const theme = this.getThemeColors();
        if (chart.options.scales?.x) {
          if (chart.options.scales.x.ticks) chart.options.scales.x.ticks.color = theme.textColor;
        }
        if (chart.options.scales?.y) {
          if (chart.options.scales.y.ticks) chart.options.scales.y.ticks.color = theme.textColor;
          if (chart.options.scales.y.grid) chart.options.scales.y.grid.color = theme.gridColor;
        }
        if (chart.options.plugins?.legend?.labels) {
          chart.options.plugins.legend.labels.color = theme.headingColor;
        }
        if (chart.data.datasets) {
          chart.data.datasets.forEach(ds => {
            if (ds.borderColor) ds.borderColor = theme.cardBg;
          });
        }
        chart.update();
      }
    });
  }
};

