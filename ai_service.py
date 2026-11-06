"""
AI Service for PaisaPilot AI
Integrates Google Gemini API for:
1. Transaction categorization
2. Personalized savings recommendations based on actual financial records

Features a live API connection verification system (Requirement 8)
and an honest, deterministic rule-based fallback engine when offline.
"""

import os
import json
import re
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# List of predefined categories specified in assignment requirements
VALID_CATEGORIES = [
    "Food",
    "Travel",
    "Shopping",
    "Education",
    "Bills",
    "Health",
    "Entertainment",
    "Salary",
    "Other"
]

# Supported candidate models for modern Gemini API
CANDIDATE_MODELS = [
    "gemini-flash-lite-latest",
    "gemini-3.1-flash-lite-preview",
    "gemini-2.5-flash-lite",
    "gemini-flash-latest",
    "gemini-2.5-flash"
]

# Rule-based fallback keywords for Indian fintech context
FALLBACK_KEYWORDS = {
    "Food": [
        "swiggy", "zomato", "restaurant", "cafe", "canteen", "mess", "food", "dinner",
        "lunch", "breakfast", "burger", "pizza", "biryani", "chai", "coffee", "starbucks",
        "mcdonalds", "kfc", "dominos", "blinkit", "zepto", "bigbasket", "groceries", "grocery"
    ],
    "Travel": [
        "uber", "ola", "rapido", "metro", "bus", "train", "irctc", "flight", "indigo",
        "redbus", "cab", "auto", "petrol", "diesel", "fuel", "toll", "parking", "commute", "travel"
    ],
    "Shopping": [
        "amazon", "flipkart", "myntra", "meesho", "ajio", "zara", "h&m", "shoes", "clothes",
        "shopping", "electronics", "gadget", "mall", "purchase", "dress", "t-shirt"
    ],
    "Education": [
        "book", "books", "tuition", "course", "udemy", "coursera", "college", "university",
        "exam", "notes", "stationery", "xerox", "printout", "fees", "fee", "classes", "library"
    ],
    "Bills": [
        "bill", "electricity", "water", "wifi", "broadband", "recharge", "airtel", "jio",
        "vi", "rent", "maintenance", "gas", "cylinder", "lpg", "dth"
    ],
    "Health": [
        "pharmacy", "apollo", "medplus", "medicine", "doctor", "clinic", "hospital",
        "gym", "fitness", "protein", "supplement", "dentist", "medical", "checkup"
    ],
    "Entertainment": [
        "netflix", "spotify", "prime", "hotstar", "youtube", "cinema", "movie", "pvr",
        "inox", "tickets", "concert", "game", "gaming", "steam", "playstation"
    ],
    "Salary": [
        "salary", "stipend", "allowance", "pocket money", "freelance", "tutoring",
        "bonus", "dividend", "interest", "wages", "internship", "earnings"
    ]
}

# In-memory connection test cache to avoid excessive latency on every poll
_connection_cache = {
    "status": None,
    "last_checked": 0,
    "model": None,
    "error": None
}


def get_api_key():
    """Retrieve Gemini API key from environment."""
    return os.environ.get("GEMINI_API_KEY", "").strip()


def verify_gemini_connection(force: bool = False):
    """
    Directly verifies whether Google Gemini API is actively responding.
    Caches the result for 60 seconds unless force=True.
    Returns (is_connected: bool, error_msg: str, active_model: str).
    """
    global _connection_cache
    api_key = get_api_key()
    
    if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
        _connection_cache = {
            "status": False,
            "last_checked": time.time(),
            "model": None,
            "error": "API key not configured"
        }
        return False, "API key not configured", None
        
    now = time.time()
    if not force and _connection_cache["status"] is not None and (now - _connection_cache["last_checked"] < 60):
        return _connection_cache["status"], _connection_cache["error"], _connection_cache["model"]
        
    # Attempt an actual lightweight connection test call
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        
        last_err = None
        for model_name in CANDIDATE_MODELS:
            try:
                res = client.models.generate_content(
                    model=model_name,
                    contents="ping"
                )
                if res and res.text:
                    _connection_cache = {
                        "status": True,
                        "last_checked": now,
                        "model": model_name,
                        "error": None
                    }
                    return True, None, model_name
            except Exception as e:
                last_err = e
                continue
                
        err_msg = str(last_err) if last_err else "All candidate Gemini models unavailable"
        _connection_cache = {
            "status": False,
            "last_checked": now,
            "model": None,
            "error": err_msg
        }
        return False, err_msg, None
    except Exception as e:
        _connection_cache = {
            "status": False,
            "last_checked": now,
            "model": None,
            "error": str(e)
        }
        return False, str(e), None


