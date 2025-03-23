# home.py
import streamlit as st
import openai
import os
import requests
from dotenv import load_dotenv
from mirror_feedback import apply_feedback, load_clarity, save_clarity
from memory_engine import update_memory, get_memory_as_string, summarize_memory
from clarity_tracker import log_clarity_change 
from adaptive_ui import detect_mood, set_mood_background, animated_response, render_trait_snapshot
from long_memory import load_long_memory

# === 🔐 Load Environment Variables ===
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
VOICE_ID = st.session_state.get("VOICE_ID", "3Tjd0DlL3tjpqnkvDu9j")

# === 🔣 ElevenLabs Voice Output ===
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
    clarity = load_clarity()
    memory = load_long_memory()
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

# === 🔗 Get GPT Reply ===
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

# === 🌐 UI Setup ===
st.set_page_config(page_title="MirrorMe", page_icon="🪞")
st.title(":mirror: MirrorMe — Talk to Your AI Mirror")

if "VOICE_ID" not in st.session_state:
    st.info(":microphone2: No voice selected yet. [Go to Voice Setup](./voice_setup)")

# === 🧠 Sidebar: Memory + Trait Snapshot ===
with st.sidebar:
    st.markdown("### 🪠 Memory Log")
    st.text(get_memory_as_string())
    st.markdown("---")
    st.markdown("### :mag: What Your Reflection Reveals")
    st.write(summarize_memory())
    with st.expander(":performing_arts: Trait Snapshot"):
        clarity = load_clarity()
        render_trait_snapshot(clarity)

# === 🗣️ Chat Memory Setup ===
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": generate_prompt_from_clarity()}
    ]

# === 🔊 User Input ===
user_input = st.text_input("You:")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    reply = get_reply(st.session_state.messages)
    if reply:
        st.session_state.messages.append({"role": "assistant", "content": reply})
        update_memory(user_input, reply)

        mood = detect_mood(user_input + " " + reply)
        set_mood_background(mood)

# === 🔄 Reflection Mode ===
if st.button(":mag: Reflect on Recent Messages"):
    recent = [m for m in st.session_state.messages[-6:] if m["role"] in ["user", "assistant"]]
    reflect_prompt = [
        {"role": "system", "content": "You are MirrorMe, a calm and insightful reflection agent."},
        {"role": "user", "content": "Reflect on this dialogue and extract an emotional insight about the user:\n\n" + "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in recent])}
    ]

    with st.spinner("Reflecting..."):
        try:
            reflection = openai.ChatCompletion.create(model="gpt-4o", messages=reflect_prompt)
            output = reflection.choices[0].message.content.strip()
            st.success(":mirror: Your Reflection:")
            st.markdown(f"> {output}")
        except Exception as e:
            st.error(f"❌ Reflection Error: {e}")

# === 💬 Message Display + Feedback ===
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
                save_clarity(clarity)
                log_clarity_change(source="feedback")
                st.success("✅ Feedback saved. Mirror will evolve.")
