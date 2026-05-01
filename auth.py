# auth.py
# Flask Blueprint — Register, Login, Logout
# Database: SQLite via Flask-SQLAlchemy
# Passwords: hashed with werkzeug

from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from database import db, User

auth = Blueprint("auth", __name__, url_prefix="/auth")


# ── REGISTER ─────────────────────────────────────────────
@auth.route("/register", methods=["POST"])
def register():
    data     = request.get_json()
    username = data.get("username", "").strip()
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not username or not email or not password:
        return jsonify({"error": "All fields are required."}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "An account with this email already exists."}), 409

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username is already taken."}), 409

    new_user = User(
        username      = username,
        email         = email,
        password_hash = generate_password_hash(password)
    )
    db.session.add(new_user)
    db.session.commit()

    session["user_id"]  = new_user.id
    session["username"] = new_user.username

    return jsonify({"message": "Account created successfully.", "username": username}), 201


# ── LOGIN ────────────────────────────────────────────────
@auth.route("/login", methods=["POST"])
def login():
    data     = request.get_json()
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password."}), 401

    session["user_id"]  = user.id
    session["username"] = user.username

    return jsonify({"message": "Logged in successfully.", "username": user.username}), 200


# ── LOGOUT ───────────────────────────────────────────────
@auth.route("/logout")
def logout():
    session.clear()
    return redirect("/auth/login-page")


# ── LOGIN PAGE ───────────────────────────────────────────
@auth.route("/login-page")
def login_page():
    if "user_id" in session:
        return redirect("/")
    return render_template("auth.html")


# ── SESSION CHECK ─────────────────────────────────────────
@auth.route("/me")
def me():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    return jsonify({"user_id": session["user_id"], "username": session["username"]})