"""
Database module for PaisaPilot AI
Handles SQLite database connection, schema setup, CRUD operations,
and financial aggregation calculations.
"""

import sqlite3
import os
from datetime import datetime, date

DB_PATH = os.path.join(os.path.dirname(__file__), "finance.db")

PREDEFINED_CATEGORIES = [
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

SAMPLE_TRANSACTIONS = [
    {
        "description": "Monthly College Allowance",
        "amount": 15000.0,
        "date": date.today().strftime("%Y-%m-01"),
        "type": "income",
        "category": "Salary"
    },
    {
        "description": "Part-Time Python Tutoring",
        "amount": 3000.0,
        "date": date.today().strftime("%Y-%m-03"),
        "type": "income",
        "category": "Salary"
    },
    {
        "description": "Swiggy & Campus Canteen Meals",
        "amount": 2000.0,
        "date": date.today().strftime("%Y-%m-05"),
        "type": "expense",
        "category": "Food"
    },
    {
        "description": "Metro Card Recharge & Uber Trips",
        "amount": 1000.0,
        "date": date.today().strftime("%Y-%m-07"),
        "type": "expense",
        "category": "Travel"
    },
    {
        "description": "Amazon Tech Accessories & Shoes",
        "amount": 1500.0,
        "date": date.today().strftime("%Y-%m-10"),
        "type": "expense",
        "category": "Shopping"
    },
    {
        "description": "College Reference Books & Stationery",
        "amount": 500.0,
        "date": date.today().strftime("%Y-%m-12"),
        "type": "expense",
        "category": "Education"
    },
    {
        "description": "Cinema Tickets & Spotify Subscription",
        "amount": 700.0,
        "date": date.today().strftime("%Y-%m-14"),
        "type": "expense",
        "category": "Entertainment"
    },
    {
        "description": "Hostel Wi-Fi & Airtel Mobile Recharge",
        "amount": 499.0,
        "date": date.today().strftime("%Y-%m-16"),
        "type": "expense",
        "category": "Bills"
    },
    {
        "description": "Apollo Pharmacy Meds & Gym Supplements",
        "amount": 800.0,
        "date": date.today().strftime("%Y-%m-18"),
        "type": "expense",
        "category": "Health"
    }
]


def get_db_connection():
    """Returns an active SQLite database connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes the database schema if tables do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
            category TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()
    
    # Auto-seed if empty
    seed_sample_data(force=False)


def seed_sample_data(force=False):
    """
    Seeds initial realistic fictional data.
    If force=True, clears existing records first.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if force:
        cursor.execute("DELETE FROM transactions")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='transactions'")
        conn.commit()
    
    cursor.execute("SELECT COUNT(*) AS count FROM transactions")
    row = cursor.fetchone()
    count = row["count"] if row else 0
    
    if count == 0:
        for item in SAMPLE_TRANSACTIONS:
            cursor.execute("""
                INSERT INTO transactions (description, amount, date, type, category)
                VALUES (?, ?, ?, ?, ?)
            """, (
                item["description"],
                item["amount"],
                item["date"],
                item["type"],
                item["category"]
            ))
        conn.commit()
    conn.close()


def add_transaction(description, amount, tx_date, tx_type, category):
    """
    Adds a new transaction to the database after basic validation.
    """
    if not description or not str(description).strip():
        raise ValueError("Transaction description cannot be empty.")
    
    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError("Amount must be a positive number greater than 0.")
    except (ValueError, TypeError):
        raise ValueError("Amount must be a valid positive number.")
    
    if tx_type not in ["income", "expense"]:
        raise ValueError("Transaction type must be 'income' or 'expense'.")
    
    # Format or validate date
    if not tx_date:
        tx_date = date.today().strftime("%Y-%m-%d")
    else:
        try:
            parsed = datetime.strptime(tx_date, "%Y-%m-%d")
            tx_date = parsed.strftime("%Y-%m-%d")
        except ValueError:
            # Fallback to today
            tx_date = date.today().strftime("%Y-%m-%d")
            
    # Clean category
    category = str(category).strip()
    if category not in PREDEFINED_CATEGORIES:
        category = "Other"
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (description, amount, date, type, category)
        VALUES (?, ?, ?, ?, ?)
    """, (description.strip(), round(amount, 2), tx_date, tx_type, category))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    
    return get_transaction_by_id(new_id)


def get_transaction_by_id(tx_id):
    """Fetch single transaction by id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE id = ?", (tx_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def delete_transaction(tx_id):
    """Deletes transaction by ID. Returns True if deleted, False if not found."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def get_all_transactions(tx_type=None, category=None, search=None, sort_by="date_desc"):
    """
    Retrieves filtered and sorted transactions.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM transactions WHERE 1=1"
    params = []
    
    if tx_type and tx_type in ["income", "expense"]:
        query += " AND type = ?"
        params.append(tx_type)
        
    if category and category in PREDEFINED_CATEGORIES:
        query += " AND category = ?"
        params.append(category)
        
    if search and search.strip():
        query += " AND (description LIKE ? OR category LIKE ?)"
        term = f"%{search.strip()}%"
        params.extend([term, term])
        
    # Sort order
    if sort_by == "date_asc":
        query += " ORDER BY date ASC, id ASC"
    elif sort_by == "amount_desc":
        query += " ORDER BY amount DESC, date DESC"
    elif sort_by == "amount_asc":
        query += " ORDER BY amount ASC, date DESC"
    else:  # date_desc default
        query += " ORDER BY date DESC, id DESC"
        
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_financial_summary():
    """
    Calculates summary figures from actual SQLite database records:
    - total_income
    - total_expenses
    - available_balance
    - monthly_savings
    - savings_rate
    - transaction_count
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) AS total_income,
            COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) AS total_expenses,
            COUNT(*) AS total_count
        FROM transactions
    """)
    row = cursor.fetchone()
    
    # Calculate current month's savings from SQLite
    current_month_prefix = date.today().strftime("%Y-%m")
    cursor.execute("""
        SELECT 
            COALESCE(SUM(CASE WHEN type = 'income' AND substr(date, 1, 7) = ? THEN amount ELSE 0 END), 0) -
            COALESCE(SUM(CASE WHEN type = 'expense' AND substr(date, 1, 7) = ? THEN amount ELSE 0 END), 0) AS current_month_net,
            COUNT(CASE WHEN substr(date, 1, 7) = ? THEN 1 END) AS current_month_count
        FROM transactions
    """, (current_month_prefix, current_month_prefix, current_month_prefix))
    month_row = cursor.fetchone()
    conn.close()
    
    total_income = round(row["total_income"], 2)
    total_expenses = round(row["total_expenses"], 2)
    available_balance = round(total_income - total_expenses, 2)
    
    if month_row and month_row["current_month_count"] > 0:
        monthly_savings = round(month_row["current_month_net"], 2)
    else:
        monthly_savings = available_balance
    
    savings_rate = 0.0
    if total_income > 0:
        savings_rate = round((available_balance / total_income) * 100, 1)
        
    # Financial Health status tag
    if total_income == 0 and total_expenses == 0:
        health_status = "No Activity"
        health_color = "neutral"
    elif available_balance < 0:
        health_status = "Deficit Warning"
        health_color = "danger"
    elif savings_rate < 20:
        health_status = "Low Savings"
        health_color = "warning"
    elif savings_rate < 40:
        health_status = "Moderate Savings"
        health_color = "info"
    else:
        health_status = "Healthy Growth"
        health_color = "success"

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "available_balance": available_balance,
        "monthly_savings": monthly_savings,
        "savings_rate": savings_rate,
        "transaction_count": row["total_count"],
        "health_status": health_status,
        "health_color": health_color
    }


