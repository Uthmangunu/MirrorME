# pages/User_Settings.py

import streamlit as st
from user_settings import load_user_settings, save_user_settings

st.set_page_config(page_title="User Settings", page_icon="🌐")
st.title("🔐 MirrorMe — User Settings")

# === Ensure User Logged In ===
if "user" not in st.session_state:
    st.warning("🔒 Please log in to access your settings.")
    st.stop()

# === Load Current Settings ===
user_id = st.session_state["user"]["localId"]
settings = load_user_settings(user_id)

# === User Interface ===
st.subheader("🎛 Preferences")
settings["dark_mode"] = st.toggle("🌙 Enable Dark Mode", value=settings["dark_mode"])
settings["voice_id"] = st.text_input("🎤 Preferred Voice ID", value=settings["voice_id"])

# === Save Button ===
if st.button("💾 Save Settings"):
    save_user_settings(user_id, settings)
    st.success("✅ Settings saved!")

# === Optional Visual Feedback ===
st.markdown("---")
st.caption("Your preferences are applied across your MirrorMe experience.")
