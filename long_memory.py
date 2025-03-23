# long_memory.py
import os
import json

def _get_memory_path(user_id):
    path = f"user_data/{user_id}/long_memory.json"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path

def load_long_memory(user_id):
    path = _get_memory_path(user_id)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {
        "core_values": [],
        "goals": [],
        "personality_summary": ""
    }

def save_long_memory(user_id, memory):
    path = _get_memory_path(user_id)
    with open(path, "w") as f:
        json.dump(memory, f, indent=2)

def append_to_long_memory(user_id, key, value):
    memory = load_long_memory(user_id)
    if key == "core_values" or key == "goals":
        if value not in memory[key]:
            memory[key].append(value)
    elif key == "personality_summary":
        memory[key] = value  # Replace for now
    save_long_memory(user_id, memory)
