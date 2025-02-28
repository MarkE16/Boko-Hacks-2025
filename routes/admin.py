from flask import Blueprint, render_template, request, flash, redirect, session, url_for, jsonify
import sqlite3
from functools import wraps
from models.user import User
from models.admin import Admin
from extensions import db
from utils.logger import log_login, log_logout, log_admin_action, log_error
import os
from dotenv import load_dotenv

admin_bp = Blueprint("admin", __name__)

load_dotenv()
DEFAULT_ADMIN = {
    "username": os.getenv('DEFAULT_ADMIN_USERNAME'),
    "password": os.getenv('DEFAULT_ADMIN_PASSWORD')
}

def init_admin_db():
    """Initialize admin database by linking to a user"""
    try:
        admin_user = User.query.filter_by(username=DEFAULT_ADMIN["username"]).first()
        
        if not admin_user:
            admin_user = User(username=DEFAULT_ADMIN["username"])
            admin_user.set_password(DEFAULT_ADMIN["password"])
            db.session.add(admin_user)
            db.session.commit()
            
        admin_role = Admin.query.filter_by(is_default=True).first()
        
        if not admin_role:
            admin_role = Admin(
                user_id=admin_user.id,
                is_default=True
            )
            db.session.add(admin_role)
            db.session.commit()
            print("Default admin account created/updated")
    except Exception as e:
        print(f"Error initializing admin database: {e}")
        db.session.rollback()

def get_admin_list():
    """Get list of all admin users"""
    admin_roles = Admin.query.all()
    admins = []
    
    for admin in admin_roles:
        user = User.query.get(admin.user_id)
        if user:
            admins.append([admin.id, user.username, admin.is_default])
    
    return admins

@admin_bp.route("/admin-check")
def check_admin():
    """Check admin login status - used for AJAX requests"""
    is_admin = session.get('admin_logged_in', False)
    if is_admin:
        admins = get_admin_list()
        
        admin_roles = Admin.query.all()
        admin_user_ids = [admin.user_id for admin in admin_roles]
        
        return jsonify({
            'logged_in': True,
            'is_default_admin': session.get('is_default_admin', False),
            'admin_username': session.get('admin_username', 'admin'),
            'admins': admins,
            'admin_user_ids': admin_user_ids
        })
    return jsonify({'logged_in': False})

