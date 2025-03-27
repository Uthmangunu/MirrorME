import streamlit as st
import requests
import json
from components.topbar import topbar

# === Page Config ===
st.set_page_config(
    page_title="MirrorMe - Login",
    page_icon="🔐",
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

.login-container {
    max-width: 400px;
    margin: 2rem auto;
    padding: 2rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.login-title {
    font-size: 2rem;
    font-weight: bold;
    text-align: center;
    margin-bottom: 2rem;
    background: linear-gradient(45deg, #FF4B4B, #FF6B6B);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.stTextInput>div>div>input {
    background-color: rgba(255, 255, 255, 0.1);
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.stTextInput>div>div>input:focus {
    border-color: #FF4B4B;
}

.stButton>button {
    width: 100%;
    background: #FF4B4B;
    color: white;
    border: none;
    padding: 0.8rem;
    border-radius: 8px;
    font-size: 1.1rem;
    transition: all 0.3s ease;
}

.stButton>button:hover {
    background: #e03e3e;
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3);
}

.remember-me {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 1rem 0;
}

.error-message {
    color: #f44336;
    padding: 1rem;
    border-radius: 8px;
    background: rgba(244, 67, 54, 0.1);
    margin-top: 1rem;
}

.success-message {
    color: #4CAF50;
    padding: 1rem;
    border-radius: 8px;
    background: rgba(76, 175, 80, 0.1);
    margin-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

# === Initialize Session State ===
if "user" not in st.session_state:
    st.session_state.user = None
if "remember_me" not in st.session_state:
    st.session_state.remember_me = False

# === Check for Remembered Login ===
if "remembered_user" in st.session_state and st.session_state.remembered_user:
    try:
        user = sign_in_with_email_and_password(
            st.session_state.remembered_user["email"],
            st.session_state.remembered_user["password"]
        )
        st.session_state.user = user
        st.switch_page("Home.py")
    except:
        st.session_state.remembered_user = None
        st.session_state.remember_me = False

# === Main UI ===
st.markdown('<div class="login-container">', unsafe_allow_html=True)

# Title
st.markdown('<div class="login-title">🔐 Login to MirrorMe</div>', unsafe_allow_html=True)

# Login Form
email = st.text_input("📧 Email", key="login_email")
password = st.text_input("🔑 Password", type="password", key="login_password")

# Remember Me Checkbox
st.session_state.remember_me = st.checkbox("Remember Me", key="remember_me")

# Login Button
if st.button("🔐 Login"):
    try:
        user = sign_in_with_email_and_password(email, password)
        st.session_state.user = user
        
        # Handle Remember Me
        if st.session_state.remember_me:
            st.session_state.remembered_user = {
                "email": email,
                "password": password
            }
        else:
            st.session_state.remembered_user = None
        
        st.success("✅ Login successful!")
        st.switch_page("Home.py")
    except Exception as e:
        st.error(f"❌ Login failed: {str(e)}")

# Register Link
st.markdown("""
<div style="text-align: center; margin-top: 1rem;">
    Don't have an account? <a href="Register" style="color: #FF4B4B; text-decoration: none;">Register</a>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
