# home.py
import streamlit as st
import openai
import os
import requests
import json
from dotenv import load_dotenv
from user_memory import (
    load_user_clarity, save_user_clarity,
    update_user_memory, get_user_memory_as_string, summarize_user_memory
)
from clarity_tracker import log_clarity_change 
from adaptive_ui import detect_mood, set_mood_background, animated_response, render_trait_snapshot
from long_memory import load_long_memory

# === 🔐 Load Environment Variables ===
load_dotenv()
openai.api_key = st.secrets["OPENAI_API_KEY"]
ELEVEN_API = st.secrets["ELEVEN_API_KEY"]

# === 🔒 Require Login ===
if "user" not in st.session_state:
    st.warning("🔐 You must log in first.")
    st.stop()
user_id = st.session_state["user"]["localId"]

# === ⚙️ Load User Settings ===
settings_path = f"user_data/{user_id}/settings.json"
if os.path.exists(settings_path):
    with open(settings_path, "r") as f:
        settings = json.load(f)
else:
    settings = {"dark_mode": False, "voice_id": "3Tjd0DlL3tjpqnkvDu9j", "enable_voice_response": True}

# === 🌒 Apply Dark Mode ===
if settings.get("dark_mode"):
    st.markdown("""
        <style>
        .stApp { background-color: #0e1117; color: white; }
        .message-box { border: 1px solid #444; border-radius: 10px; padding: 0.75em; margin-bottom: 1em; background-color: #1a1d23; }
        .user-msg { color: #FFD700; font-weight: bold; }
        .ai-msg { color: #90EE90; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        .message-box { border: 1px solid #ccc; border-radius: 10px; padding: 0.75em; margin-bottom: 1em; background-color: #f9f9f9; }
        .user-msg { color: #333; font-weight: bold; }
        .ai-msg { color: #000; }
        </style>
    """, unsafe_allow_html=True)

VOICE_ID = settings.get("voice_id", "3Tjd0DlL3tjpqnkvDu9j")
VOICE_ENABLED = settings.get("enable_voice_response", True)

# === 🗣️ ElevenLabs Voice Output ===
def speak_text(text):
    if not VOICE_ENABLED:
        return
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
        headers = {
            "xi-api-key": ELEVEN_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.99}
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            with open("response.mp3", "wb") as f:
                f.write(response.content)
            st.audio("response.mp3", format="audio/mp3")
    except Exception as e:
        st.error(f"❌ ElevenLabs Error: {e}")

# === 🧠 Adaptive Prompt Generator ===
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

# === GPT ===
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

# === UI Setup ===
st.set_page_config(page_title="MirrorMe", page_icon="🪞")
st.title("🪞 MirrorMe — Your AI Mirror")

# === Sidebar ===
with st.sidebar:
    st.markdown("### 🧠 Memory Log")
    st.text(get_user_memory_as_string(user_id))
    st.markdown("---")
    st.markdown("### 🔍 Your Reflection")
    st.write(summarize_user_memory(user_id))
    with st.expander("🎭 Trait Snapshot"):
        clarity = load_user_clarity(user_id)
        render_trait_snapshot(clarity)

# === Init Chat Session ===
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": generate_prompt_from_clarity(user_id)}]

# === Text Input ===
user_input = st.chat_input("Send a message...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    reply = get_reply(st.session_state.messages)
    if reply:
        st.session_state.messages.append({"role": "assistant", "content": reply})
        update_user_memory(user_id, user_input, reply)
        mood = detect_mood(user_input + " " + reply)
        set_mood_background(mood)

# === Display Chat ===
for msg in st.session_state.messages[1:]:
    with st.container():
        if msg["role"] == "user":
            st.markdown(f"<div class='message-box user-msg'>👤 You: {msg['content']}</div>", unsafe_allow_html=True)
        elif msg["role"] == "assistant":
            st.markdown(f"<div class='message-box ai-msg'>🧠 MirrorMe: {msg['content']}</div>", unsafe_allow_html=True)
            speak_text(msg["content"])
