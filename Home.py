import streamlit as st
import openai
import os
import requests
import json
from mirror_feedback import apply_feedback
from dotenv import load_dotenv
from user_memory import (
    load_user_clarity, save_user_clarity,
    update_user_memory, get_user_memory_as_string, summarize_user_memory
)
from clarity_tracker import log_clarity_change
from adaptive_ui import detect_mood, set_mood_background, animated_response, render_trait_snapshot
from long_memory import load_long_memory
from mirror_feedback import apply_feedback

# === 🔐 Load Environment Variables ===
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")


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
    settings = {"dark_mode": False, "voice_id": "3Tjd0DlL3tjpqnkvDu9j"}

# === Apply Theme ===
if settings.get("dark_mode"):
    st.markdown("""
        <style>
        .stApp { background-color: #0e1117; color: white; }
        </style>
    """, unsafe_allow_html=True)

VOICE_ID = settings.get("voice_id", "3Tjd0DlL3tjpqnkvDu9j")

# === 🗣️ ElevenLabs Voice Output ===
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
            with open("uthman_response.mp3", "wb") as f:
                f.write(response.content)
            st.audio("uthman_response.mp3", format="audio/mp3")
        else:
            st.error(f"❌ ElevenLabs Error: {response.text}")
    except Exception as e:
        st.error(f"❌ ElevenLabs Error: {e}")

# === 🧠 Dynamic Prompt Generation ===
def generate_prompt_from_clarity():
    clarity = load_user_clarity(user_id)
    memory = load_long_memory(user_id)
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

Speak and respond like someone with this energy. Maintain their tone and perspective.
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
st.title("🪞 MirrorMe — Talk to Your AI Mirror")

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
    st.markdown("---")
    if st.button("🔄 Reset Conversation"):
        st.session_state.messages = [{"role": "system", "content": generate_prompt_from_clarity()}]
        st.experimental_rerun()


# === Init Chat Session ===
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": generate_prompt_from_clarity()}]

# === User Input ===
user_input = st.text_input("You:")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    reply = get_reply(st.session_state.messages)
    if reply:
        st.session_state.messages.append({"role": "assistant", "content": reply})
        update_user_memory(user_id, user_input, reply)

        mood = detect_mood(user_input + " " + reply)
        set_mood_background(mood)

# === Reflect Button ===
if st.button("🔍 Reflect on Recent Messages"):
    recent = [m for m in st.session_state.messages[-6:] if m["role"] in ["user", "assistant"]]
    reflect_prompt = [
        {"role": "system", "content": "You are MirrorMe, a calm and insightful reflection agent."},
        {"role": "user", "content": "Reflect on this dialogue and extract an emotional insight about the user:\n\n" + "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in recent])}
    ]

    with st.spinner("Reflecting..."):
        try:
            reflection = openai.ChatCompletion.create(model="gpt-4o", messages=reflect_prompt)
            output = reflection.choices[0].message.content.strip()
            st.success("🪞 Your Reflection:")
            st.markdown(f"> {output}")
        except Exception as e:
            st.error(f"❌ Reflection Error: {e}")

# === Chat Log + Feedback ===
for i, msg in enumerate(st.session_state.messages[1:], start=1):
    if msg["role"] == "assistant":
        animated_response(msg["content"])
        speak_text(msg["content"])
    else:
        st.markdown(f"**👤 You:** {msg['content']}")

    if msg["role"] == "assistant" and i == len(st.session_state.messages) - 1:
        st.markdown("### 🧠 Was this reply accurate to your personality?")
        feedback = st.radio("Feedback:", ["✅ Yes", "❌ No - Needs Tweaking"], key=f"feedback_{i}")

        if feedback == "❌ No - Needs Tweaking":
            issue = st.selectbox("What was off?", [
                "Too blunt", "Too soft", "Not witty enough", "Too robotic", "Too emotional"
            ], key=f"issue_{i}")
            notes = st.text_input("Optional: Add notes", key=f"note_{i}")
            if st.button("📎 Submit Feedback", key=f"submit_{i}"):
                apply_feedback(issue, clarity)
                save_user_clarity(user_id, clarity)
                log_clarity_change(user_id, source="feedback")
                st.success("✅ Feedback saved. Mirror will evolve.")
