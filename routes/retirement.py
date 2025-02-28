from flask import Blueprint, render_template, jsonify, request, session
from extensions import db
from models.user import User
from models.retirement import RetirementAccount
import time
from typing import Dict, Any, Tuple, Union
from sqlalchemy.exc import SQLAlchemyError

retirement_bp = Blueprint("retirement", __name__, url_prefix="/apps/401k")

@retirement_bp.route("/")
def retirement_dashboard() -> Union[str, Tuple[Dict[str, str], int]]:
    """
    Render the retirement dashboard page.
    
    Returns:
        Union[str, Tuple[Dict[str, str], int]]: Rendered template or error response
    """
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401
    return render_template("401k.html", username=session["user"])

@retirement_bp.route("/balance")
def get_balance() -> Tuple[Dict[str, Any], int]:
    """
    Get the balance information for the current user.
    
    Returns:
        Tuple[Dict[str, Any], int]: JSON response with balance data and status code
    """
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401
        
    username = session["user"]
    
    # Find the user
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Find or create retirement account
    retirement_account = RetirementAccount.query.filter_by(user_id=user.id).first()
    
    if not retirement_account:
        # Create a new retirement account with default values
        retirement_account = RetirementAccount(
            user_id=user.id,
            personal_funds=10000.0,
            retirement_balance=0.0
        )
        db.session.add(retirement_account)
        db.session.commit()
    
    return jsonify(retirement_account.to_dict()), 200

@retirement_bp.route("/contribute", methods=["POST"])
def contribute() -> Tuple[Dict[str, Any], int]:
    """
    Process a contribution to the retirement account.
    
    Returns:
        Tuple[Dict[str, Any], int]: JSON response with updated balance data and status code
    """
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401
        
    data = request.get_json()
    amount = float(data.get("amount", 0))
    
    username = session["user"]
    
    # Find the user
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Find or create retirement account
    retirement_account = RetirementAccount.query.filter_by(user_id=user.id).first()
    
    if not retirement_account:
        # Create a new retirement account with default values
        retirement_account = RetirementAccount(
            user_id=user.id,
            personal_funds=10000.0,
            retirement_balance=0.0
        )
        db.session.add(retirement_account)
        db.session.commit()
    
    if amount <= 0:
        return jsonify({
            "message": "Invalid contribution amount!", 
            "funds": retirement_account.personal_funds,
            "401k_balance": retirement_account.retirement_balance
        }), 400
    
    if amount > retirement_account.personal_funds:
        return jsonify({
            "message": "Insufficient personal funds for this contribution!", 
            "funds": retirement_account.personal_funds,
            "401k_balance": retirement_account.retirement_balance
        }), 400

    try:
        company_match = amount * 0.5
        total_contribution = amount + company_match

        if retirement_account.personal_funds - amount < 0:
            return jsonify({
                "message": "Contribution would result in negative balance!",
                "funds": retirement_account.personal_funds,
                "401k_balance": retirement_account.retirement_balance
            }), 400
        retirement_account.personal_funds -= amount
        retirement_account.retirement_balance += total_contribution
        
        db.session.commit()

        time.sleep(2)  # Simulate processing time

        return jsonify({
            "message": f"Contributed ${amount}. Employer matched ${company_match}!",
            "funds": retirement_account.personal_funds,
            "401k_balance": retirement_account.retirement_balance
        }), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            "message": f"Database error: {str(e)}", 
            "funds": retirement_account.personal_funds,
            "401k_balance": retirement_account.retirement_balance
        }), 500


@retirement_bp.route("/reset", methods=["POST"])
def reset_account() -> Tuple[Dict[str, Any], int]:
    """
    Reset the retirement account to default values.
    
    Returns:
        Tuple[Dict[str, Any], int]: JSON response with reset confirmation and status code
    """
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401
        
    username = session["user"]
    
    # Find the user
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Find retirement account
    retirement_account = RetirementAccount.query.filter_by(user_id=user.id).first()
    
    if not retirement_account:
        return jsonify({
            "message": "Account not found!", 
            "funds": 0,
            "401k_balance": 0
        }), 404
    
    try:
        retirement_account.personal_funds = 10000.0
        retirement_account.retirement_balance = 0.0
        db.session.commit()
        
        return jsonify({
            "message": "Account reset successfully!",
            "funds": retirement_account.personal_funds,
            "401k_balance": retirement_account.retirement_balance
        }), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            "message": f"Database error: {str(e)}", 
            "funds": retirement_account.personal_funds,
            "401k_balance": retirement_account.retirement_balance
        }), 500