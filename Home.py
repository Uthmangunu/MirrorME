
import streamlit as st
import openai
import os
import requests
import json
import uuid
from dotenv import load_dotenv
from user_memory import (
    load_user_clarity, save_user_clarity,
    update_user_memory, get_user_memory_as_string, summarize_user_memory
)
from clarity_tracker import log_clarity_change 
from adaptive_ui import detect_mood, set_mood_background, animated_response, render_trait_snapshot
from long_memory import load_long_memory
from clarity_core import load_clarity, save_clarity, apply_trait_xp
from user_settings import load_user_settings
from vector_store import get_similar_memories

st.set_page_config(page_title="MirrorMe", page_icon="🪞")

clarity_data = load_clarity()
if not clarity_data.get("archetype") or "traits" not in clarity_data:
    st.warning("🔧 Mirror setup not complete. Please go to the Welcome page first.")
    st.stop()

def clarity_stage_label(level):
    stages = {
        0: "Shell", 1: "Echo", 2: "Voiceprint", 3: "Imprint", 4: "Reflection", 5: "You"
    }
    return stages.get(level, "Unknown")

load_dotenv()
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
ELEVEN_API = st.secrets["ELEVEN_API_KEY"]

if "user" not in st.session_state:
    st.warning("🔐 You must log in first.")
    st.stop()
user_id = st.session_state["user"]["localId"]

settings = load_user_settings(user_id)

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
            filename = f"{user_id}_response.mp3"
            with open(filename, "wb") as f:
                f.write(response.content)
            st.audio(filename, format="audio/mp3")
            os.remove(filename)
    except Exception as e:
        st.error(f"❌ ElevenLabs Error: {e}")

def generate_prompt_from_clarity(user_id):
    clarity = load_user_clarity(user_id)
    memory = load_long_memory(user_id)
    traits = clarity.get("traits", {})
    tone = []
    if traits.get("humor", {}).get("score", 0) > 60: tone.append("playful and witty")
    if traits.get("empathy", {}).get("score", 0) > 60: tone.append("deeply understanding and emotionally intelligent")
    if traits.get("ambition", {}).get("score", 0) > 60: tone.append("motivational and driven")
    if traits.get("flirtiness", {}).get("score", 0) > 60: tone.append("charming or flirtatious")
    tone_description = ", and ".join(tone) if tone else "neutral"

    archetype = clarity.get("archetype", "Strategist")
    meta = clarity.get("archetype_meta", {})
    emoji = meta.get("emoji", "♟️")
    desc = meta.get("desc", "Strategic, calm, structured.")

    recent_text = " ".join([m["content"] for m in st.session_state.get("messages", [])[-3:] if m["role"] == "user"])
    insights = get_similar_memories(user_id, recent_text, top_n=3) or []
    insight_block = "\n".join([f"- {i}" for i in insights]) if insights else "None"

    return f"""
You are MirrorMe — a digital version of the user, trained to evolve with them over time.

🧬 Archetype: {emoji} {archetype}
Tone Style: {tone_description}
Mirror Description: {desc}

Contextual Insights from Past Reflections:
{insight_block}

Long-Term Memory:
- Values: {', '.join(memory['core_values'])}
- Goals: {', '.join(memory['goals'])}
- Personality Summary: {memory['personality_summary']}

Speak in a way that reflects this tone and personality. Be expressive, insightful, and act like their emotional reflection. Stay in character.
"""

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

st.title("🪞 MirrorMe — Your AI Mirror")

if st.sidebar.button("🧹 Reset Mirror Session"):
    st.session_state.messages = [{"role": "system", "content": generate_prompt_from_clarity(user_id)}]
    st.experimental_rerun()

if st.sidebar.button("📥 Export Chat"):
    history_text = "\n\n".join([f"{m['role'].title()}: {m['content']}" for m in st.session_state.get("messages", [])[1:]])
    st.download_button("📤 Download Chat History", history_text, file_name="mirror_chat.txt")

with st.sidebar:
    st.markdown("### 🧠 Memory Log")
    st.text(get_user_memory_as_string(user_id))
    st.markdown("---")
    st.markdown("### 🔍 Your Reflection")
    st.write(summarize_user_memory(user_id))
    st.markdown("### 🪞 Mirror Clarity")
    st.markdown(f"**Archetype:** {clarity_data['archetype']}")
    st.markdown(f"**Level {clarity_data.get('clarity_level', 0)}** — {clarity_stage_label(clarity_data.get('clarity_level', 0))}")
    if clarity_data.get("total_xp") is not None and clarity_data.get("xp_to_next_level", 1) > 0:
        st.progress(min(clarity_data["total_xp"] / clarity_data["xp_to_next_level"], 1.0))
    else:
        st.warning("⚠️ XP tracking not initialized.")
    st.markdown("**Traits**")
    for trait, values in clarity_data["traits"].items():
        st.text(f"{trait.title()}: {int(values['score'])}")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": generate_prompt_from_clarity(user_id)}]

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

if len(st.session_state.messages) > 10:
    st.session_state.messages = [st.session_state.messages[0]] + st.session_state.messages[-9:]

for i, msg in enumerate(st.session_state.messages[1:], start=1):
    with st.container():
        if msg["role"] == "user":
            st.markdown(f"<div class='message-box user-msg'>👤 You: {msg['content']}</div>", unsafe_allow_html=True)
        elif msg["role"] == "assistant":
            st.markdown(f"<div class='message-box ai-msg'>🧠 MirrorMe: {msg['content']}</div>", unsafe_allow_html=True)
            speak_text(msg["content"])
            if "insights" in locals() and insights:
                with st.expander("🔎 Contextual Memory Recalled", expanded=False):
                    for insight in insights:
                        st.markdown(f"- _{insight}_")
