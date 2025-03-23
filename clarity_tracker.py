# clarity_tracker.py
import os
import json
from datetime import datetime

# === Get path to user-specific clarity history ===
def get_history_path(user_id):
    path = f"user_data/{user_id}/clarity_history.json"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path

# === Log changes in clarity over time ===
def log_clarity_change(user_id, source="manual"):
    from user_memory import load_user_clarity  # Import here to avoid circular import

    current_clarity = load_user_clarity(user_id)
    log_path = get_history_path(user_id)

    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            history = json.load(f)
    else:
        history = []

    history.append({
        "timestamp": datetime.utcnow().isoformat(),
        "source": source,
        "clarity": current_clarity
    })

    with open(log_path, "w") as f:
        json.dump(history, f, indent=2)

# === Load clarity history ===
def load_clarity_history(user_id):
    path = get_history_path(user_id)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []
