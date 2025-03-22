import streamlit as st
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="MirrorMe", page_icon="🪞")

st.title("🪞 MirrorMe — Talk to Your AI Mirror")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are Uthman's AI mirror. Talk like him — calm, confident, funny, a little deep, a little cheeky."}
    ]

# User input
user_input = st.text_input("You:", key="input")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=st.session_state.messages
        )
        reply = response.choices[0].message.content.strip()
        st.session_state.messages.append({"role": "assistant", "content": reply})
    except Exception as e:
        reply = "❌ GPT Error: " + str(e)

# Display chat history
for msg in st.session_state.messages[1:]:  # skip system prompt
    speaker = "🧠 MirrorMe" if msg["role"] == "assistant" else "🧍 You"
    st.markdown(f"**{speaker}:** {msg['content']}")
