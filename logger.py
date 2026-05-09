# logger.py
# Central logging setup for Shisela Nathi Lab
# Writes separate log files per concern + console output

import logging
import os
from datetime import datetime

# ── CREATE LOGS FOLDER ───────────────────────────────────
os.makedirs("logs", exist_ok=True)

# ── LOG FILE PATHS ───────────────────────────────────────
LOG_FILE      = f"logs/app_{datetime.now().strftime('%Y-%m-%d')}.log"
ERROR_FILE    = "logs/errors.log"
AUTH_FILE     = "logs/auth.log"
ESTIMATE_FILE = "logs/estimates.log"

# ── FORMATTER ────────────────────────────────────────────
formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)-8s | %(name)-10s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def get_logger(name, log_file, level=logging.INFO):
    """Create a named logger writing to file + console."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent duplicate handlers on Flask reload
    if logger.handlers:
        return logger

    # File handler
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(level)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger

# ── NAMED LOGGERS (import these wherever needed) ─────────
app_logger      = get_logger("app",      LOG_FILE)
auth_logger     = get_logger("auth",     AUTH_FILE)
estimate_logger = get_logger("estimate", ESTIMATE_FILE)
error_logger    = get_logger("error",    ERROR_FILE, level=logging.ERROR)

app_logger.info("=" * 60)
app_logger.info("Shisela Nathi Lab — Logger initialised")
app_logger.info("=" * 60)
