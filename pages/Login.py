import streamlit as st
import requests
import json
from components.topbar import topbar

# === Page Config ===
st.set_page_config(
    page_title="MirrorMe - Login",
    page_icon="🔐",
    layout="centered",
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
    text-align: center;
    font-size: 2rem;
    margin-bottom: 2rem;
    color: white;
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

.error-message {
    color: #FF4B4B;
    text-align: center;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# === Check if already logged in ===
if "user" in st.session_state and st.session_state.user:
    st.switch_page("pages/Clarity.py")

# === Login Form ===
st.markdown('<div class="login-container">', unsafe_allow_html=True)
st.markdown('<div class="login-title">🔐 Login to MirrorMe</div>', unsafe_allow_html=True)

# Email input
email = st.text_input("Email", key="email_input")

# Password input
password = st.text_input("Password", type="password", key="password_input")

# Login button
if st.button("Login"):
    if not email or not password:
        st.error("Please enter both email and password.")
    else:
        try:
            # Firebase Authentication
            response = requests.post(
                "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword",
                params={"key": st.secrets["FIREBASE_API_KEY"]},
                json={"email": email, "password": password}
            )
            
            if response.status_code == 200:
                user_data = response.json()
                st.session_state.user = user_data
                st.session_state.user_id = user_data["localId"]
                
                # Save to session state
                st.session_state["logged_in"] = True
                
                # Redirect to Clarity page
                st.switch_page("pages/Clarity.py")
            else:
                error_data = response.json()
                error_message = error_data.get("error", {}).get("message", "Invalid email or password.")
                if "INVALID_PASSWORD" in error_message:
                    st.error("Incorrect password. Please try again.")
                elif "EMAIL_NOT_FOUND" in error_message:
                    st.error("Email not found. Please check your email or register.")
                else:
                    st.error(f"Login failed: {error_message}")
        except Exception as e:
            st.error(f"Login failed: {str(e)}")

# Register link
st.markdown("""
<div style="text-align: center; margin-top: 1rem;">
    <a href="/Register" style="color: #FF4B4B; text-decoration: none;">
        Don't have an account? Register here
    </a>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
