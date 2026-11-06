"""
Flask Application for PaisaPilot AI
AI-Powered Personal Finance Management System
College Assignment: AI for Finance CIA-2
"""

import os
import csv
import io
import json
from flask import Flask, render_template, request, jsonify, Response
from dotenv import load_dotenv

import database
import ai_service

# Load environment
load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "paisapilot-ai-secure-secret-2026")

# Initialize database schema and seed data on startup
with app.app_context():
    database.init_db()


# -------------------------------------------------------------
# Frontend Route
# -------------------------------------------------------------
@app.route("/")
def index():
    """Renders the main single-page dashboard application."""
    ai_status = ai_service.get_ai_status()
    return render_template(
        "index.html",
        categories=database.PREDEFINED_CATEGORIES,
        ai_status=ai_status
    )


# -------------------------------------------------------------
# System & Status API
# -------------------------------------------------------------
@app.route("/api/status", methods=["GET"])
def get_status():
    """Returns application health and AI engine status."""
    ai_status = ai_service.get_ai_status()
    summary = database.get_financial_summary()
    return jsonify({
        "status": "healthy",
        "app_name": "PaisaPilot AI",
        "version": "1.0.0",
        "ai": ai_status,
        "transaction_count": summary["transaction_count"]
    })


@app.route("/api/update-api-key", methods=["POST"])
def update_api_key():
    """
    Allows user to update the Gemini API key directly from UI modal.
    Saves to runtime environment, updates .env file, and genuinely tests the connection.
    """
    data = request.get_json() or {}
    new_key = data.get("api_key", "").strip()
    
    # Update runtime environment
    os.environ["GEMINI_API_KEY"] = new_key
    
    # Attempt to persist to .env file
    try:
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        lines = []
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        
        key_found = False
        new_lines = []
        for line in lines:
            if line.startswith("GEMINI_API_KEY="):
                new_lines.append(f"GEMINI_API_KEY={new_key}\n")
                key_found = True
            else:
                new_lines.append(line)
        if not key_found:
            new_lines.append(f"GEMINI_API_KEY={new_key}\n")
            
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
    except Exception as e:
        print("Note: Could not write to .env:", e)

    # Genuinely verify API connection with force=True
    ai_status = ai_service.get_ai_status(force_check=True)
    if ai_status["live"]:
        msg = f"Gemini API key verified successfully! Connected to {ai_status['engine']}."
    elif new_key:
        msg = "API key saved, but Gemini API failed to respond. Switched to offline fallback mode."
    else:
        msg = "Switched to rule-based fallback mode."

    return jsonify({
        "success": True,
        "ai": ai_status,
        "message": msg
    })


# -------------------------------------------------------------
# Financial Summary API
# -------------------------------------------------------------
@app.route("/api/summary", methods=["GET"])
def get_summary():
    """Returns key financial metrics computed from actual database records."""
    summary = database.get_financial_summary()
    return jsonify(summary)


# -------------------------------------------------------------
# Transaction Management API
# -------------------------------------------------------------
@app.route("/api/transactions", methods=["GET"])
def list_transactions():
    """Retrieves list of transactions with optional search and filters."""
    tx_type = request.args.get("type", None)
    category = request.args.get("category", None)
    search = request.args.get("search", None)
    sort_by = request.args.get("sort", "date_desc")
    
    transactions = database.get_all_transactions(
        tx_type=tx_type,
        category=category,
        search=search,
        sort_by=sort_by
    )
    return jsonify({
        "count": len(transactions),
        "transactions": transactions
    })


@app.route("/api/transactions", methods=["POST"])
def create_transaction():
    """Adds a new transaction."""
    data = request.get_json() or {}
    
    description = data.get("description", "").strip()
    amount = data.get("amount")
    tx_date = data.get("date")
    tx_type = data.get("type", "expense")
    category = data.get("category", "Other")
    
    try:
        new_tx = database.add_transaction(
            description=description,
            amount=amount,
            tx_date=tx_date,
            tx_type=tx_type,
            category=category
        )
        return jsonify({
            "success": True,
            "message": "Transaction added successfully.",
            "transaction": new_tx
        }), 201
    except ValueError as val_err:
        return jsonify({"success": False, "error": str(val_err)}), 400
    except Exception as err:
        return jsonify({"success": False, "error": "Internal server error: " + str(err)}), 500


@app.route("/api/transactions/<int:tx_id>", methods=["DELETE"])
def remove_transaction(tx_id):
    """Deletes a transaction by ID."""
    deleted = database.delete_transaction(tx_id)
    if deleted:
        return jsonify({"success": True, "message": f"Transaction #{tx_id} deleted."})
    return jsonify({"success": False, "error": "Transaction not found."}), 404


# -------------------------------------------------------------
# Spending Analysis & Timeline API
# -------------------------------------------------------------
@app.route("/api/spending", methods=["GET"])
def get_spending():
    """Returns category-wise breakdown and 50-30-20 budget metrics."""
    analysis = database.get_spending_analysis()
    return jsonify(analysis)


@app.route("/api/timeline", methods=["GET"])
def get_timeline():
    """Returns monthly income vs expense timeline."""
    timeline = database.get_monthly_timeline()
    return jsonify({"timeline": timeline})


# -------------------------------------------------------------
# AI Integration API
# -------------------------------------------------------------
@app.route("/api/categorize", methods=["POST"])
def categorize():
    """
    Categorizes a transaction description using Gemini AI or fallback engine.
    """
    data = request.get_json() or {}
    description = data.get("description", "").strip()
    
    if not description:
        return jsonify({"error": "Description is required."}), 400
        
    result = ai_service.categorize_transaction(description)
    return jsonify(result)


@app.route("/api/recommendations", methods=["GET", "POST"])
def recommendations():
    """
    Generates personalized savings recommendations from actual database summary.
    """
    summary = database.get_financial_summary()
    spending = database.get_spending_analysis()
    
    recs = ai_service.generate_savings_recommendations(summary, spending)
    return jsonify({
        "summary": summary,
        "spending": spending,
        "recommendations": recs
    })


# -------------------------------------------------------------
# Sample Data & Export API
# -------------------------------------------------------------
@app.route("/api/reset", methods=["POST"])
def reset_sample_data():
    """Resets transactions to the official fictional sample dataset."""
    database.seed_sample_data(force=True)
    return jsonify({
        "success": True,
        "message": "Database reset to realistic fictional sample transactions."
    })


@app.route("/api/export/json", methods=["GET"])
def export_json():
    """Exports transactions as JSON."""
    transactions = database.get_all_transactions()
    return Response(
        json.dumps(transactions, indent=2),
        mimetype="application/json",
        headers={"Content-Disposition": "attachment;filename=paisapilot_transactions.json"}
    )


@app.route("/api/export/csv", methods=["GET"])
def export_csv():
    """Exports transactions as CSV."""
    transactions = database.get_all_transactions()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Date", "Description", "Type", "Category", "Amount (INR)", "Created At"])
    for t in transactions:
        writer.writerow([t["id"], t["date"], t["description"], t["type"], t["category"], t["amount"], t["created_at"]])
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=paisapilot_transactions.csv"}
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    debug = os.environ.get("DEBUG", "True").lower() in ("true", "1")
    print(f"🚀 Starting PaisaPilot AI on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)

