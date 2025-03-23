import os
import json

MEMORY_FILE = "memory.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE) or os.path.getsize(MEMORY_FILE) == 0:
        return []  # return an empty memory if file doesn't exist or is empty
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []  # fallback if file is malformed

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def update_memory(user_input, reply):
    memory = load_memory()
    memory.append({
        "user": user_input,
        "mirror": reply
    })
    save_memory(memory)
