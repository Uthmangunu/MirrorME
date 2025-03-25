import streamlit as st
import os
import requests
from dotenv import load_dotenv
from firebase_client import save_doc, get_doc
from components.feedback_button import feedback_button



# === Page Config ===
st.set_page_config(page_title="🗣️ Mirror Voice Setup", page_icon="🎙️")
st.title("🗣️ MirrorMe Voice Setup")
st.markdown("Choose how you want your Mirror to sound.")

# === 🔐 Require Login ===
if "user" not in st.session_state:
    st.warning("🔒 You must be logged in to access this page.")
    st.stop()
user_id = st.session_state["user"]["localId"]

# === Load API Key ===
load_dotenv()
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")

# === Predefined Voice Options ===
preset_voices = {
    "Uthman Vibe (Calm + Smooth)": "3Tjd0DlL3tjpqnkvDu9j",
    "Witty Confidant": "EXAVITQu4vr4xnSDxMaL",
    "Playful Narrator": "ErXwobaYiN019PkySvjV",
    "Chill Deep (Default)": "21m00Tcm4TlvDq8ikWAM"
}

# === Load Current Settings ===
current = get_doc("settings", user_id) or {}
current_id = current.get("voice_id", "21m00Tcm4TlvDq8ikWAM")
current_voice_name = next((k for k, v in preset_voices.items() if v == current_id), None)

# === UI: Select Voice Style ===
st.markdown("### 🎙️ Pick a Pre-Trained Voice")
chosen_voice = st.selectbox(
    "Choose a voice style:",
    options=list(preset_voices.keys()),
    index=list(preset_voices.keys()).index(current_voice_name) if current_voice_name else 0
)

selected_voice_id = preset_voices[chosen_voice]

# === Auto Preview: Generate & Play Voice ===
st.markdown("#### 🧪 Hear how your Mirror sounds")
test_phrase = "Hey, I’m your Mirror. Let’s see how I sound."

def speak(text, voice_id):
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
        headers = {
            "xi-api-key": ELEVEN_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.9
            }
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            audio_path = f"preview_{voice_id}.mp3"
            with open(audio_path, "wb") as f:
                f.write(response.content)
            st.audio(audio_path, format="audio/mp3")
        else:
            st.error("❌ Failed to fetch voice preview.")
    except Exception as e:
        st.error(f"Error: {e}")

speak(test_phrase, selected_voice_id)

# === Save Selection ===
if st.button("✅ Save Voice Selection"):
    save_doc("settings", user_id, {
        "voice_id": selected_voice_id,
        "enable_voice_response": True
    })
    st.success("✅ Your Mirror voice is set!")

# === Upload Custom Voice ===
st.markdown("### 🧬 Upload Your Own Voice (optional)")
st.caption("_This is just for future cloning, not used yet._")
uploaded_audio = st.file_uploader("Upload a short voice sample (MP3 or WAV)", type=["mp3", "wav"])
if uploaded_audio:
    st.audio(uploaded_audio, format="audio/mp3")
    st.info("✅ Voice sample uploaded. Mirror cloning feature coming soon.")

# === Footer ===
st.markdown("---")
st.caption("This voice will be used every time your Mirror speaks.")
feedback_button(user_id)