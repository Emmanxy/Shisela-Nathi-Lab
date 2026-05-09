# app.py
# Main Flask entry point — wires everything together

from flask import Flask, redirect, session, request, jsonify
from database import db
from auth import auth
from routing import main
from logger import app_logger, error_logger

app = Flask(__name__)

# ── CONFIG ───────────────────────────────────────────────
app.secret_key = "shisela-nathi-lab-secret-2024"   # Change in production!
app.config["SQLALCHEMY_DATABASE_URI"]        = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ── INIT DB ──────────────────────────────────────────────
db.init_app(app)

with app.app_context():
    db.create_all()
    app_logger.info("Database initialised — users.db ready")

# ── REGISTER BLUEPRINTS ──────────────────────────────────
app.register_blueprint(auth)
app.register_blueprint(main)
app_logger.info("Blueprints registered: auth, main")


# ── PROTECT MAIN ROUTES ──────────────────────────────────
@app.before_request
def require_login():
    open_prefixes = ["/auth/", "/static/"]
    if any(request.path.startswith(p) for p in open_prefixes):
        return
    if "user_id" not in session:
        app_logger.info(
            f"UNAUTHENTICATED ACCESS | path={request.path} | ip={request.remote_addr}"
        )
        return redirect("/auth/login-page")


# ── LOG EVERY REQUEST ────────────────────────────────────
@app.after_request
def log_request(response):
    if not request.path.startswith("/static/"):
        app_logger.info(
            f"{request.method} {request.path} | "
            f"status={response.status_code} | "
            f"user={session.get('username', 'anonymous')} | "
            f"ip={request.remote_addr}"
        )
    return response


# ── HANDLE 404 ───────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    app_logger.warning(
        f"404 NOT FOUND | path={request.path} | ip={request.remote_addr}"
    )
    return jsonify({"error": "Route not found."}), 404


# ── HANDLE ALL UNHANDLED EXCEPTIONS ──────────────────────
@app.errorhandler(Exception)
def handle_exception(e):
    error_logger.error(
        f"UNHANDLED EXCEPTION | {request.method} {request.path} | "
        f"user={session.get('username', 'anonymous')} | "
        f"ip={request.remote_addr} | error={str(e)}",
        exc_info=True
    )
    return jsonify({"error": "An unexpected server error occurred."}), 500


if __name__ == "__main__":
    app_logger.info("Starting Flask development server on port 5000...")
    app.run(host="0.0.0.0", port=5000, debug=True)