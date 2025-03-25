import streamlit as st
from firebase_auth import signup, login
import os
import json

st.set_page_config(page_title="Login", page_icon="🔐")
st.title("🔐 MirrorMe Login")

AUTH_CACHE = ".auth_cache.json"

# === Auth Cache Helpers ===
def save_auth_cache(user):
    with open(AUTH_CACHE, "w") as f:
        json.dump(user, f)

def load_auth_cache():
    if os.path.exists(AUTH_CACHE):
        with open(AUTH_CACHE, "r") as f:
            return json.load(f)
    return None

def clear_auth_cache():
    if os.path.exists(AUTH_CACHE):
        os.remove(AUTH_CACHE)

# === Auto Login from Cache ===
if "user" not in st.session_state:
    cached_user = load_auth_cache()
    if cached_user:
        st.session_state["user"] = cached_user

# === Logged In View ===
if "user" in st.session_state:
    user_id = st.session_state["user"]["localId"]
    st.success(f"✅ Logged in as: {st.session_state['user']['email']}")
    
    # Show feedback button ONLY for you
    if st.session_state["user"]["email"] == "uthman.admin@mirrorme.app":
        from components.feedback_button import feedback_button
        feedback_button(user_id)

    if st.button("🚪 Log Out"):
        clear_auth_cache()
        del st.session_state["user"]
        st.rerun()

# === Login / Sign Up Form ===
else:
    st.subheader("🔑 Access MirrorMe")
    mode = st.radio("Mode", ["Login", "Sign Up"], horizontal=True)
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    remember = st.checkbox("Remember Me", value=True)

    if st.button("🚀 Submit"):
        try:
            user = login(email, password) if mode == "Login" else signup(email, password)
            if user:
                st.success("🎉 Welcome, you're in.")
                user["email"] = email  # store email for UI
                st.session_state["user"] = user
                if remember:
                    save_auth_cache(user)
                st.rerun()
        except Exception as e:
            error_msg = str(e)
            if "INVALID_PASSWORD" in error_msg:
                st.error("❌ Incorrect password.")
            elif "EMAIL_NOT_FOUND" in error_msg:
                st.error("❌ Email not found. Try signing up.")
            elif "EMAIL_EXISTS" in error_msg:
                st.error("❌ Email already in use. Try logging in.")
            else:
                st.error("❌ Auth failed: " + error_msg)
