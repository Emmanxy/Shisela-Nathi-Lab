# auth.py
# Flask Blueprint — Register, Login, Logout
# Passwords hashed with werkzeug | Users stored in SQLite

from flask import Blueprint, request, jsonify, session, redirect, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from database import db, User
from logger import auth_logger, error_logger

auth = Blueprint("auth", __name__, url_prefix="/auth")


# ── REGISTER ─────────────────────────────────────────────
@auth.route("/register", methods=["POST"])
def register():
    data     = request.get_json()
    username = data.get("username", "").strip()
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    auth_logger.info(f"REGISTER ATTEMPT | email={email} | username={username}")

    if not username or not email or not password:
        auth_logger.warning(f"REGISTER REJECTED | reason=missing fields | email={email}")
        return jsonify({"error": "All fields are required."}), 400

    if len(password) < 6:
        auth_logger.warning(f"REGISTER REJECTED | reason=password too short | email={email}")
        return jsonify({"error": "Password must be at least 6 characters."}), 400

    if User.query.filter_by(email=email).first():
        auth_logger.warning(f"REGISTER REJECTED | reason=duplicate email | email={email}")
        return jsonify({"error": "An account with this email already exists."}), 409

    if User.query.filter_by(username=username).first():
        auth_logger.warning(f"REGISTER REJECTED | reason=duplicate username | username={username}")
        return jsonify({"error": "Username is already taken."}), 409

    try:
        new_user = User(
            username      = username,
            email         = email,
            password_hash = generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()

        session["user_id"]  = new_user.id
        session["username"] = new_user.username

        auth_logger.info(
            f"REGISTER SUCCESS | user_id={new_user.id} | "
            f"username={username} | email={email}"
        )
        return jsonify({"message": "Account created successfully.", "username": username}), 201

    except Exception as e:
        db.session.rollback()
        error_logger.error(f"REGISTER ERROR | email={email} | error={str(e)}", exc_info=True)
        return jsonify({"error": "Registration failed. Please try again."}), 500


# ── LOGIN ────────────────────────────────────────────────
@auth.route("/login", methods=["POST"])
def login():
    data     = request.get_json()
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    auth_logger.info(f"LOGIN ATTEMPT | email={email} | ip={request.remote_addr}")

    if not email or not password:
        auth_logger.warning(f"LOGIN REJECTED | reason=missing fields | email={email}")
        return jsonify({"error": "Email and password are required."}), 400

    try:
        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            auth_logger.warning(
                f"LOGIN FAILED | reason=invalid credentials | "
                f"email={email} | ip={request.remote_addr}"
            )
            return jsonify({"error": "Invalid email or password."}), 401

        session["user_id"]  = user.id
        session["username"] = user.username

        auth_logger.info(
            f"LOGIN SUCCESS | user_id={user.id} | "
            f"username={user.username} | ip={request.remote_addr}"
        )
        return jsonify({"message": "Logged in successfully.", "username": user.username}), 200

    except Exception as e:
        error_logger.error(f"LOGIN ERROR | email={email} | error={str(e)}", exc_info=True)
        return jsonify({"error": "Login failed. Please try again."}), 500


# ── LOGOUT ───────────────────────────────────────────────
@auth.route("/logout")
def logout():
    user_id  = session.get("user_id",  "unknown")
    username = session.get("username", "unknown")
    auth_logger.info(
        f"LOGOUT | user_id={user_id} | username={username} | ip={request.remote_addr}"
    )
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
    return jsonify({
        "user_id":  session["user_id"],
        "username": session["username"]
    })