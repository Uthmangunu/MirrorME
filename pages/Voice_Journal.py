# voice_journal.py
import streamlit as st
import os
import datetime
import tempfile
import openai
from dotenv import load_dotenv
from clarity_tracker import log_clarity_change
from user_memory import update_user_memory, load_user_clarity, save_user_clarity
from long_memory import load_long_memory
import speech_recognition as sr
from pydub import AudioSegment
import ast
import json

# === 🔐 Load API Keys ===
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# === 🎤 Page Setup ===
st.set_page_config(page_title="Voice Journal", page_icon="🎤")
st.title("🎤 MirrorMe Voice Journal")

if "user" not in st.session_state:
    st.warning("🔒 You must log in to use this feature.")
    st.stop()

user_id = st.session_state["user"]["localId"]

# === ⚙️ Load User Settings ===
settings_path = f"user_data/{user_id}/settings.json"
if os.path.exists(settings_path):
    with open(settings_path, "r") as f:
        settings = json.load(f)
else:
    settings = {"dark_mode": False, "voice_id": "3Tjd0DlL3tjpqnkvDu9j", "enable_voice_response": True}

if settings.get("dark_mode"):
    st.markdown("""
        <style>
        .stApp { background-color: #0e1117; color: white; }
        </style>
    """, unsafe_allow_html=True)

# === 📤 Upload Voice Note ===
st.markdown("Upload a voice note (.mp3 or .wav). MirrorMe will transcribe, reflect, and adapt.")
uploaded_file = st.file_uploader("Upload voice journal", type=["mp3", "wav"])
submit = st.button("📝 Reflect from Voice")

# === 🧠 Auto-Adaptive Prompt Generator ===
def generate_prompt_from_clarity(user_id):
    clarity = load_user_clarity(user_id)
    memory = load_long_memory(user_id)

    tone = []
    if clarity["humor"] > 6: tone.append("playful and witty")
    if clarity["empathy"] > 6: tone.append("deeply understanding and emotionally intelligent")
    if clarity["ambition"] > 6: tone.append("motivational and driven")
    if clarity["flirtiness"] > 6: tone.append("charming or flirtatious")

    tone_description = ", and ".join(tone) if tone else "neutral"

    return f"""
You are MirrorMe — a confident, calm, deep AI clone of the user.

Long-Term Memory:
- Values: {', '.join(memory['core_values'])}
- Goals: {', '.join(memory['goals'])}
- Personality Summary: {memory['personality_summary']}

Personality Traits:
- Humor: {clarity['humor']}/10
- Empathy: {clarity['empathy']}/10
- Ambition: {clarity['ambition']}/10
- Flirtiness: {clarity['flirtiness']}/10

Respond with a tone that is {tone_description}. Stay in character. Keep it sharp and personal.
"""

if submit and uploaded_file:
    try:
        file_type = uploaded_file.type.split("/")[-1]
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
            {"role": "system", "content": generate_prompt_from_clarity(user_id)},
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