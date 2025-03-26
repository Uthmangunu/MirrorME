import streamlit as st
import openai
import os
import requests
import json
from dotenv import load_dotenv

from user_memory import (
    load_user_clarity, save_user_clarity,
    update_user_memory, get_user_memory_as_string
)
from clarity_tracker import log_clarity_change 
from adaptive_ui import detect_mood, set_mood_background
from long_memory import load_long_memory
from clarity_core import load_clarity, save_clarity, apply_trait_xp
from user_settings import load_user_settings
from generate_prompt import generate_prompt_from_clarity

load_dotenv()
st.set_page_config(page_title="MirrorMe", page_icon="🪞")

# === AUTH HANDLING ===
if "user" not in st.session_state:
    st.title("🪞 MirrorMe — Your Evolving AI Twin")
    st.markdown("Build a version of you that speaks your mind. Adaptive. Expressive. Real.")
    if st.button("🔐 Login to Begin"):
        st.switch_page("pages/Login.py")
    st.stop()

user_id = st.session_state["user"]["localId"]
clarity_data = load_clarity()
settings = load_user_settings(user_id)

if "traits" not in clarity_data:
    st.warning("🔧 Mirror not initialized. Please complete setup.")
    st.stop()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ELEVEN_API = os.getenv("ELEVEN_API_KEY")

# === DARK MODE ===
if settings.get("dark_mode"):
    st.markdown("""
        <style>
        .stApp { background-color: #0e1117; color: white; }
        .message-box { border: 1px solid #444; border-radius: 10px; padding: 0.75em; background-color: #1a1d23; }
        .user-msg { color: #FFD700; }
        .ai-msg { color: #90EE90; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        .message-box { border: 1px solid #ccc; border-radius: 10px; padding: 0.75em; background-color: #f9f9f9; }
        .user-msg { color: #333; }
        .ai-msg { color: #000; }
        </style>
    """, unsafe_allow_html=True)

# === VOICE SETTINGS ===
VOICE_ID = settings.get("voice_id", "3Tjd0DlL3tjpqnkvDu9j")
VOICE_ENABLED = settings.get("enable_voice_response", True)

def speak_text(text):
    if not VOICE_ENABLED:
        return
    try:
        response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
            headers={"xi-api-key": ELEVEN_API, "Content-Type": "application/json"},
            json={
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.99}
            }
        )
        if response.status_code == 200:
            filename = f"{user_id}_response.mp3"
            with open(filename, "wb") as f:
                f.write(response.content)
            st.audio(filename, format="audio/mp3")
            os.remove(filename)
    except Exception as e:
        st.error(f"❌ Voice Error: {e}")

def get_reply(messages):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"❌ OpenAI Error: {e}")
        return None

# === INIT SYSTEM PROMPT ===
if "messages" not in st.session_state:
    last_user_msgs = []
else:
    last_user_msgs = [m["content"] for m in st.session_state["messages"] if m["role"] == "user"][-5:]

prompt = generate_prompt_from_clarity(user_id, last_user_msgs)
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": prompt}]

# === INPUT ===
user_input = st.chat_input("Send a message...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    clarity_data = apply_trait_xp(clarity_data, "dm")
    reply = get_reply(st.session_state.messages)
    if reply:
        st.session_state.messages.append({"role": "assistant", "content": reply})
        update_user_memory(user_id, user_input, reply)
        mood = detect_mood(user_input + " " + reply)
        set_mood_background(mood)
        save_clarity(clarity_data)

# === DISPLAY ===
for msg in st.session_state.messages[1:]:
    if msg["role"] == "user":
        st.markdown(f"<div class='message-box user-msg'>👤 {msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='message-box ai-msg'>🧠 {msg['content']}</div>", unsafe_allow_html=True)
        speak_text(msg["content"])

# === SIDEBAR ===
with st.sidebar:
    st.markdown("### 🧠 Memory Log")
    st.text(get_user_memory_as_string(user_id))
    st.markdown("---")
    st.markdown("### 🪞 Mirror Clarity Traits")
    for trait, values in clarity_data["traits"].items():
        st.text(f"{trait.title()}: {int(values['score'])}")
    st.markdown("---")
    st.markdown("### 🧹 Tools")
    if st.button("🔁 Reset Mirror"):
        st.session_state.messages = [{"role": "system", "content": prompt}]
        st.experimental_rerun()
    if st.button("📤 Export Chat"):
        text = "\n\n".join([f"{m['role'].title()}: {m['content']}" for m in st.session_state["messages"][1:]])
        st.download_button("💾 Save Chat", text, file_name="mirror_chat.txt")
