import streamlit as st
import os
import json
from user_memory import load_user_clarity
from long_memory import load_long_memory

st.set_page_config(page_title="User Profile", page_icon="👤")
st.title("👤 MirrorMe — Your Profile")

# === 🔐 Require Login ===
if "user" not in st.session_state:
    st.warning("🔒 You must log in first.")
    st.stop()

user_id = st.session_state["user"]["localId"]
settings_path = f"user_data/{user_id}/settings.json"

# === Load Settings ===
if os.path.exists(settings_path):
    with open(settings_path, "r") as f:
        settings = json.load(f)
else:
    settings = {
        "dark_mode": False,
        "voice_id": "3Tjd0DlL3tjpqnkvDu9j",
        "enable_voice_response": True
    }

# === 🌙 Apply Dark Mode ===
if settings.get("dark_mode"):
    st.markdown("""
        <style>
        .stApp { background-color: #0e1117; color: white; }
        </style>
    """, unsafe_allow_html=True)

# === 🎭 Personality Traits ===
st.subheader("🎭 Your Trait Snapshot")
clarity = load_user_clarity(user_id)

for trait, score in clarity.items():
    st.slider(trait.capitalize(), 0.0, 10.0, float(score), step=0.1, disabled=True)

# === 🧠 Long-Term Memory ===
st.subheader("🧠 MirrorMe's Long-Term Memory")
memory = load_long_memory(user_id)

st.markdown("**Core Values:**")
st.write(", ".join(memory.get("core_values", [])))

st.markdown("**Goals:**")
st.write(", ".join(memory.get("goals", [])))

st.markdown("**Personality Summary:**")
st.info(memory.get("personality_summary", "No summary found."))

# === ⚙️ Voice Preferences ===
st.subheader("🔊 Voice Preferences")
st.markdown(f"- **Voice ID:** `{settings.get('voice_id')}`")
st.markdown(f"- **Voice Response Enabled:** `{settings.get('enable_voice_response')}`")
