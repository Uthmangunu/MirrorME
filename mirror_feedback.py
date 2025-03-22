# app.py

import streamlit as st
import openai
import os
import requests
from dotenv import load_dotenv
from mirror_feedback import load_clarity, apply_feedback  # ✅ NEW

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
VOICE_ID = os.getenv("VOICE_ID") or "3Tjd0DlL3tjpqnkvDu9j"

# Load clarity data
clarity = load_clarity()

# === Prompt Builder ===
def get_prompt():
    return (
        f"You are MirrorMe — a confident, calm, reflective AI clone.\n"
        f"Traits:\n"
        f"- Humor: {clarity['humor']}/10\n"
        f"- Empathy: {clarity['empathy']}/10\n"
        f"- Ambition: {clarity['ambition']}/10\n"
        f"- Flirtiness: {clarity['flirtiness']}/10\n"
        f"Speak with wit, honesty, and reflection like Uthman would."
    )

def speak_text(text):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {"xi-api-key": ELEVEN_API_KEY, "Content-Type": "application/json"}
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
        st.error(f"ElevenLabs Error: {response.text}")

def get_reply(messages):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"OpenAI Error: {e}")
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

# === Display Chat + Feedback ===
for msg in st.session_state.messages[1:]:
    role = "🧍 You" if msg["role"] == "user" else "🧠 MirrorMe"
    st.markdown(f"**{role}:** {msg['content']}")
    
    if msg["role"] == "assistant":
        speak_text(msg["content"])

        # Feedback only for the last response
        if msg == st.session_state.messages[-1]:
            st.markdown("### 🤖 Was this reply accurate to your personality?")
            feedback = st.radio("Feedback:", ["✅ Yes", "❌ No - Needs Tweaking"], key=f"fb_{len(st.session_state.messages)}")

            if feedback == "❌ No - Needs Tweaking":
                issue = st.selectbox("What was off?", [
                    "Too blunt", "Too soft", "Not witty enough", "Too robotic", "Too emotional"
                ])
                notes = st.text_input("Add notes if needed:", key=f"notes_{len(st.session_state.messages)}")
                if st.button("💾 Submit Feedback"):
                    apply_feedback(issue, clarity)
                    st.success("✅ Feedback saved. Mirror will evolve.")