def get_spending_analysis():
    """
    Analyzes transaction records and returns:
    - Category-wise expenses list with amounts and percentages
    - Highest spending category
    - 50-30-20 budget breakdown (Needs, Wants, Savings)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total expenses
    cursor.execute("SELECT COALESCE(SUM(amount), 0) AS total_exp FROM transactions WHERE type = 'expense'")
    total_exp = cursor.fetchone()["total_exp"]
    
    # Category totals for expenses
    cursor.execute("""
        SELECT category, SUM(amount) AS total, COUNT(*) AS count
        FROM transactions
        WHERE type = 'expense'
        GROUP BY category
        ORDER BY total DESC
    """)
    category_rows = cursor.fetchall()
    
    categories = []
    highest_category = None
    
    for row in category_rows:
        amount = round(row["total"], 2)
        pct = round((amount / total_exp * 100), 1) if total_exp > 0 else 0
        cat_data = {
            "category": row["category"],
            "amount": amount,
            "percentage": pct,
            "count": row["count"]
        }
        categories.append(cat_data)
        if highest_category is None:
            highest_category = cat_data

    # Total income for budget rule calculation
    cursor.execute("SELECT COALESCE(SUM(amount), 0) AS total_inc FROM transactions WHERE type = 'income'")
    total_inc = cursor.fetchone()["total_inc"]
    conn.close()

    if highest_category is None:
        highest_category = {
            "category": "None",
            "amount": 0.0,
            "percentage": 0.0,
            "count": 0
        }

    # Group actual expenses strictly into:
    # Needs: Bills, Health, Food and Education
    # Wants: Shopping, Entertainment and Travel (plus Other if recorded)
    # Remaining balance: Income minus expenses
    needs_categories = ["Bills", "Health", "Food", "Education"]
    wants_categories = ["Shopping", "Entertainment", "Travel", "Other"]
    
    needs_spent = sum(c["amount"] for c in categories if c["category"] in needs_categories)
    wants_spent = sum(c["amount"] for c in categories if c["category"] in wants_categories)
    
    # Remaining balance is strictly Income minus Expenses
    remaining_balance = round(total_inc - total_exp, 2)
    
    # Calculate actual percentages relative to total income
    if total_inc > 0:
        needs_pct = round((needs_spent / total_inc * 100), 1)
        wants_pct = round((wants_spent / total_inc * 100), 1)
        remaining_pct = round((remaining_balance / total_inc * 100), 1)
    else:
        needs_pct = 0.0
        wants_pct = 0.0
        remaining_pct = 0.0

    # Status assessments comparing actual vs recommended
    # Needs recommended benchmark: 50%
    if total_inc <= 0:
        needs_status = "No Income Recorded"
        needs_status_class = "neutral"
    elif needs_pct <= 50:
        needs_status = "Within Target (≤50%)"
        needs_status_class = "success"
    else:
        needs_status = f"Exceeds Target by {round(needs_pct - 50, 1)}%"
        needs_status_class = "warning"

    # Wants recommended benchmark: 30%
    if total_inc <= 0:
        wants_status = "No Income Recorded"
        wants_status_class = "neutral"
    elif wants_pct <= 30:
        wants_status = "Within Target (≤30%)"
        wants_status_class = "success"
    else:
        wants_status = f"Exceeds Target by {round(wants_pct - 30, 1)}%"
        wants_status_class = "warning"

    # Remaining Balance / Potential Savings recommended benchmark: 20%
    if total_inc <= 0:
        savings_status = "No Income Recorded"
        savings_status_class = "neutral"
    elif remaining_balance < 0:
        savings_status = f"Deficit Warning ({remaining_pct}%)"
        savings_status_class = "danger"
    elif remaining_pct >= 20:
        savings_status = "Above Target (≥20%)"
        savings_status_class = "success"
    else:
        savings_status = f"Below 20% Target ({remaining_pct}%)"
        savings_status_class = "warning"

    budget_breakdown = {
        "needs": {
            "amount": round(needs_spent, 2),
            "percentage": needs_pct,
            "recommended_pct": 50,
            "status": needs_status,
            "status_class": needs_status_class
        },
        "wants": {
            "amount": round(wants_spent, 2),
            "percentage": wants_pct,
            "recommended_pct": 30,
            "status": wants_status,
            "status_class": wants_status_class
        },
        "savings": {
            "amount": remaining_balance,
            "percentage": remaining_pct,
            "recommended_pct": 20,
            "is_deficit": remaining_balance < 0,
            "status": savings_status,
            "status_class": savings_status_class
        }
    }

    return {
        "total_expenses": round(total_exp, 2),
        "total_income": round(total_inc, 2),
        "categories": categories,
        "highest_spending_category": highest_category,
        "budget_breakdown": budget_breakdown
    }


def get_monthly_timeline():
    """
    Returns grouped monthly data for Income vs Expense timeline visualization.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            substr(date, 1, 7) AS month,
            SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) AS income,
            SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) AS expense
        FROM transactions
        GROUP BY month
        ORDER BY month ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    timeline = []
    for r in rows:
        timeline.append({
            "month": r["month"],
            "income": round(r["income"], 2),
            "expense": round(r["expense"], 2)
        })
    return timeline

