import streamlit as st
st.set_page_config(page_title="MirrorMe", page_icon="🪞")

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
from clarity_core import load_clarity, save_clarity, apply_trait_xp

def clarity_stage_label(level):
    stages = {
        0: "Shell",
        1: "Echo",
        2: "Voiceprint",
        3: "Imprint",
        4: "Reflection",
        5: "You"
    }
    return stages.get(level, "Unknown")

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

# === 🪞 Load Clarity System ===
clarity_data = load_clarity()

# === 🗣️ ElevenLabs Voice Output ===
def speak_text(text):
    if not VOICE_ENABLED:
        return
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
        headers = {
            "xi-api-key": ELEVEN_API,
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

    # Get the archetype for tone setting
    archetype = clarity.get("archetype", "Strategist")
    meta = clarity.get("archetype_meta", {})
    emoji = meta.get("emoji", "♟️")
    desc = meta.get("desc", "Strategic, calm, structured.")

    return f"""
You are MirrorMe — a digital version of the user, trained to evolve with them over time.

🧬 Archetype: {emoji} {archetype}
Tone Style: {tone_description}
Mirror Description: {desc}

Long-Term Memory:
- Values: {', '.join(memory['core_values'])}
- Goals: {', '.join(memory['goals'])}
- Personality Summary: {memory['personality_summary']}

Speak in a way that reflects this tone and personality. Be expressive, insightful, and act like their emotional reflection. Stay in character.
"""

# === 🧐 GPT ===
def get_reply(messages):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=150  # You can adjust this depending on the response length you want
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        st.error(f"❌ OpenAI Error: {e}")
        return None

# === UI Setup ===
st.title("🪞 MirrorMe — Your AI Mirror")

# === Sidebar ===
with st.sidebar:
    st.markdown("### 🧠 Memory Log")
    st.text(get_user_memory_as_string(user_id))
    st.markdown("---")
    st.markdown("### 🔍 Your Reflection")
    st.write(summarize_user_memory(user_id))
    st.markdown("### 🪞 Mirror Clarity")
    st.markdown(f"**Archetype:** {clarity_data['archetype']}")
    st.markdown(f"**Level {clarity_data['clarity_level']}** — {clarity_stage_label(clarity_data['clarity_level'])}")
    st.progress(clarity_data['total_xp'] / clarity_data['xp_to_next_level'])
    st.markdown("**Traits**")
    for trait, values in clarity_data["traits"].items():
        st.text(f"{trait.title()}: {int(values['score'])}")

## === Redirect to Archetype Test if not taken yet ===
if not clarity_data.get("archetype"):
    st.title("🔮 Welcome to MirrorMe!")
    st.write("""
        Before you start chatting with your Mirror, we need to set the tone.  
        **Your Mirror’s personality** is based on a fun test that helps define how it speaks and interacts with you.
    """)
    st.markdown("""
        **Why Take the Test?**
        - Your Mirror’s responses will reflect your unique personality archetype.
        - It helps us create a custom experience for you!
    """)
    
    # Add an option for the user to skip, but recommend the test
    st.warning("🚀 Let’s begin by choosing your Mirror Archetype. Taking the test is highly recommended!")
    if st.button("Take the Archetype Test"):
        st.session_state["archetype_test_taken"] = True
        st.experimental_rerun()  # Redirect to ArchetypeTest.py
    else:
        st.write("You can skip for now, but we recommend you take the test to get the best experience.")
    st.stop()  # Stop here, redirecting to Archetype Test if button is pressed



# === Init Chat Session ===
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": generate_prompt_from_clarity(user_id)}]

# === Text Input ===
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

# === Display Chat ===
for msg in st.session_state.messages[1:]:
    with st.container():
        if msg["role"] == "user":
            st.markdown(f"<div class='message-box user-msg'>👤 You: {msg['content']}</div>", unsafe_allow_html=True)
        elif msg["role"] == "assistant":
            st.markdown(f"<div class='message-box ai-msg'>🧠 MirrorMe: {msg['content']}</div>", unsafe_allow_html=True)
            speak_text(msg["content"])
