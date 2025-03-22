import streamlit as st
import openai
import os
import requests
from dotenv import load_dotenv

# === 🔐 Load Environment Variables ===
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
ELEVEN_API_KEY = os.getenv('ELEVEN_API_KEY')
VOICE_ID = os.getenv('VOICE_ID') or "3Tjd0DlL3tjpqnkvDu9j"

# === 🧠 Mirror Personality Prompt ===
system_prompt = (
    "You are Uthman's Mirror — an AI clone that thinks and speaks like him: calm, confident, witty, philosophical, sometimes a little savage. "
    "Respond with personality, purpose, and power."
)
 
# === 🔊 ElevenLabs Voice Function (Using raw API) ===
def speak_text(text):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.99
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        audio_file = "uthman_response.mp3"
        with open(audio_file, "wb") as f:
            f.write(response.content)
        st.audio(audio_file, format="audio/mp3")
    else:
        st.error(f"❌ ElevenLabs Error: {response.text}")

# === 🧠 GPT-4o Chat Completion ===
def get_mirror_reply(messages):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"❌ OpenAI Error: {e}")
        return None

# === 🎛️ Streamlit Page Setup ===
st.set_page_config(page_title="MirrorMe", page_icon="🪞")
st.title("🪞 MirrorMe — Talk to Your AI Mirror")

# === 💬 Session State Init ===
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": system_prompt}
    ]

# === 📝 User Input ===
user_input = st.text_input("You:", key="input")

# === 🔁 Handle Input & Response ===
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    reply = get_mirror_reply(st.session_state.messages)
    if reply:
        st.session_state.messages.append({"role": "assistant", "content": reply})

# === 💬 Display Chat History ===
for msg in st.session_state.messages[1:]:
    role = "🧍 You" if msg["role"] == "user" else "🧠 MirrorMe"
    st.markdown(f"**{role}:** {msg['content']}")
    if msg["role"] == "assistant":
        speak_text(msg["content"])
