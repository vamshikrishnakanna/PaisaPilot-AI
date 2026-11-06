# PaisaPilot AI – AI-Powered Personal Finance Management System

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1%2B-lightgrey.svg)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-blue.svg)](https://www.sqlite.org/)
[![Google Gemini](https://img.shields.io/badge/AI-Google%20Gemini%202.5%20Flash-blueviolet.svg)](https://aistudio.google.com/)
[![Chart.js](https://img.shields.io/badge/Visuals-Chart.js%204.4-orange.svg)](https://www.chartjs.org/)
[![License](https://img.shields.io/badge/Project-Academic%20CIA--2-purple.svg)]()

> **College Assignment:** AI for Finance CIA-2  
> **Course:** AI-Powered Personal Finance Management System  
> **Developer:** Full-Stack & AI Application Engineer

---

## 📌 1. Project Overview

**PaisaPilot AI** is a professional, full-stack personal finance web application designed to help young earners and college students master their cash flow. It combines a sleek, fintech-inspired dashboard with the **Google Gemini API** to automate tedious transaction categorization and produce data-driven, personalized savings advice.

### Key Capabilities:
- 📊 **Dynamic Financial Dashboard:** Real-time metrics for Total Income, Total Expenses, Available Balance, and Monthly Savings calculated dynamically from SQLite database records.
- 💳 **Transaction Management:** Add, filter, search, sort, and delete income and expense entries with Indian Rupee (₹) formatting.
- ✨ **AI Transaction Categorization:** Automatically maps transaction descriptions (e.g., `Swiggy ₹350` → Food, `Uber ₹200` → Travel) into 9 standardized categories using Google Gemini AI.
- 📈 **Spending Pattern Analysis:** Category breakdown doughnut and ranking bar charts, highest spending highlight, and a 50/30/20 budget benchmark check.
- 💡 **AI Savings Advisor:** Analyzes actual database records to calculate a Financial Health Score (0–100), identify cost leaks, and generate realistic monthly rupee savings targets.
- 🛡️ **Dual-Engine Architecture (Fault-Tolerant):** Operates seamlessly with live Google Gemini 2.5 Flash when an API key is provided, or in a transparently labeled deterministic rule-based fallback mode when offline.
- 🌙 **Modern Design & Dark Mode:** Responsive purple, white, and light-grey fintech aesthetic with a persistent dark mode toggle.

---

## 🛠️ 2. Technology Stack

- **Frontend:** HTML5, CSS3 (Modern custom variables, responsive grid, rounded cards), Vanilla JavaScript (ES6+).
- **Backend:** Python with Flask.
- **Database:** SQLite (`finance.db`) with atomic relational queries and aggregations.
- **AI Integration:** Google Gemini API (`google-genai` SDK) targeting `gemini-2.5-flash`.
- **Data Visualizations:** Chart.js 4.4 for dynamic responsive charts.
- **Export Formats:** CSV, JSON, and PowerPoint presentation (`.pptx`).

---

## 📂 3. Directory Structure

```
PaisaPilot_AI/
├── .env.example                     # Environment template
├── .env                             # Environment configuration (API key)
├── .gitignore                       # Git ignore rules
├── requirements.txt                 # Python package dependencies
├── app.py                           # Flask backend entry point & REST API
├── database.py                      # SQLite database schema, CRUD & aggregation logic
├── ai_service.py                    # Gemini API client & deterministic fallback engine
├── generate_presentation.py         # Script generating PowerPoint presentation
├── PaisaPilot_AI_Presentation.pptx  # 10-slide professional presentation
├── PROJECT_REPORT.md                # Comprehensive academic CIA-2 project report
├── sample_transactions.json         # Realistic fictional sample dataset (JSON)
├── sample_transactions.csv          # Realistic fictional sample dataset (CSV)
├── static/
│   ├── css/
│   │   └── style.css                # Premium purple/white/light-grey stylesheet & dark mode
│   └── js/
│       ├── app.js                   # Application controller, modal handling, CRUD & filters
│       └── charts.js                # Chart.js initialization & dynamic theme adapters
└── templates/
    └── index.html                   # Single-page dashboard application
```

---

## 🚀 4. Quick Start & Execution Instructions

### Prerequisites
- Python 3.10 or higher installed on your computer.

### Step 1: Clone or Navigate to the Directory
```bash
cd /path/to/PaisaPilot_AI
```

### Step 2: Set Up Python Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate on macOS / Linux:
source venv/bin/activate

# (Or on Windows Command Prompt):
# venv\Scripts\activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables (Optional)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Open `.env` and add your Google Gemini API key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
PORT=5000
DEBUG=True
```
> [!NOTE]  
> If you do not have a Gemini API key or leave it blank, **PaisaPilot AI automatically runs in Rule-Based Offline Fallback Mode**. You can also enter or test your API key directly in the web UI header modal at any time without restarting the server!

### Step 5: Run the Web Application
```bash
python3 app.py
```

Open your browser and navigate to:
```
http://localhost:5000
```

---

## 🤖 5. AI Implementation Details

### A. Predefined Categorization Taxonomy
Transactions are classified strictly into 9 predefined categories:
- **Food** (Swiggy, Zomato, groceries, campus canteen, restaurants)
- **Travel** (Uber, Ola, Rapido, Metro, train, fuel, bus)
- **Shopping** (Amazon, Flipkart, clothing, shoes, tech gadgets)
- **Education** (Books, tuition fees, stationery, online courses)
- **Bills** (Electricity, Wi-Fi, mobile recharge, rent, gas)
- **Health** (Pharmacy, doctor, gym memberships, fitness supplements)
- **Entertainment** (Movies, Netflix, Spotify, gaming, concerts)
- **Salary** (Monthly allowance, stipend, freelance earnings)
- **Other** (Uncategorized or miscellaneous items)

### B. Gemini AI Integration & Prompt Design
When `GEMINI_API_KEY` is present, the backend invokes `gemini-2.5-flash`:
1. **Categorization:** Sends the description to Gemini with few-shot Indian fintech examples, returning valid JSON containing `{ category, confidence, reasoning }`.
2. **Savings Advisor:** Injects actual database aggregates (Income, Expenses, Savings Rate, Category Outlays, Top Expense Driver) into Gemini to produce tailored savings tips, a Financial Health Score (0–100), and a 30-day savings challenge.

### C. Academic Fallback Guarantee
If the API key is unset or network errors occur, the backend utilizes its deterministic heuristic logic engine (`ai_service.py`). The UI transparently identifies this mode:
- 🟢 **Live Gemini AI Active** (when API key is verified)
- 🟡 **Offline Fallback Mode** (standard rule-based heuristic logic)

---

## 🧪 6. Automated Testing

An end-to-end integration test verifies all 11 core functional requirements:
- Web dashboard route accessibility.
- Accurate dynamic database calculations (income, expense, balance, savings rate).
- Adding income and expense records.
- Instant transaction deletion and database cascade.
- AI categorization against assignment examples (`Swiggy ₹350`, `Uber ₹200`, `Amazon ₹1500`, `College books ₹500`).
- AI savings recommendation synthesis.
- CSV and JSON export endpoints.
- Database reset functionality.

Run the test suite anytime:
```bash
source venv/bin/activate
python3 -c "
import app, json
client = app.app.test_client()

# Check Status
res = client.get('/api/status')
assert res.status_code == 200
print('Status OK:', res.json['ai']['engine'])

# Check Dynamic DB Aggregates
summary = client.get('/api/summary').json
print('DB Income:', summary['total_income'], 'Expenses:', summary['total_expenses'], 'Balance:', summary['available_balance'])

# Test AI Categorization
tests = [('Swiggy ₹350', 'Food'), ('Uber ₹200', 'Travel'), ('Amazon ₹1,500', 'Shopping'), ('College books ₹500', 'Education')]
for desc, expected in tests:
    cat = client.post('/api/categorize', json={'description': desc}).json['category']
    assert cat == expected, f'Failed {desc}: got {cat}'
    print(f'AI: {desc} -> {cat} (Verified)')

print('All Integration Tests Passed!')
"
```

---

## 📊 7. Demonstration Dataset

The SQLite database (`finance.db`) is automatically seeded on first launch with realistic fictional student transactions in Indian Rupees (₹):

| Transaction Description | Type | Category | Amount |
| :--- | :--- | :--- | :--- |
| **Monthly College Allowance** | Income | Salary | ₹15,000.00 |
| **Part-Time Python Tutoring** | Income | Salary | ₹3,000.00 |
| **Swiggy & Campus Canteen Meals** | Expense | Food | ₹2,000.00 |
| **Metro Card Recharge & Uber Trips** | Expense | Travel | ₹1,000.00 |
| **Amazon Tech Accessories & Shoes** | Expense | Shopping | ₹1,500.00 |
| **College Reference Books & Stationery** | Expense | Education | ₹500.00 |
| **Cinema Tickets & Spotify Subscription** | Expense | Entertainment | ₹700.00 |
| **Hostel Wi-Fi & Airtel Mobile Recharge** | Expense | Bills | ₹499.00 |
| **Apollo Pharmacy Meds & Gym Supplements** | Expense | Health | ₹800.00 |

- **Total Inflow:** ₹18,000.00
- **Total Outflow:** ₹6,999.00
- **Available Liquidity:** ₹11,001.00
- **Savings Rate:** 61.1% (*Healthy Growth*)
- **Highest Spending Category:** Food (₹2,000.00 / 28.6% of expenses)

You can restore this dataset at any point by clicking the **Reset Demo Data** icon in the top header or via `POST /api/reset`.

---

## 📑 8. Deliverables Included

1. **Complete Source Code:** Full Flask application (`app.py`), database management (`database.py`), AI service (`ai_service.py`), modern CSS (`style.css`), Chart.js engine (`charts.js`), and frontend client (`app.js`).
2. **README.md:** Installation, architecture, testing, and operational manual.
3. **Sample Datasets:** Pre-generated [sample_transactions.json](file:///Users/vamshikrishnakanna/Desktop/PaisaPilot_AI/sample_transactions.json) and [sample_transactions.csv](file:///Users/vamshikrishnakanna/Desktop/PaisaPilot_AI/sample_transactions.csv).
4. **Project Report:** Complete academic report ([PROJECT_REPORT.md](file:///Users/vamshikrishnakanna/Desktop/PaisaPilot_AI/PROJECT_REPORT.md)) covering objectives, architecture, AI methodology, sample outputs, and conclusions.
5. **Presentation Slides:** A professional 10-slide PowerPoint presentation ([PaisaPilot_AI_Presentation.pptx](file:///Users/vamshikrishnakanna/Desktop/PaisaPilot_AI/PaisaPilot_AI_Presentation.pptx)) generated via `generate_presentation.py`.

---

## 🎓 Academic Integrity Note
In compliance with academic standards, **PaisaPilot AI** strictly differentiates live LLM inference from deterministic fallback logic. When `GEMINI_API_KEY` is not present, the system transparently identifies the engine as `Rule-Based Financial Logic Engine (Offline Fallback)` and does not falsely claim machine learning or AI execution.

