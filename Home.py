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
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.99}
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
# mirror_feedback.py

import streamlit as st
import json
import os

# === 🔁 Feedback-Based Personality Adjustment System ===

# --- Load Existing Clarity Profile or Initialize Default ---
def load_clarity():
    default_data = {
        "humor": 5,
        "empathy": 5,
        "ambition": 5,
        "flirtiness": 5
    }
    if os.path.exists("clarity_data.json"):
        with open("clarity_data.json", "r") as f:
            return json.load(f)
    return default_data

# --- Save Updated Clarity Profile ---
def save_clarity(data):
    with open("clarity_data.json", "w") as f:
        json.dump(data, f, indent=2)

# --- Visualize Feedback UI ---
def feedback_ui(latest_reply, clarity):
    st.markdown("---")
    st.markdown("### 🧪 Feedback on Mirror's Response")
    st.markdown(f"> {latest_reply}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ That's Me"):
            st.success("Got it. We'll reinforce this style.")
    with col2:
        if st.button("❌ That's Not Me"):
            st.warning("Understood. Let’s refine that.")
            tweak = st.selectbox("What was wrong?", [
                "Too blunt", "Too soft", "Not funny", "Too robotic", "Too emotional"
            ])
            if tweak:
                apply_feedback(tweak, clarity)
                save_clarity(clarity)

# --- Adjust Clarity Data Based on Feedback ---
def apply_feedback(tweak, clarity):
    if tweak == "Too blunt":
        clarity["empathy"] = min(10, clarity["empathy"] + 0.5)
    elif tweak == "Too soft":
        clarity["empathy"] = max(0, clarity["empathy"] - 0.5)
    elif tweak == "Not funny":
        clarity["humor"] = max(0, clarity["humor"] - 0.5)
    elif tweak == "Too robotic":
        clarity["flirtiness"] = min(10, clarity["flirtiness"] + 0.5)
    elif tweak == "Too emotional":
        clarity["flirtiness"] = max(0, clarity["flirtiness"] - 0.5)

# --- Radar Chart Optional (TBD Later) ---

# Usage example (in app.py or another file):
# clarity = load_clarity()
# feedback_ui(latest_reply, clarity)

