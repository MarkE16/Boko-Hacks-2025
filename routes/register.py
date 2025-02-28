from flask import Blueprint, render_template, request, flash, redirect, url_for, session, current_app
from models.user import User
from extensions import db, mail  # Import db and mail from extensions.py
import random
import string
from flask_mail import Message
from utils.logger import log_registration
import requests
import json

register_bp = Blueprint("register", __name__)

def verify_hcaptcha(h_captcha_response, remote_ip=None):
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    secret = os.getenv("HCAPTCHA_SECRET")
    data = {
        'secret': secret,
        'response': h_captcha_response
    }
    
    if remote_ip:
        data['remoteip'] = remote_ip
    
    response = requests.post('https://api.hcaptcha.com/siteverify', data=data)
    result = json.loads(response.content)
    
    return result['success']


def generate_verification_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@register_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        h_captcha_response = request.form.get('h-captcha-response')
        client_ip = request.remote_addr

        if not verify_hcaptcha(h_captcha_response, client_ip):
            log_registration(success=False, username=username, reason="Invalid hCaptcha")
            flash("Invalid hCaptcha. Please try again.", "error")
            return redirect(url_for("register.register"))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            log_registration(success=False, username=username, reason="Username already exists")
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

        session.pop("verification_code", None)
        session.pop("username", None)
        session.pop("email", None)
        session.pop("password", None)

        log_registration(success=True, username=username)
        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("login.login"))

    return render_template("verify.html")

