from firebase_client import get_doc, save_doc

# === 🔧 Load User Settings ===
def load_user_settings(user_id):
    data = get_doc("settings", user_id)
    return {
        "dark_mode": data.get("dark_mode", False),
        "voice_id": data.get("voice_id", "3Tjd0DlL3tjpqnkvDu9j"),
        "enable_voice_response": data.get("enable_voice_response", True)
    }

# === 💾 Save User Settings ===
def save_user_settings(user_id, settings_data):
    save_doc("settings", user_id, settings_data)
