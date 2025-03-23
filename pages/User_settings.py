# pages/User_Settings.py
import streamlit as st
import os
import json

st.set_page_config(page_title="User Settings", page_icon="🌐")
st.title("🔐 MirrorMe — User Settings")

# === 🔒 Require Login ===
if "user" not in st.session_state:
    st.warning("🔒 Please log in to access settings.")
    st.stop()

user_id = st.session_state["user"]["localId"]
settings_path = f"user_data/{user_id}/settings.json"
os.makedirs(os.path.dirname(settings_path), exist_ok=True)

# === Load Settings with Safe Defaults ===
def load_settings():
    default = {
        "dark_mode": False,
        "voice_id": "3Tjd0DlL3tjpqnkvDu9j",
        "enable_voice_response": True
    }
    if os.path.exists(settings_path):
        with open(settings_path, "r") as f:
            loaded = json.load(f)
            default.update(loaded)  # Fill in any missing keys
    return default

def save_settings(settings):
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)

settings = load_settings()

# === UI ===
st.markdown("### ⚙️ Personalization")

settings["dark_mode"] = st.toggle("🌜 Enable Dark Mode", value=settings.get("dark_mode", False))
settings["enable_voice_response"] = st.toggle("🔊 Enable Voice Output", value=settings.get("enable_voice_response", True))
settings["voice_id"] = st.text_input("🎤 Preferred Voice ID", value=settings.get("voice_id", ""))

if st.button("🔄 Save Settings"):
    save_settings(settings)
    st.success("✅ Settings saved!")
