import streamlit as st
import os
from long_memory import load_long_memory
from user_memory import load_user_clarity
from clarity_core import load_clarity
from user_settings import load_user_settings

st.set_page_config(page_title="User Profile", page_icon="👤")
st.title("👤 MirrorMe — Your Profile")

if "user" not in st.session_state:
    st.warning("🔐 You must log in first.")
    st.stop()

user_id = st.session_state["user"]["localId"]
settings = load_user_settings(user_id)

if settings.get("dark_mode"):
    st.markdown("""
        <style>
        .stApp { background-color: #0e1117; color: white; }
        </style>
    """, unsafe_allow_html=True)

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
        clarity["archetype"] = None
        clarity["archetype_meta"] = {}
        clarity["traits"] = {}
        from clarity_core import save_clarity
        save_clarity(clarity)
        st.session_state["force_reset"] = True
        st.success("🔁 Archetype and traits reset. Redirecting to test...")
        st.switch_page("pages/Welcome.py")
else:
    st.info("You haven’t taken the Archetype Test yet.")
    if st.button("🎯 Take Archetype Quiz Now"):
        st.switch_page("pages/Welcome.py")

st.subheader("📈 Clarity Level")
level = clarity.get("clarity_level", 0)
total_xp = clarity.get("total_xp", 0)
xp_to_next = clarity.get("xp_to_next_level", 100)

st.markdown(f"**Level {level}** — XP: {total_xp} / {xp_to_next}")
if xp_to_next > 0:
    st.progress(min(total_xp / xp_to_next, 1.0))
else:
    st.warning("Clarity leveling not initialized.")

st.subheader("🎭 Personality Traits")
traits = clarity.get("traits", {})
for trait, values in traits.items():
    st.slider(trait.capitalize(), 0.0, 10.0, float(values["score"]), step=0.1, disabled=True)

st.subheader("🧠 MirrorMe's Long-Term Memory")
memory = load_long_memory(user_id)

st.markdown("**Core Values:**")
st.write(", ".join(memory.get("core_values", [])))

st.markdown("**Goals:**")
st.write(", ".join(memory.get("goals", [])))

st.markdown("**Personality Summary:**")
st.info(memory.get("personality_summary", "No summary found."))

st.subheader("🔊 Voice Preferences")
st.markdown(f"- **Voice ID:** `{settings.get('voice_id')}`")
st.markdown(f"- **Voice Response Enabled:** `{settings.get('enable_voice_response')}`")
