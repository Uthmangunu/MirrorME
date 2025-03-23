# voice_journal.py
import streamlit as st
import os
import openai
import requests
import datetime
from dotenv import load_dotenv
from memory_engine import update_memory
from clarity_tracker import log_clarity_change
from mirror_feedback import load_clarity, save_clarity, apply_feedback

# === 🔐 Load Environment ===
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
WHISPER_URL = "https://api.openai.com/v1/audio/transcriptions"

# === 📁 Setup Paths ===
os.makedirs("voice_journals", exist_ok=True)
os.makedirs("voice_samples", exist_ok=True)

# === 📝 Streamlit Page ===
st.set_page_config(page_title="Voice Journal", page_icon="🎤")
st.title("🎤 Voice Journal")
st.markdown("Upload your voice, and MirrorMe will reflect on your thoughts.")

# === 🎙️ Voice Upload ===
uploaded_file = st.file_uploader("Upload voice (mp3/wav)", type=["mp3", "wav"])
submit = st.button("🧠 Transcribe & Reflect")

# === 🧪 Voice Calibration (First 3 Uses) ===
def count_user_samples():
    return len([f for f in os.listdir("voice_samples") if f.endswith(".mp3") or f.endswith(".wav")])

def save_voice_sample(file):
    index = count_user_samples() + 1
    with open(f"voice_samples/sample_{index}.mp3", "wb") as f:
        f.write(file.read())

if uploaded_file and count_user_samples() < 3:
    st.info(f"🔊 Voice Sample {count_user_samples()+1}/3 saved for voice calibration.")
    save_voice_sample(uploaded_file)

# === 🔍 Transcribe and Reflect ===
if submit and uploaded_file:
    file_path = f"voice_journals/{datetime.datetime.now().isoformat()}.mp3"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())

    with st.spinner("Transcribing with Whisper..."):
        try:
            with open(file_path, "rb") as audio_file:
                response = requests.post(
                    WHISPER_URL,
                    headers={"Authorization": f"Bearer {openai.api_key}"},
                    files={"file": audio_file},
                    data={"model": "whisper-1"}
                )
            response.raise_for_status()
            transcript = response.json()["text"]
            st.success("✅ Transcription Complete")
            st.markdown(f"**You said:** {transcript}")
        except Exception as e:
            st.error(f"❌ Whisper Error: {e}")
            st.stop()

    # === 💬 Reflect with GPT ===
    reflection_prompt = [
        {"role": "system", "content": "You're MirrorMe — insightful and emotionally intelligent. Reflect on the user's journal and offer clarity."},
        {"role": "user", "content": transcript}
    ]

    with st.spinner("Reflecting..."):
        try:
            reflection = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=reflection_prompt
            ).choices[0].message.content.strip()

            st.success("🪞 MirrorMe Reflects:")
            st.markdown(f"> {reflection}")

            update_memory(transcript, reflection)
            clarity = load_clarity()
            apply_feedback("auto", clarity)  # Treat as general insight feedback
            save_clarity(clarity)
            log_clarity_change(source="voice_journal")

        except Exception as e:
            st.error(f"❌ Reflection Error: {e}")
