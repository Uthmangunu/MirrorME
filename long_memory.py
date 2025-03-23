# long_memory.py

import json
import os

LONG_MEMORY_FILE = "long_memory.json"

def load_long_memory():
    if not os.path.exists(LONG_MEMORY_FILE):
        return []
    with open(LONG_MEMORY_FILE, "r") as f:
        return json.load(f)

def save_long_memory(data):
    with open(LONG_MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def append_to_long_memory(entry):
    data = load_long_memory()
    data.append(entry)
    save_long_memory(data)
