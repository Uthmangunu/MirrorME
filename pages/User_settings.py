# pages/User_Settings.py
import streamlit as st
import os
import json

st.set_page_config(page_title="User Settings", page_icon="🌐")
st.title("🔐 MirrorMe — User Settings")

if "user" not in st.session_state:
    st.warning("🔒 Please log in to access settings.")
    st.stop()

user_id = st.session_state["user"]["localId"]
settings_path = f"user_data/{user_id}/settings.json"
os.makedirs(os.path.dirname(settings_path), exist_ok=True)

# === Load Existing Settings or Defaults ===
def load_settings():
    if os.path.exists(settings_path):
        with open(settings_path, "r") as f:
            return json.load(f)
    return {
        "dark_mode": False,
        "voice_id": "3Tjd0DlL3tjpqnkvDu9j",
        "enable_voice_response": True
    }

def save_settings(settings):
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)

settings = load_settings()

# === UI ===
st.markdown("### ⚙️ Personalization")
settings["dark_mode"] = st.toggle("🌜 Enable Dark Mode", value=settings["dark_mode"])
settings["enable_voice_response"] = st.toggle("🔊 Enable Voice Output", value=settings["enable_voice_response"])
settings["voice_id"] = st.text_input("🎤 Preferred Voice ID", value=settings["voice_id"])

if st.button("🔄 Save Settings"):
    save_settings(settings)
    st.success("✅ Settings saved!")
