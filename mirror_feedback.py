# mirror_feedback.py
from clarity_core import load_clarity
import json
import os
from clarity_core import load_clarity, save_clarity
from clarity_tracker import log_clarity_change



# === 🔁 Feedback-Based Personality Adjustment System ===

# --- Load Existing Clarity Profile or Initialize Default ---
def load_clarity():
    default_data = {
        "humor": 5,
        "empathy": 5,
        "ambition": 5,
        "flirtiness": 5
    }
    if os.path.exists("clarity_data.json"):
        with open("clarity_data.json", "r") as f:
            return json.load(f)
    return default_data

# --- Save Updated Clarity Profile ---
def save_clarity(data):
    with open("clarity_data.json", "w") as f:
        json.dump(data, f, indent=2)
        log_clarity_change(data)


# --- Adjust Clarity Data Based on Feedback ---
def apply_feedback(tweak, clarity):
    if tweak == "Too blunt":
        clarity["empathy"] = min(10, clarity["empathy"] + 0.5)
    elif tweak == "Too soft":
        clarity["empathy"] = max(0, clarity["empathy"] - 0.5)
    elif tweak == "Not witty enough":
        clarity["humor"] = max(0, clarity["humor"] - 0.5)
    elif tweak == "Too robotic":
        clarity["flirtiness"] = min(10, clarity["flirtiness"] + 0.5)
    elif tweak == "Too emotional":
        clarity["flirtiness"] = max(0, clarity["flirtiness"] - 0.5)