def is_ai_live():
    """
    Returns True ONLY if Gemini API connection is genuinely active and responding.
    Strictly satisfies Requirement 8.
    """
    is_connected, _, _ = verify_gemini_connection()
    return is_connected


def get_ai_status(force_check: bool = False):
    """
    Returns AI operational status for UI display.
    Guarantees that 'Live Gemini AI Active' is ONLY shown if the API actually responds!
    """
    api_key = get_api_key()
    if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
        return {
            "live": False,
            "engine": "Rule-Based Logic Engine (Offline Fallback)",
            "badge_text": "Offline Fallback Mode",
            "badge_class": "badge-ai-fallback",
            "description": "Standard keyword & deterministic heuristic logic (API key not configured)"
        }
        
    is_connected, err_msg, model_name = verify_gemini_connection(force=force_check)
    if is_connected:
        return {
            "live": True,
            "engine": f"Google Gemini AI ({model_name})",
            "badge_text": "Live Gemini AI Active",
            "badge_class": "badge-ai-live",
            "description": f"Real-time generative AI verified & responding via {model_name}"
        }
    else:
        # API key is present but connection is NOT responding
        short_err = (err_msg[:60] + "...") if err_msg and len(err_msg) > 60 else (err_msg or "Unreachable")
        return {
            "live": False,
            "engine": "Rule-Based Logic Engine (Offline Fallback)",
            "badge_text": "API Error – Fallback Active",
            "badge_class": "badge-ai-fallback",
            "description": f"Gemini API not responding ({short_err}). Using deterministic rule-based fallback."
        }


def extract_json_safely(text: str) -> dict:
    """Safely extracts JSON from an LLM response even with surrounding text or markdown."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Fallback to regex finding the outermost { ... }
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise


def generate_with_gemini(api_key: str, prompt: str):
    """
    Invokes Google Gemini using candidate model cascade for resilience.
    Tries fast lightweight models first and falls back to alternatives if busy.
    """
    from google import genai
    client = genai.Client(api_key=api_key)
    
    last_err = None
    for model_name in CANDIDATE_MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            if response and response.text:
                return response.text.strip(), model_name
        except Exception as e:
            last_err = e
            continue
            
    raise RuntimeError(f"All Gemini models exhausted: {last_err}")


# =====================================================================
# FEATURE C: TRANSACTION CATEGORIZATION
# =====================================================================

def categorize_transaction_with_rules(description: str) -> dict:
    """
    Deterministic rule-based keyword matching fallback.
    Transparently reports engine as 'rule-based-fallback'.
    """
    desc_lower = description.lower()
    
    for category, keywords in FALLBACK_KEYWORDS.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower) or kw in desc_lower:
                return {
                    "category": category,
                    "confidence": 0.85,
                    "reasoning": f"Matched financial keyword '{kw}' associated with {category}.",
                    "engine": "Rule-Based Heuristic Engine (Offline Fallback)",
                    "is_fallback": True
                }
                
    return {
        "category": "Other",
        "confidence": 0.50,
        "reasoning": "No specific category keywords identified. Assigned to 'Other'.",
        "engine": "Rule-Based Heuristic Engine (Offline Fallback)",
        "is_fallback": True
    }


def categorize_transaction(description: str) -> dict:
    """
    Categorizes a transaction using Google Gemini AI, falling back
    to transparent rule-based heuristics if the key is unset or call fails.
    """
    if not description or not str(description).strip():
        return {
            "category": "Other",
            "confidence": 0.0,
            "reasoning": "Empty description provided.",
            "engine": "Validation",
            "is_fallback": True
        }

    api_key = get_api_key()
    if not is_ai_live():
        return categorize_transaction_with_rules(description)

    # Attempt Google Gemini API call
    try:
        prompt = f"""
You are an expert financial transaction classification assistant for PaisaPilot AI, an Indian personal finance management system.
Your task is to classify the following transaction description into exactly ONE category from this allowed list:
{', '.join(VALID_CATEGORIES)}

Transaction Description: "{description}"

Rules:
1. Choose strictly from the allowed list: Food, Travel, Shopping, Education, Bills, Health, Entertainment, Salary, Other.
2. Consider Indian brands and terminology (e.g., Swiggy/Zomato -> Food, Uber/Ola/Metro -> Travel, Amazon/Myntra -> Shopping, Airtel/Jio/Rent -> Bills, Apollo/Gym -> Health, Allowance/Stipend -> Salary).
3. Return valid JSON only with keys: "category", "confidence" (float between 0.0 and 1.0), and "reasoning" (concise one-sentence rationale).

Example Output:
{{"category": "Food", "confidence": 0.95, "reasoning": "Swiggy is a well-known food delivery platform in India."}}
"""
        text, model_used = generate_with_gemini(api_key, prompt)
        data = extract_json_safely(text)
        
        category = data.get("category", "Other")
        if category not in VALID_CATEGORIES:
            category = "Other"
            
        return {
            "category": category,
            "confidence": float(data.get("confidence", 0.95)),
            "reasoning": data.get("reasoning", f"Categorized by Google Gemini AI ({model_used})."),
            "engine": f"Google Gemini ({model_used})",
            "is_fallback": False
        }
    except Exception as e:
        # Graceful fallback on API error
        fallback_res = categorize_transaction_with_rules(description)
        fallback_res["api_error"] = str(e)
        return fallback_res


# =====================================================================
# FEATURE E: AI SAVINGS RECOMMENDATIONS
# =====================================================================

def generate_savings_recommendations_with_rules(summary: dict, spending: dict) -> dict:
    """
    Deterministic heuristic recommendation generator based on actual mathematical
    ratios from the user's database records. Transparently marked as rule-based fallback.
    """
    total_income = summary.get("total_income", 0.0)
    total_expenses = summary.get("total_expenses", 0.0)
    savings = summary.get("available_balance", 0.0)
    savings_rate = summary.get("savings_rate", 0.0)
    categories = spending.get("categories", [])
    highest_cat = spending.get("highest_spending_category", {})
    budget = spending.get("budget_breakdown", {})
    
    # Calculate health score (0 to 100)
    if total_income <= 0 and total_expenses <= 0:
        score = 50
        rating = "No Transactions Recorded"
    elif total_income <= 0:
        score = 30
        rating = "Needs Income Records"
    elif savings < 0:
        score = max(20, int(50 + (savings / total_income) * 50))
        rating = "Budget Deficit Warning"
    else:
        score = min(95, int(40 + (savings_rate / 50.0) * 55))
        if score >= 80:
            rating = "Excellent Financial Health"
        elif score >= 60:
            rating = "Healthy & Stable"
        else:
            rating = "Moderate / Improvement Needed"

    top_name = highest_cat.get("category", "None")
    top_amount = highest_cat.get("amount", 0.0)
    top_pct = highest_cat.get("percentage", 0.0)
    
    tips = []
    potential_savings = 0.0

    if top_name == "Food":
        potential_save = round(top_amount * 0.25, 2)
        potential_savings += potential_save
        tips.append({
            "title": f"Optimize Dining & Food Orders (Save ~₹{potential_save:,.0f}/mo)",
            "category": "Food",
            "impact": "High",
            "description": f"Food is your #1 expense at ₹{top_amount:,.2f} ({top_pct}% of total expenses). Limiting delivery app surge orders to weekends and using campus meal plans can trim ~25% without sacrificing nutrition."
        })
    elif top_name == "Shopping":
        potential_save = round(top_amount * 0.30, 2)
        potential_savings += potential_save
        tips.append({
            "title": f"Apply 48-Hour Cart Rule on Shopping (Save ~₹{potential_save:,.0f}/mo)",
            "category": "Shopping",
            "impact": "High",
            "description": f"Shopping accounts for ₹{top_amount:,.2f} ({top_pct}% of your expenses). Place non-essential items on a 48-hour cooling wishlist before purchase to eliminate impulse buys."
        })
    elif top_name == "Travel":
        potential_save = round(top_amount * 0.20, 2)
        potential_savings += potential_save
        tips.append({
            "title": f"Switch to Monthly Transit Passes (Save ~₹{potential_save:,.0f}/mo)",
            "category": "Travel",
            "impact": "Medium",
            "description": f"You spent ₹{top_amount:,.2f} on travel. Adopting metro smart cards or pooling cab rides for routine commutes saves up to 20% compared to on-demand cab bookings."
        })
    elif top_name == "Entertainment":
        potential_save = round(top_amount * 0.35, 2)
        potential_savings += potential_save
        tips.append({
            "title": f"Audit Digital Subscriptions (Save ~₹{potential_save:,.0f}/mo)",
            "category": "Entertainment",
            "impact": "Medium",
            "description": f"Entertainment represents ₹{top_amount:,.2f}. Consolidate OTT/music platforms, utilize student discount subscriptions (e.g. Spotify student tier), and share family plans."
        })
    elif top_name != "None":
        potential_save = round(top_amount * 0.15, 2)
        potential_savings += potential_save
        tips.append({
            "title": f"Cap Spending on {top_name} (Save ~₹{potential_save:,.0f}/mo)",
            "category": top_name,
            "impact": "Medium",
            "description": f"{top_name} is currently your highest expenditure category at ₹{top_amount:,.2f}. Setting a strict weekly sub-budget will keep spending under control."
        })

    # 50/30/20 Budget Rule Assessment
    wants_pct = budget.get("wants", {}).get("percentage", 0.0)
    wants_amt = budget.get("wants", {}).get("amount", 0.0)
    if wants_pct > 30:
        wants_trim = round(wants_amt * 0.20, 2)
        potential_savings += wants_trim
        tips.append({
            "title": "Realign Wants to 30% Benchmark",
            "category": "Budgeting",
            "impact": "High",
            "description": f"Your discretionary 'Wants' (Shopping, Entertainment, Travel) stand at {wants_pct}% of income, exceeding the recommended 30% threshold. Trimming non-essentials can free up ~₹{wants_trim:,.0f}."
        })
    else:
        tips.append({
            "title": "Healthy Discretionary Ratio Maintained",
            "category": "Budgeting",
            "impact": "Low",
            "description": f"Great discipline! Discretionary wants constitute {wants_pct}% of your income, well within the safe 30% target."
        })

    # Emergency Fund & Savings Growth
    if savings_rate < 20:
        tips.append({
            "title": "Target a 20% Minimum Baseline Savings",
            "category": "Savings",
            "impact": "High",
            "description": f"Your current savings rate is {savings_rate}%. Financial advisors recommend putting aside at least 20% (₹{round(total_income * 0.2, 2):,.2f}) as an emergency cushion."
        })
    else:
        tips.append({
            "title": "Automate Surplus Savings into High-Yield Deposits",
            "category": "Investing",
            "impact": "Medium",
            "description": f"With an outstanding {savings_rate}% savings rate (₹{savings:,.2f} surplus), set up an automated Recurring Deposit (RD) or liquid fund to earn 6-7% interest on idle cash."
        })

    challenge = f"Try a 7-Day 'Zero-Unplanned Spend' Challenge: Prep meals at home and pause non-essential shopping to lock in an extra ₹{max(500, int(potential_savings * 0.5)):,.0f} this month."

    return {
        "score": score,
        "rating": rating,
        "executive_summary": (
            f"Based on your recorded income of ₹{total_income:,.2f} and expenses of ₹{total_expenses:,.2f}, "
            f"you have an active surplus of ₹{savings:,.2f} ({savings_rate}% savings rate). "
            + (f"Your largest cost driver is {top_name} (₹{top_amount:,.2f})." if top_name != "None" else "No expense recorded yet.")
        ),
        "potential_monthly_savings": potential_savings,
        "recommendations": tips,
        "monthly_challenge": challenge,
        "engine": "Rule-Based Financial Logic Engine (Offline Fallback)",
        "is_fallback": True,
        "note": "To enable generative AI analysis, configure a working GEMINI_API_KEY."
    }


def generate_savings_recommendations(summary: dict, spending: dict) -> dict:
    """
    Generates personalized savings recommendations using Gemini AI,
    or falls back to deterministic financial heuristics if offline.
    """
    api_key = get_api_key()
    if not is_ai_live():
        return generate_savings_recommendations_with_rules(summary, spending)

    try:
        prompt = f"""
