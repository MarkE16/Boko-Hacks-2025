from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from models.user import User
from extensions import db
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


@register_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
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

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        log_registration(success=True, username=username)
        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("login.login"))

    return render_template("register.html")
