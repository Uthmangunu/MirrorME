# voice_journal.py
import streamlit as st
import os
import datetime
import tempfile
import openai
from dotenv import load_dotenv
from clarity_tracker import log_clarity_change
from user_memory import update_user_memory, load_user_clarity, save_user_clarity
import speech_recognition as sr
from pydub import AudioSegment
import ast

# === 🔐 Load API Keys ===
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# === 🎤 Page Setup ===
st.set_page_config(page_title="Voice Journal", page_icon="🎤")
st.title("🎤 MirrorMe Voice Journal")

if "user" not in st.session_state:
    st.warning("🔒 You must log in to use this feature.")
    st.stop()

# === 📤 Upload Voice Note ===
st.markdown("Upload a voice note (.mp3 or .wav). MirrorMe will transcribe, reflect, and adapt.")
uploaded_file = st.file_uploader("Upload voice journal", type=["mp3", "wav"])
submit = st.button("📝 Reflect from Voice")

if submit and uploaded_file:
    try:
        file_type = uploaded_file.type.split("/")[-1]
        user_id = st.session_state["user"]["localId"]
        today = datetime.date.today().isoformat()

        # === 🎧 Convert to WAV using pydub
        audio = AudioSegment.from_file(uploaded_file, format=file_type)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav:
            audio.export(tmp_wav.name, format="wav")
            wav_path = tmp_wav.name

        # === 🧠 Transcribe
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            transcript = recognizer.recognize_google(audio_data)

        st.markdown(f"### 📜 Transcribed Entry ({today})")
        st.text_area("Transcript", transcript, height=200)

        # === 🤖 GPT Reflection
        prompt = [
            {"role": "system", "content": (
                "You're MirrorMe — insightful, calm, reflective.\n"
                "First reflect on the emotional and mental state of the user.\n"
                "Then, based on tone and content, suggest adjustments (from -1 to +1) for:\n"
                "humor, empathy, ambition, flirtiness.\n"
                "Return a JSON block like:\n"
                "{'reflection': '...', 'adjustments': {'humor': +0.5, 'empathy': -0.5}}"
            )},
            {"role": "user", "content": f"Voice Journal Entry on {today}:\n\n{transcript}"}
        ]

        with st.spinner("Reflecting & Updating..."):
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=prompt
            )
            raw = response.choices[0].message.content.strip()
            parsed = ast.literal_eval(raw)

            reflection = parsed["reflection"]
            adjustments = parsed["adjustments"]

            st.success("🪞 Your Reflection:")
            st.markdown(f"> {reflection}")

            # === 🧠 Update Memory & Clarity
            update_user_memory(user_id, transcript, reflection)

            clarity = load_user_clarity(user_id)
            for trait, delta in adjustments.items():
                if trait in clarity:
                    clarity[trait] = round(min(10, max(0, clarity[trait] + delta)), 2)

            save_user_clarity(user_id, clarity)
            log_clarity_change(user_id=user_id, source="voice_journal")

            st.success("🧠 Mirror’s clarity has evolved based on your voice journal.")

    except Exception as e:
        st.error(f"❌ Error during transcription or reflection: {e}")
