import os
import json

def get_path(user_id):
    return f"user_data/{user_id}/long_memory.json"

def load_long_memory(user_id):
    path = get_path(user_id)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {
        "core_values": [],
        "goals": [],
        "personality_summary": "Not yet defined."
    }

def save_long_memory(user_id, data):
    path = get_path(user_id)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def append_to_long_memory(user_id, key, value):
    data = load_long_memory(user_id)
    if key in data and isinstance(data[key], list):
        data[key].append(value)
    else:
        data[key] = value
    save_long_memory(user_id, data)
