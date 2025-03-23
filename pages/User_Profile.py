import streamlit as st
import json
import os
from user_memory import load_user_clarity
from long_memory import load_long_memory

st.set_page_config(page_title="User Profile", page_icon="👤")
st.title("👤 MirrorMe — User Profile")

# 🔐 Require login
if "user" not in st.session_state:
    st.warning("🔒 Please log in to view your profile.")
    st.stop()

user = st.session_state["user"]
user_id = user["localId"]

# === ⚙️ Load Settings ===
settings_path = f"user_data/{user_id}/settings.json"
if os.path.exists(settings_path):
    with open(settings_path, "r") as f:
        settings = json.load(f)
else:
    settings = {
        "dark_mode": False,
        "voice_id": "3Tjd0DlL3tjpqnkvDu9j",
        "enable_voice_response": True
    }

# === 🧠 Load Clarity and Long-Term Memory ===
clarity = load_user_clarity(user_id)
long_memory = load_long_memory(user_id)

# === 🧾 Basic Info ===
st.markdown("### 🪪 Basic Info")
st.write(f"**User ID:** `{user_id}`")
st.write(f"**Email:** `{user.get('email', 'N/A')}`")

# === 🔧 Settings Overview ===
st.markdown("### ⚙️ Preferences")
st.write(f"**Dark Mode:** {'✅ Enabled' if settings['dark_mode'] else '❌ Disabled'}")
st.write(f"**Voice ID:** `{settings['voice_id']}`")
st.write(f"**Voice Response:** {'✅ Enabled' if settings['enable_voice_response'] else '❌ Disabled'}")

# === 🎯 Clarity Trait Snapshot ===
st.markdown("### 🎯 Clarity Trait Snapshot")
for trait, score in clarity.items():
    st.slider(trait.capitalize(), 0, 10, float(score), disabled=True)

# === 🧠 Long-Term Memory ===
st.markdown("### 🧠 Long-Term Memory Summary")
st.write(f"**Core Values:** {', '.join(long_memory.get('core_values', []))}")
st.write(f"**Goals:** {', '.join(long_memory.get('goals', []))}")
st.write("**Personality Summary:**")
st.text_area("Summary", long_memory.get("personality_summary", "Not yet set."), height=120, disabled=True)
