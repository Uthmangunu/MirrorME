import streamlit as st
from firebase_auth import signup, login
import os
import json



st.set_page_config(page_title="Login", page_icon="🔐")
st.title("🔐 MirrorMe Login")

AUTH_CACHE = ".auth_cache.json"

# === 🔒 Persistent Login Helpers ===
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

# === 🔁 Auto-Login from Cache ===
if "user" not in st.session_state:
    cached_user = load_auth_cache()
    if cached_user:
        st.session_state["user"] = cached_user

# === ✅ Already Logged In ===
if "user" in st.session_state:
    st.success("✅ You are already logged in.")
    if st.button("🚪 Log Out"):
        clear_auth_cache()
        del st.session_state["user"]
        st.rerun()

# === 🔐 Login/Signup UI ===
else:
    st.subheader("🔑 Access MirrorMe")
    mode = st.radio("Mode", ["Login", "Sign Up"], horizontal=True)
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    remember = st.checkbox("Remember Me", value=True)

    if st.button("🚀 Submit"):
        user = login(email, password) if mode == "Login" else signup(email, password)
        if user:
            st.success("🎉 Success! Welcome.")
            st.session_state["user"] = user
            if remember:
                save_auth_cache(user)
            st.rerun()
        else:
            st.error("❌ Failed. Please check your credentials.")
