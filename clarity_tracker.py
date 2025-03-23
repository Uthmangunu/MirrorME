# clarity_tracker.py
import os
import json
from datetime import datetime

def log_clarity_change(current_data):
    os.makedirs("clarity_logs", exist_ok=True)
    log_path = "clarity_logs/history.json"

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "clarity": current_data
    }

    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            data = json.load(f)
    else:
        data = []

    data.append(log_entry)

    with open(log_path, "w") as f:
        json.dump(data, f, indent=2)
