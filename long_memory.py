from firebase_client import get_doc, save_doc

# === 🧠 Load Long-Term Memory ===
def load_long_memory(user_id):
    data = get_doc("long_memory", user_id)
    return {
        "core_values": data.get("core_values", []),
        "goals": data.get("goals", []),
        "personality_summary": data.get("personality_summary", "No summary found.")
    }

# === 🧠 Save Long-Term Memory ===
def save_long_memory(user_id, memory_data):
    save_doc("long_memory", user_id, memory_data)
