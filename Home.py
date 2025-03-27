import streamlit as st
import openai
import os
import requests
import json
import tempfile
from dotenv import load_dotenv
import time
from components.topbar import topbar
from firebase_client import get_doc
from user_memory import (
    load_user_clarity, save_user_clarity,
    update_user_memory, get_user_memory_as_string
)
from clarity_tracker import log_clarity_change 
from adaptive_ui import (
    detect_mood, set_mood_background, render_mood_indicator,
    create_animated_input
)
from long_memory import load_long_memory
from clarity_core import load_clarity, save_clarity, apply_trait_xp
from user_settings import load_user_settings
from vector_store import get_similar_memories
from style_analyzer import analyze_user_style

# === Page Config ===
st.set_page_config(
    page_title="MirrorMe - Chat",
    page_icon="🪞",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# === Custom CSS ===
st.markdown("""
<style>
.main {
    background-color: #0E1117;
    color: white;
}

.chat-container {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-top: 1rem;
}

.message-box {
    border: 1px solid #444;
    border-radius: 10px;
    padding: 0.75em;
    background-color: #1a1d23;
    color: white;
    margin-bottom: 0.5rem;
}

.mood-container {
    margin-top: 1.5rem;
}

.sidebar-content {
    background: rgba(255, 255, 255, 0.05);
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# === Redirect if Logged In ===
if "user" in st.session_state and st.session_state.user:
    # Check if user has completed Clarity setup
    user_id = st.session_state.user["localId"]
    current = get_doc("settings", user_id) or {}
    
    # Only redirect to Clarity if core values or personality traits are not set
    if not current.get("core_values") or not current.get("personality_traits"):
        st.switch_page("pages/Clarity.py")
    # Otherwise, stay on Home page

# === Require Login ===
if "user" not in st.session_state:
    st.warning("⚠️ Please Log In to Access This Page.")
    if st.button("🔐 Login"):
        st.switch_page("pages/Login.py")
    st.stop()

# === Initialize User Data ===
user_id = st.session_state.user["localId"]
username = st.session_state.user.get("displayName", "User")
clarity_data = load_clarity()
settings = load_user_settings(user_id)

# Add topbar
topbar(username)

# === Initialize Chat State ===
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": generate_prompt_from_clarity(user_id)}]
if "current_mood" not in st.session_state:
    st.session_state.current_mood = "neutral"
if "mood_changed" not in st.session_state:
    st.session_state.mood_changed = False
if "last_mood_change_time" not in st.session_state:
    st.session_state.last_mood_change_time = 0

# === Chat Interface ===
# Title and Mood Indicator
col1, col2 = st.columns([20, 1])
with col1:
    st.title("🪞 Chat with Your Mirror")
with col2:
    animation_class = "mood-changed" if (time.time() - st.session_state.last_mood_change_time) < 1 else ""
    render_mood_indicator(st.session_state.current_mood, size=40, animation_class=animation_class)

# Chat Messages
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.messages[1:]:
    if msg["role"] == "user":
        st.markdown(f"<div class='message-box user-msg'>👤 {msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='message-box ai-msg'>🧠 {msg['content']}</div>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Chat Input
user_input = st.chat_input("Send a message...")
if user_input:
    # Add user message
    st.markdown(f"<div class='message-box user-msg'>👤 {user_input}</div>", unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Update clarity data
    clarity_data = apply_trait_xp(clarity_data, "dm")
    
    # Get AI response
    response_placeholder = st.empty()
    full_response = ""
    
    response = get_reply(st.session_state.messages)
    if response:
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                full_response += chunk.choices[0].delta.content
                response_placeholder.markdown(f"<div class='message-box ai-msg'>🧠 {full_response}</div>", unsafe_allow_html=True)
        
        # Update state
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        update_user_memory(user_id, user_input, full_response)
        
        # Update mood
        mood = detect_mood(user_input + " " + full_response)
        if mood != st.session_state.current_mood:
            st.session_state.current_mood = mood
            st.session_state.last_mood_change_time = time.time()
        set_mood_background(mood)
        
        # Save data
        save_clarity(clarity_data)
        
        # Speak response if enabled
        if settings.get("enable_voice_response", True):
            speak_text(full_response)

# === Sidebar ===
with st.sidebar:
    st.markdown("### 🧠 Memory Log")
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    st.text(get_user_memory_as_string(user_id))
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### 🪞 Mirror Traits")
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    for trait, values in clarity_data.get("traits", {}).items():
        score = values.get("score", 50)
        st.text(f"{trait.title()}: {int(score)}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### 🧹 Tools")
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    if st.button("🔁 Reset Chat"):
        st.session_state.messages = [{"role": "system", "content": generate_prompt_from_clarity(user_id)}]
        st.session_state.current_mood = "neutral"
        st.session_state.last_mood_change_time = 0
        st.rerun()
    
    if st.button("📤 Export Chat"):
        text = "\n\n".join([f"{m['role'].title()}: {m['content']}" for m in st.session_state["messages"][1:]])
        st.download_button("💾 Save Chat", text, file_name="mirror_chat.txt")
    st.markdown('</div>', unsafe_allow_html=True)
