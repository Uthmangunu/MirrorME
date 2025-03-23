# clarity_tracker.py
import json
import os
from datetime import datetime
from mirror_feedback import load_clarity

def log_clarity_change(source="unspecified"):
    clarity = load_clarity()
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "clarity": clarity,
        "source": source
    }
    os.makedirs("clarity_logs", exist_ok=True)
    log_path = "clarity_logs/history.json"

    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            history = json.load(f)
    else:
        history = []

    history.append(log_entry)

    with open(log_path, "w") as f:
        json.dump(history, f, indent=2)
