import re
import time
from collections import defaultdict, deque
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from . import db
from .models import User

auth_bp = Blueprint("auth", __name__)
_attempts = defaultdict(deque)


def valid_csrf():
    return request.form.get("csrf_token") == session.get("csrf_token")


def rate_limited():
    key = request.remote_addr or "local"
    entries = _attempts[key]
    cutoff = time.time() - 60
    while entries and entries[0] < cutoff:
        entries.popleft()
    if len(entries) >= 12:
        return True
    entries.append(time.time())
    return False


def username_is_valid(username):
    return bool(re.fullmatch(r"[A-Za-z0-9_]{3,20}", username or ""))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if not valid_csrf():
            flash("Your form expired. Please try again.", "error")
        elif rate_limited():
            flash("Too many attempts. Please wait a minute.", "error")
        else:
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            confirm = request.form.get("confirm_password", "")
            if not username_is_valid(username):
                flash("Username must be 3–20 letters, numbers, or underscores.", "error")
            elif len(password) < 8:
                flash("Password must be at least 8 characters.", "error")
            elif password != confirm:
                flash("Passwords do not match.", "error")
            elif User.query.filter(db.func.lower(User.username) == username.lower()).first():
                flash("Username already exists.", "error")
            else:
                user = User(username=username, password_hash=generate_password_hash(password))
                db.session.add(user)
                db.session.commit()
                session.clear()
                session["user_id"] = user.id
                flash("Account created. Let’s play!", "success")
                return redirect(url_for("main.game"))
    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if not valid_csrf():
            flash("Your form expired. Please try again.", "error")
        elif rate_limited():
            flash("Too many attempts. Please wait a minute.", "error")
        else:
            user = User.query.filter(db.func.lower(User.username) == request.form.get("username", "").strip().lower()).first()
            if not user or not check_password_hash(user.password_hash, request.form.get("password", "")):
                flash("Invalid username or password.", "error")
            else:
                session.clear()
                session["user_id"] = user.id
                return redirect(url_for("main.game"))
    return render_template("login.html")


@auth_bp.post("/logout")
def logout():
    if valid_csrf():
        session.clear()
    return redirect(url_for("main.index"))