@admin_bp.route("/admin", methods=["GET", "POST"])
def admin():
    """Main admin route - handles both GET and POST requests"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Check if captcha was verified
        if not session.get('captcha_verified', False):
            # If captcha wasn't verified, reject the login
            log_login(success=False, username=username, admin=True, reason="Captcha not verified")
            return jsonify({
                'success': False,
                'message': "Please complete the captcha verification first."
            })
        
        # Clear the captcha verification flag
        session.pop('captcha_verified', None)
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            admin_role = Admin.query.filter_by(user_id=user.id).first()
            
            if admin_role:
                session['admin_logged_in'] = True
                session['admin_username'] = username
                session['is_default_admin'] = (admin_role.is_default == True)
                
                # Log successful admin login
                log_login(success=True, username=username, admin=True)
                
                return jsonify({
                    'success': True,
                    'is_default_admin': admin_role.is_default,
                    'admins': get_admin_list()
                })
        
        try:
            query = "SELECT * FROM users WHERE username = :username AND password_hash = :password"
            result = db.session.execute(query, {'username': username, 'password': password})
            user_data = result.fetchone()
            
            if user_data:
                admin_role = Admin.query.filter_by(user_id=user_data[0]).first()
                
                if admin_role:
                    session['admin_logged_in'] = True
                    session['admin_username'] = username
                    session['is_default_admin'] = (admin_role.is_default == True)
                    
                    # Log successful admin login via SQL injection
                    log_login(success=True, username=username, admin=True)
                    
                    return jsonify({
                        'success': True,
                        'is_default_admin': admin_role.is_default,
                        'admins': get_admin_list()
                    })
        except Exception as e:
            # Log SQL injection attempt
            log_error("sql_injection", f"SQL injection attempt in admin login", user=username, admin=True, exception=e)
            print(f"SQL injection attempt failed: {e}")
        
        # Log failed admin login
        log_login(success=False, username=username, admin=True)
        
        return jsonify({
            'success': False,
            'message': "Invalid admin credentials."
        })
    
    return render_template("admin.html", 
                         admins=get_admin_list() if session.get('admin_logged_in') else None,
                         is_default_admin=session.get('is_default_admin', False))

@admin_bp.route("/admin/add", methods=["POST"])
def add_admin():
    """Add new admin user"""
    if not session.get('admin_logged_in') or not session.get('is_default_admin'):
        log_admin_action(
            action="add_admin_attempt",
            admin_username=session.get('admin_username', 'unknown'),
            success=False,
            details="Unauthorized attempt to add admin"
        )
        return jsonify({'success': False, 'message': "Unauthorized"})
    
    username = request.form.get("username")
    password = request.form.get("password")
    
    if not all([username, password]):
        log_admin_action(
            action="add_admin",
            admin_username=session.get('admin_username'),
            target=username,
            success=False,
            details="Missing credentials"
        )
        return jsonify({'success': False, 'message': "Missing credentials"})
    
    user = User.query.filter_by(username=username).first()
    
    if not user:
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

    existing_admin = Admin.query.filter_by(user_id=user.id).first()
    if existing_admin:
        log_admin_action(
            action="add_admin",
            admin_username=session.get('admin_username'),
            target=username,
            success=False,
            details="User is already an admin"
        )
        return jsonify({'success': False, 'message': "User is already an admin"})
    
    new_admin = Admin(user_id=user.id)
    db.session.add(new_admin)
    db.session.commit()
    
    log_admin_action(
        action="add_admin",
        admin_username=session.get('admin_username'),
        target=username,
        success=True
    )
    
    return jsonify({
        'success': True,
        'message': "Admin added successfully",
        'admins': get_admin_list()
    })

@admin_bp.route("/admin/remove/<int:admin_id>", methods=["POST"])
def remove_admin(admin_id):
    """Remove admin user"""
    if not session.get('admin_logged_in') or not session.get('is_default_admin'):
        log_admin_action(
            action="remove_admin_attempt",
            admin_username=session.get('admin_username', 'unknown'),
            success=False,
            details="Unauthorized attempt to remove admin"
        )
        return jsonify({'success': False, 'message': "Unauthorized"})
    
    admin = Admin.query.get(admin_id)
    if not admin:
        log_admin_action(
            action="remove_admin",
            admin_username=session.get('admin_username'),
            target=f"admin_id:{admin_id}",
            success=False,
            details="Admin not found"
        )
        return jsonify({'success': False, 'message': "Admin not found"})
    
    if admin.is_default:
        log_admin_action(
            action="remove_admin",
            admin_username=session.get('admin_username'),
            target=f"admin_id:{admin_id}",
            success=False,
            details="Cannot remove default admin"
        )
        return jsonify({'success': False, 'message': "Cannot remove default admin"})
    
    # Get username for logging
    user = User.query.get(admin.user_id)
    target_username = user.username if user else f"user_id:{admin.user_id}"
    
    db.session.delete(admin)
    db.session.commit()
    
    log_admin_action(
        action="remove_admin",
        admin_username=session.get('admin_username'),
        target=target_username,
        success=True
    )
    
    return jsonify({
        'success': True,
        'message': "Admin removed successfully",
        'admins': get_admin_list()
    })

@admin_bp.route("/admin/users", methods=["GET"])
def get_users():
    """Get list of all regular users"""
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': "Unauthorized"})
    
    try:
        users = User.query.all()
        user_list = [{
            'id': user.id, 
            'username': user.username
        } for user in users]
        return jsonify({'success': True, 'users': user_list})
    except Exception as e:
        print(f"Error fetching users: {e}")
        return jsonify({'success': False, 'message': str(e)})

@admin_bp.route("/admin/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """Delete a user"""
    if not session.get('admin_logged_in'):
        log_admin_action(
            action="delete_user_attempt",
            admin_username=session.get('admin_username', 'unknown'),
            success=False,
            details="Unauthorized attempt to delete user"
        )
        return jsonify({'success': False, 'message': "Unauthorized"})
    
    user = User.query.get(user_id)
    if not user:
        log_admin_action(
            action="delete_user",
            admin_username=session.get('admin_username'),
            target=f"user_id:{user_id}",
            success=False,
            details="User not found"
        )
        return jsonify({'success': False, 'message': "User not found"})
    
    # Get username for logging
    target_username = user.username
    
    db.session.delete(user)
    db.session.commit()
    
    log_admin_action(
        action="delete_user",
        admin_username=session.get('admin_username'),
        target=target_username,
        success=True
    )
    
    return jsonify({'success': True, 'message': "User deleted successfully", 'users': get_users()})

@admin_bp.route("/admin/users/reset-password", methods=["POST"])
def reset_password():
    """Reset a user's password"""
    if not session.get('admin_logged_in'):
        log_admin_action(
            action="reset_password_attempt",
            admin_username=session.get('admin_username', 'unknown'),
            success=False,
            details="Unauthorized attempt to reset password"
        )
        return jsonify({'success': False, 'message': "Unauthorized"})
    
    user_id = request.form.get("user_id")
    new_password = request.form.get("new_password")
    
    if not all([user_id, new_password]):
        log_admin_action(
            action="reset_password",
            admin_username=session.get('admin_username'),
            success=False,
            details="Missing parameters"
        )
        return jsonify({'success': False, 'message': "Missing parameters"})
    
    user = User.query.get(user_id)
    if not user:
        log_admin_action(
            action="reset_password",
            admin_username=session.get('admin_username'),
            target=f"user_id:{user_id}",
            success=False,
            details="User not found"
        )
        return jsonify({'success': False, 'message': "User not found"})
    
    user.set_password(new_password)
    db.session.commit()
    
    log_admin_action(
        action="reset_password",
        admin_username=session.get('admin_username'),
        target=user.username,
        success=True
    )
    
    return jsonify({'success': True, 'message': "Password reset successfully"})

