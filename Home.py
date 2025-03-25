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
from adaptive_ui import detect_mood, set_mood_background
from long_memory import load_long_memory
from clarity_core import load_clarity, save_clarity, apply_trait_xp
from user_settings import load_user_settings
from vector_store import get_similar_memories
from style_analyzer import analyze_user_style

load_dotenv()

# === CONFIG ===
st.set_page_config(page_title="MirrorMe", page_icon="🪞")

# === AUTH ===
if "user" not in st.session_state:
    st.warning("🔐 You must log in first.")
    st.stop()

user_id = st.session_state["user"]["localId"]
clarity_data = load_clarity()
settings = load_user_settings(user_id)

if not clarity_data.get("archetype") or "traits" not in clarity_data:
    st.warning("🔧 Mirror setup not complete. Please go to the Welcome page first.")
    st.stop()

client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
ELEVEN_API = st.secrets["ELEVEN_API_KEY"]

# === UI STYLE ===
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

# === VOICE ===
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

# === GENERATE PROMPT ===
def generate_prompt_from_clarity(user_id):
    clarity = load_user_clarity(user_id)
    memory = load_long_memory(user_id)

    # === Traits Tone Inference ===
    traits = clarity.get("traits", {})
    tone_tags = []
    if traits.get("humor", {}).get("score", 0) > 60: tone_tags.append("witty")
    if traits.get("empathy", {}).get("score", 0) > 60: tone_tags.append("emotionally intelligent")
    if traits.get("ambition", {}).get("score", 0) > 60: tone_tags.append("motivational")
    if traits.get("flirtiness", {}).get("score", 0) > 60: tone_tags.append("charismatic")
    trait_tone = ", ".join(tone_tags) if tone_tags else "neutral"

    # === Style Analyzer (from message history) ===
    user_msgs = [m["content"] for m in st.session_state.get("messages", []) if m["role"] == "user"]
    style_sample = " ".join(user_msgs[-5:]) if user_msgs else ""
    writing_style = analyze_user_style([style_sample]) if style_sample else "balanced"

    # === Long-Term Memory Context ===
    values = memory.get("core_values", [])
    goals = memory.get("goals", [])
    summary = memory.get("personality_summary", "No summary available.")

    # === Archetype ===
    archetype = clarity.get("archetype", "Strategist")
    meta = clarity.get("archetype_meta", {})
    emoji = meta.get("emoji", "♟️")
    desc = meta.get("desc", "Strategic, calm, structured.")

    # === Semantic Memory ===
    try:
        recent_text = " ".join(user_msgs[-3:])
        insights = get_similar_memories(user_id, recent_text, top_k=3)
    except Exception as e:
        st.warning(f"⚠️ Semantic memory failed: {e}")
        insights = []

    insight_block = "\n".join([f"- {i}" for i in insights]) if insights else "None"

    # === Prompt Blueprint ===
    return f"""
You are MirrorMe — a digital twin of the user, designed to speak in their style and reflect their mindset.

🧬 Archetype: {emoji} {archetype}
Mirror Personality: {desc}
Tone Guide: {trait_tone}
Writing Style: {writing_style}

Long-Term Memory:
- Values: {', '.join(values)}
- Goals: {', '.join(goals)}
- Personality Summary: {summary}

Contextual Insights:
{insight_block}

Be expressive, adaptive, and in-sync with how the user communicates.
Speak like *them*, not like an assistant. Stay in character.
"""




# === CHAT ===
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

# === INIT ===
st.title("🪞 MirrorMe — Your AI Mirror")
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": generate_prompt_from_clarity(user_id)}]


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
    st.markdown("### 🪞 Mirror Clarity")
    st.markdown(f"**Archetype:** {clarity_data['archetype']}")
    st.markdown(f"**Traits**")
    for trait, values in clarity_data["traits"].items():
        st.text(f"{trait.title()}: {int(values['score'])}")
    st.markdown("---")
    st.markdown("### 🧹 Tools")
    if st.button("🔁 Reset Mirror"):
        st.session_state.messages = [{"role": "system", "content": generate_prompt(user_id)}]
        st.experimental_rerun()

    if st.button("📤 Export Chat"):
        text = "\n\n".join([f"{m['role'].title()}: {m['content']}" for m in st.session_state["messages"][1:]])
        st.download_button("💾 Save Chat", text, file_name="mirror_chat.txt")
