from flask import Blueprint, render_template, request, flash, redirect, session, url_for
from models.user import User
from extensions import db
from utils.logger import log_login, log_logout

login_bp = Blueprint("login", __name__)

@login_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session["user"] = user.username
            flash("Login successful!", "success")
            # Log successful login
            log_login(success=True, username=username)
            return redirect(url_for("hub.hub"))
        else:
            # Log failed login attempt
            log_login(success=False, username=username)
            flash("Invalid username or password.", "error")

    return render_template("login.html")

@login_bp.route("/logout")
def logout():
    username = session.get("user")
    session.pop("user", None)
    session.pop('_flashes',None)
    # Log logout if user was logged in
    if username:
        log_logout(username=username)
    flash("You have been logged out.", "info")
    return redirect(url_for("login.login"))
