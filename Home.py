# Folder: MirrorME/
# File: app.py (Main Chat Page)

import streamlit as st
import openai
import os
from dotenv import load_dotenv
import requests

# === 🔐 Load Environment Variables ===
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
VOICE_ID = os.getenv("VOICE_ID") or "3Tjd0DlL3tjpqnkvDu9j"

# === Load System Prompt from Session or Default ===
def get_prompt():
    default = "You are MirrorMe — a confident, calm, and deep AI clone."
    return st.session_state.get("system_prompt", default)

# === ElevenLabs Voice Function ===
def speak_text(text):
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
        headers = {
            "xi-api-key": ELEVEN_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.9}
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            audio_file = "uthman_response.mp3"
            with open(audio_file, "wb") as f:
                f.write(response.content)
            st.audio(audio_file, format="audio/mp3")
        else:
            st.error(f"❌ ElevenLabs Error: {response.text}")
    except Exception as e:
        st.error(f"❌ ElevenLabs Error: {e}")

# === Chat Completion ===
def get_reply(messages):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"❌ OpenAI Error: {e}")
        return None

# === UI ===
st.set_page_config(page_title="MirrorMe", page_icon="🪞")
st.title("🪞 MirrorMe — Talk to Your AI Mirror")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": get_prompt()}
    ]

user_input = st.text_input("You:")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    reply = get_reply(st.session_state.messages)
    if reply:
        st.session_state.messages.append({"role": "assistant", "content": reply})

for msg in st.session_state.messages[1:]:
    role = "🧍 You" if msg["role"] == "user" else "🧠 MirrorMe"
    st.markdown(f"**{role}:** {msg['content']}")
    if msg["role"] == "assistant":
        speak_text(msg["content"])
