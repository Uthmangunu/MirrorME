import streamlit as st
from firebase_auth import signup, login
import os
import json

st.set_page_config(page_title="Login", page_icon="🔐")
st.title("🔐 MirrorMe Login")

AUTH_CACHE = ".auth_cache.json"

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

# Auto-login from cache if available
if "user" not in st.session_state:
    cached_user = load_auth_cache()
    if cached_user:
        st.session_state["user"] = cached_user

# If logged in
if "user" in st.session_state:
    user_id = st.session_state["user"]["localId"]
    email = st.session_state["user"]["email"]
    st.success(f"✅ Logged in as: {email}")

    if email == "uthman.admin@mirrorme.app":
        from components.feedback_button import feedback_button
        feedback_button(user_id)

    if st.button("🚪 Log Out"):
        clear_auth_cache()
        del st.session_state["user"]
        st.rerun()

else:
    st.subheader("🔑 Access MirrorMe")
    mode = st.radio("Mode", ["Login", "Sign Up"], horizontal=True)
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    remember = st.checkbox("Remember Me", value=True)

    if st.button("🚀 Submit"):
        try:
            auth_fn = login if mode == "Login" else signup
            user = auth_fn(email, password)
            if user and "localId" in user:
                user["email"] = email
                st.session_state["user"] = user
                if remember:
                    save_auth_cache(user)
                st.success("🎉 You're in!")
                st.rerun()
            else:
                st.error("❌ Auth failed: No user data returned.")
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
