# File: voice_setup.py

import streamlit as st
import os
from dotenv import load_dotenv

# Load API keys
load_dotenv()
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")

# === PAGE CONFIG ===
st.set_page_config(page_title="Mirror Voice Setup", page_icon="🗣️")
st.title("🗣️ MirrorMe Voice Setup")
st.markdown("Choose how you want your Mirror to sound.")

# === VOICE PRESETS ===
st.markdown("### 🎙️ Pick a Pre-Trained Voice")
preset_voices = {
    "Uthman Vibe (Calm + Smooth)": "3Tjd0DlL3tjpqnkvDu9j",
    "Witty Confidant": "EXAVITQu4vr4xnSDxMaL",
    "Playful Narrator": "ErXwobaYiN019PkySvjV",
    "Chill Deep": "21m00Tcm4TlvDq8ikWAM",  # default
}

chosen_voice = st.selectbox("Choose a voice style:", list(preset_voices.keys()))
st.session_state["VOICE_ID"] = preset_voices[chosen_voice]

st.success(f"✅ Voice set to: {chosen_voice}")

# === OPTIONAL: USER VOICE UPLOAD ===
st.markdown("### 🧬 Upload Your Voice (optional)")

uploaded_audio = st.file_uploader("Upload a short audio of your voice (MP3 or WAV)", type=["mp3", "wav"])

if uploaded_audio:
    st.audio(uploaded_audio, format="audio/mp3")
    st.session_state["user_voice_sample"] = uploaded_audio
    st.info("✅ Voice sample uploaded. We'll use this for cloning in the future.")

# === COMING SOON MESSAGE ===
st.markdown("#### 🚧 Voice Cloning Coming Soon")
st.caption("""
In the future, your Mirror will literally speak in your voice.
For now, you can pick a preset above — or upload your real voice so we’re ready when it’s time to clone.
""")