You are an expert personal finance advisor for 'PaisaPilot AI', advising a college student / young Indian earner.
Analyze their REAL financial database summary below and generate actionable, highly personalized recommendations.

ACTUAL FINANCIAL DATA:
- Total Income: ₹{summary.get('total_income', 0)}
- Total Expenses: ₹{summary.get('total_expenses', 0)}
- Available Balance (Monthly Savings): ₹{summary.get('available_balance', 0)}
- Savings Rate: {summary.get('savings_rate', 0)}%
- Number of Transactions: {summary.get('transaction_count', 0)}
- Highest Spending Category: {json.dumps(spending.get('highest_spending_category', {}))}
- Category Breakdown: {json.dumps(spending.get('categories', []))}
- 50/30/20 Budget Analysis: {json.dumps(spending.get('budget_breakdown', {}))}

REQUIREMENTS:
1. Base all advice strictly on their actual figures (e.g., mention exact rupee amounts and percentages).
2. If Food or Shopping is high, provide concrete, realistic Indian student tips (e.g., meal-prep, campus tiffin, pause delivery apps, 48-hour cooling cart rule).
3. Provide a realistic Financial Health Score (0 to 100) and an assessment rating.
4. Calculate realistic 'potential_monthly_savings' (in ₹) achievable by adopting your tips.
5. Provide 3 to 4 specific recommendations. Each recommendation must have:
   - "title" (concise, punchy)
   - "category" (e.g. Food, Shopping, Budgeting, Investing)
   - "impact" ("High", "Medium", or "Low")
   - "description" (2-3 sentences explaining the exact rationale referencing their numbers)
6. Provide a practical "monthly_challenge" (e.g. 7-day no-takeout streak).

OUTPUT FORMAT:
Return valid JSON only (no markdown code blocks, or clean json) with keys:
{{
  "score": 85,
  "rating": "Healthy & Thriving",
  "executive_summary": "1-2 sentence executive financial verdict",
  "potential_monthly_savings": 1200.0,
  "recommendations": [
    {{
      "title": "...",
      "category": "...",
      "impact": "High",
      "description": "..."
    }}
  ],
  "monthly_challenge": "..."
}}
"""
        text, model_used = generate_with_gemini(api_key, prompt)
        data = extract_json_safely(text)
        data["engine"] = f"Google Gemini AI ({model_used})"
        data["is_fallback"] = False
        return data
    except Exception as e:
        fallback_res = generate_savings_recommendations_with_rules(summary, spending)
        fallback_res["api_error"] = str(e)
        return fallback_res
