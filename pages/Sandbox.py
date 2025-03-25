import streamlit as st
from clarity_core import load_clarity
from long_memory import load_long_memory
import openai
import os
from components.feedback_button import feedback_button



st.set_page_config(page_title="🕶 Sandbox Mode", page_icon="🧠")
st.title("🕶 Talk to a Public Mirror")

if "sandbox_target" not in st.session_state:
    st.error("No mirror selected.")
    st.stop()

user_id = st.session_state["sandbox_target"]
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

clarity = load_clarity(user_id)
memory = load_long_memory(user_id)


def generate_prompt():
    tone = []
    traits = clarity.get("traits", {})
    if traits.get("humor", {}).get("score", 0) > 60: tone.append("playful and witty")
    if traits.get("empathy", {}).get("score", 0) > 60: tone.append("deeply understanding")
    if traits.get("ambition", {}).get("score", 0) > 60: tone.append("motivational")
    if traits.get("flirtiness", {}).get("score", 0) > 60: tone.append("charming")

    tone_desc = ", and ".join(tone) if tone else "neutral"
    desc = clarity.get("archetype_meta", {}).get("desc", "a thoughtful digital persona")

    return f"""
You are a public Mirror — an expressive, thoughtful version of another user.

Personality Style: {tone_desc}
Description: {desc}

Core Values: {', '.join(memory.get('core_values', []))}
Goals: {', '.join(memory.get('goals', []))}
Summary: {memory.get('personality_summary', '')}

Simulate their tone. Keep replies short, smart, expressive.
This is a sandbox — do not store or evolve anything.
"""

# Init chat
if "sandbox_messages" not in st.session_state:
    st.session_state.sandbox_messages = [
        {"role": "system", "content": generate_prompt()}
    ]

user_input = st.chat_input("Say something to this Mirror...")
if user_input:
    st.session_state.sandbox_messages.append({"role": "user", "content": user_input})
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=st.session_state.sandbox_messages,
            max_tokens=150
        )
        reply = response.choices[0].message.content.strip()
        st.session_state.sandbox_messages.append({"role": "assistant", "content": reply})
    except Exception as e:
        st.error(f"OpenAI error: {e}")

for msg in st.session_state.sandbox_messages[1:]:
    role_icon = "👤" if msg["role"] == "user" else "🧠"
    st.markdown(f"{role_icon} {msg['content']}")
feedback_button(user_id)