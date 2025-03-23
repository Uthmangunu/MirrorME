# clarity_core.py
import json
import os

def load_clarity():
    default_data = {
        "humor": 5,
        "empathy": 5,
        "ambition": 5,
        "flirtiness": 5
    }
    if os.path.exists("clarity_data.json"):
        try:
            with open("clarity_data.json", "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            # If the file is empty or corrupted, reset it
            save_clarity(default_data)
            return default_data
    return default_data
