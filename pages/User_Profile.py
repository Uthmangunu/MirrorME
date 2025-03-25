import streamlit as st
import os
import json
from user_memory import load_user_clarity
from long_memory import load_long_memory
from clarity_core import load_clarity, save_clarity
from firebase_client import save_doc, delete_doc
from components.feedback_button import feedback_button
feedback_button(user_id)

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

# === 🨠 Mirror Summary Card ===
st.subheader("🔠 Mirror Identity")
clarity = load_clarity()
archetype = clarity.get("archetype")
archetype_meta = clarity.get("archetype_meta", {})

if archetype:
    emoji = archetype_meta.get("emoji", "")
    desc = archetype_meta.get("desc", "")
    st.markdown(f"### {emoji} {archetype}")
    st.caption(desc)
    if st.button("🔄 Retake Archetype Test"):
        st.switch_page("Welcome.py")
else:
    st.info("You haven’t taken the Archetype Test yet.")
    if st.button("🎯 Take Archetype Quiz Now"):
        st.switch_page("Welcome.py")

# === 📈 Clarity Level & XP ===
st.subheader("📈 Clarity Level")
level = clarity.get("clarity_level", 0)
total_xp = clarity.get("total_xp", 0)
xp_to_next = clarity.get("xp_to_next_level", 100)

st.markdown(f"**Level {level}** — XP: {total_xp} / {xp_to_next}")
if xp_to_next > 0:
    st.progress(min(total_xp / xp_to_next, 1.0))
else:
    st.warning("Clarity leveling not initialized.")

# === 🎭 Trait Snapshot ===
st.subheader("🎭 Personality Traits")
traits = clarity.get("traits", {})
for trait, values in traits.items():
    st.slider(trait.capitalize(), 0.0, 100.0, float(values["score"]), step=1.0, disabled=True)

# === 🧠 Long-Term Memory ===
st.subheader("🧠 MirrorMe's Long-Term Memory")
memory = load_long_memory(user_id)

st.markdown("**Core Values:**")
st.write(", ".join(memory.get("core_values", [])))

st.markdown("**Goals:**")
st.write(", ".join(memory.get("goals", [])))

st.markdown("**Personality Summary:**")
st.info(memory.get("personality_summary", "No summary found."))

# === 🌍 Public Mirror Toggle ===
st.subheader("🌍 Mirror Visibility")
public_toggle = st.toggle("Make My Mirror Public", value=clarity.get("public", False))

if public_toggle != clarity.get("public"):
    clarity["public"] = public_toggle
    save_clarity(clarity)

    if public_toggle:
        summary = {
            "user_id": user_id,
            "archetype": clarity["archetype"],
            "desc": clarity["archetype_meta"]["desc"],
            "emoji": clarity["archetype_meta"]["emoji"],
            "traits": {k: v["score"] for k, v in clarity["traits"].items()}
        }
        save_doc("public_mirrors", user_id, summary)
        st.success("✅ Your Mirror is now visible in the public feed.")
    else:
        delete_doc("public_mirrors", user_id)
        st.info("🛑 Mirror removed from public view.")

# === ⚙️ Voice Preferences ===
st.subheader("🔊 Voice Preferences")
st.markdown(f"- **Voice ID:** `{settings.get('voice_id')}`")
st.markdown(f"- **Voice Response Enabled:** `{settings.get('enable_voice_response')}`")
