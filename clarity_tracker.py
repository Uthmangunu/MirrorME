# clarity_tracker.py
from datetime import datetime
import os
import json
from clarity_core import load_clarity

def log_clarity_change(source="unknown"):
    clarity = load_clarity()
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "source": source,
        "clarity": clarity
    }

    os.makedirs("clarity_logs", exist_ok=True)
    path = "clarity_logs/history.json"

    history = []
    if os.path.exists(path):
        with open(path, "r") as f:
            try:
                history = json.load(f)
            except:
                history = []

    history.append(log_entry)
    with open(path, "w") as f:
        json.dump(history, f, indent=2)
