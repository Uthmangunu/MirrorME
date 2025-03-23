# adaptive_ui.py
import streamlit as st
import time

# === Mood to Color Mapping ===
MOOD_COLOR_MAP = {
    "calm": "#2E8B57",
    "sad": "#4169E1",
    "angry": "#B22222",
    "happy": "#FFD700",
    "neutral": "#708090"
}

# === Determine Mood from Text ===
def detect_mood(text):
    lowered = text.lower()
    if any(word in lowered for word in ["sad", "tired", "lonely", "depressed", "cry", "blue"]):
        return "sad"
    elif any(word in lowered for word in ["angry", "annoyed", "pissed", "frustrated"]):
        return "angry"
    elif any(word in lowered for word in ["happy", "excited", "grateful", "glad", "joyful"]):
        return "happy"
    elif any(word in lowered for word in ["calm", "relaxed", "peaceful", "okay"]):
        return "calm"
    else:
        return "neutral"

# === Mood-Based Highlight Styling ===
def set_mood_background(mood):
    color = MOOD_COLOR_MAP.get(mood, "#333")
    st.markdown(f"""
    <style>
    .stApp {{
        background-color: {color}1A;  /* Light transparent background */
    }}
    </style>
    """, unsafe_allow_html=True)

# === Typing Animation Effect ===
def animated_response(text, delay=0.015):
    animated = ""
    placeholder = st.empty()
    for char in text:
        animated += char
        placeholder.markdown(f"**🧠 MirrorMe:** {animated}█")
        time.sleep(delay)
    placeholder.markdown(f"**🧠 MirrorMe:** {animated}")

# === Display Read-Only Clarity Sliders ===
def render_trait_snapshot(clarity):
    st.markdown("### 🎯 Current Trait Snapshot")
    for trait, value in clarity.items():
        st.slider(trait.capitalize(), 0, 10, value, disabled=True)
