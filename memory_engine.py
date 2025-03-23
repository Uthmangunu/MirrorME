# memory_engine.py
import json
import os

MEMORY_FILE = "mirror_memory.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def update_memory(user_input, mirror_reply):
    memory = load_memory()
    memory.append({
        "user": user_input,
        "mirror": mirror_reply
    })
    save_memory(memory)