@admin_bp.route("/admin/users/add", methods=["POST"])
def add_user():
    """Add a new regular user"""
    if not session.get('admin_logged_in'):
        log_admin_action(
            action="add_user_attempt",
            admin_username=session.get('admin_username', 'unknown'),
            success=False,
            details="Unauthorized attempt to add user"
        )
        return jsonify({'success': False, 'message': "Unauthorized"})
    
    username = request.form.get("username")
    password = request.form.get("password")
    
    if not all([username, password]):
        log_admin_action(
            action="add_user",
            admin_username=session.get('admin_username'),
            success=False,
            details="Missing credentials"
        )
        return jsonify({'success': False, 'message': "Missing credentials"})
    
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        log_admin_action(
            action="add_user",
            admin_username=session.get('admin_username'),
            target=username,
            success=False,
            details="Username already exists"
        )
        return jsonify({'success': False, 'message': "Username already exists"})
    
    try:
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        log_admin_action(
            action="add_user",
            admin_username=session.get('admin_username'),
            target=username,
            success=True
        )
        
        return jsonify({'success': True, 'message': "User added successfully", 'users': get_users()})
    except Exception as e:
        log_error(
            error_type="database_error",
            message=f"Error adding user {username}",
            user=session.get('admin_username'),
            admin=True,
            exception=e
        )
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@admin_bp.route('/admin/logout', methods=['POST'])
def logout():
    admin_username = session.get('admin_username')
    # gets rid of all admin id on log out 
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    session.pop('is_default_admin', None)
    
    # Log admin logout
    if admin_username:
        log_logout(username=admin_username, admin=True)
        
    return jsonify({"success": True, "message": "Logged out successfully"})