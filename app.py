# app.py
# Main Flask entry point — wires everything together

from flask import Flask, redirect, session
from database import db
from auth import auth
from routing import main

app = Flask(__name__)

# ── CONFIG ───────────────────────────────────────────────
app.secret_key = "shisela-nathi-lab-secret-2024"   # Change this in production!
app.config["SQLALCHEMY_DATABASE_URI"]        = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ── INIT DB ──────────────────────────────────────────────
db.init_app(app)

with app.app_context():
    db.create_all()   # Creates users.db + users table on first run
    print("✅ Database ready")

# ── REGISTER BLUEPRINTS ──────────────────────────────────
app.register_blueprint(auth)   # /auth/login-page, /auth/register, /auth/login, /auth/logout
app.register_blueprint(main)   # /, /generate


# ── PROTECT MAIN ROUTES ──────────────────────────────────
@app.before_request
def require_login():
    from flask import request
    open_prefixes = ["/auth/", "/static/"]
    if any(request.path.startswith(p) for p in open_prefixes):
        return
    if "user_id" not in session:
        return redirect("/auth/login-page")


if __name__ == "__main__":
    app.run(debug=True)