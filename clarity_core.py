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
        with open("clarity_data.json", "r") as f:
            return json.load(f)
    return default_data

def save_clarity(data):
    with open("clarity_data.json", "w") as f:
        json.dump(data, f, indent=2)
