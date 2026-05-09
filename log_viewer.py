# log_viewer.py
# Simple CLI tool to read and tail your log files
# Usage:
#   python log_viewer.py              → shows today's app log
#   python log_viewer.py auth         → shows auth log
#   python log_viewer.py estimates    → shows estimates log
#   python log_viewer.py errors       → shows errors log
#   python log_viewer.py auth 50      → shows last 50 lines of auth log
#   python log_viewer.py watch        → live tail of app log (Ctrl+C to stop)

import sys
import os
import time
from datetime import datetime

LOG_FILES = {
    "app":       f"logs/app_{datetime.now().strftime('%Y-%m-%d')}.log",
    "auth":      "logs/auth.log",
    "estimates": "logs/estimates.log",
    "errors":    "logs/errors.log",
}

# Colour codes for terminal
COLOURS = {
    "INFO":    "\033[36m",   # cyan
    "WARNING": "\033[33m",   # yellow
    "ERROR":   "\033[31m",   # red
    "RESET":   "\033[0m"
}

def colourise(line):
    for level, colour in COLOURS.items():
        if f"] {level}" in line:
            return f"{colour}{line}{COLOURS['RESET']}"
    return line

def print_log(filepath, lines=100):
    if not os.path.exists(filepath):
        print(f"Log file not found: {filepath}")
        return
    with open(filepath, "r", encoding="utf-8") as f:
        all_lines = f.readlines()
    for line in all_lines[-lines:]:
        print(colourise(line.rstrip()))

def watch_log(filepath, interval=1.0):
    """Live tail — prints new lines as they appear."""
    print(f"Watching {filepath} — press Ctrl+C to stop\n")
    if not os.path.exists(filepath):
        print(f"Log file not found: {filepath}")
        return
    with open(filepath, "r", encoding="utf-8") as f:
        f.seek(0, 2)  # go to end of file
        try:
            while True:
                line = f.readline()
                if line:
                    print(colourise(line.rstrip()))
                else:
                    time.sleep(interval)
        except KeyboardInterrupt:
            print("\nStopped watching.")

def print_summary():
    """Print a quick summary of line counts across all logs."""
    print("\n── Log Summary ─────────────────────────────")
    for name, path in LOG_FILES.items():
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            errors   = sum(1 for l in lines if "] ERROR" in l)
            warnings = sum(1 for l in lines if "] WARNING" in l)
            print(
                f"  {name:<12} {len(lines):>5} lines | "
                f"{warnings} warnings | {errors} errors"
            )
        else:
            print(f"  {name:<12} — not created yet")
    print("─────────────────────────────────────────────\n")

if __name__ == "__main__":
    args = sys.argv[1:]

    if not args:
        print_summary()
        print_log(LOG_FILES["app"])

    elif args[0] == "watch":
        target = args[1] if len(args) > 1 else "app"
        watch_log(LOG_FILES.get(target, LOG_FILES["app"]))

    elif args[0] == "summary":
        print_summary()

    else:
        target = args[0]
        n_lines = int(args[1]) if len(args) > 1 else 100
        filepath = LOG_FILES.get(target)
        if filepath:
            print_log(filepath, n_lines)
        else:
            print(f"Unknown log: '{target}'")
            print(f"Available: {', '.join(LOG_FILES.keys())}")
