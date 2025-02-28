from flask import Blueprint, render_template, request, flash, redirect, url_for, session, current_app
from models.user import User
from extensions import db, mail  # Import db and mail from extensions.py
import random
import string
from flask_mail import Message

register_bp = Blueprint("register", __name__)

def generate_verification_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@register_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        captcha_response = request.form.get("captcha")
        stored_captcha = session.get("captcha_text")

        if not stored_captcha or captcha_response.upper() != stored_captcha:
            flash("Invalid CAPTCHA. Please try again.", "error")
            return redirect(url_for("register.register"))

        session.pop("captcha_text", None)

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists. Please choose a different one.", "error")
            return redirect(url_for("register.register"))

        verification_code = generate_verification_code()
        session['verification_code'] = verification_code
        session['username'] = username
        session['email'] = email
        session['password'] = password

        # Send verification code to user's email
        msg = Message("Your Verification Code", recipients=[email], sender=current_app.config['MAIL_DEFAULT_SENDER'])
        msg.body = f"Your verification code is {verification_code}"
        mail.send(msg)

        return redirect(url_for("register.verify"))

    return render_template("register.html")

@register_bp.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        verification_code = request.form.get("verification_code")
        stored_code = session.get("verification_code")

        if verification_code != stored_code:
            flash("Invalid verification code. Please try again.", "error")
            return redirect(url_for("register.verify"))

        username = session.get("username")
        email = session.get("email")
        password = session.get("password")

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        session.pop("verification_code", None)
        session.pop("username", None)
        session.pop("email", None)
        session.pop("password", None)

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("login.login"))

    return render_template("verify.html")

