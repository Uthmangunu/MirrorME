import streamlit as st
from firebase_auth import signup, login
import os
import json

st.set_page_config(page_title="Login", page_icon="🔐")
st.title("🔐 MirrorMe Login")

# === Auth Cache Helpers ===
def get_cache_path(email):
    safe_email = email.replace("@", "_at_").replace(".", "_dot_")
    return f".auth_cache_{safe_email}.json"

def save_auth_cache(email, user):
    with open(get_cache_path(email), "w") as f:
        json.dump(user, f)

def load_auth_cache(email):
    path = get_cache_path(email)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None

def clear_auth_cache(email):
    path = get_cache_path(email)
    if os.path.exists(path):
        os.remove(path)

# === Login State Initialization ===
if "user" not in st.session_state:
    # If any cache exists, auto-login from first found
    for file in os.listdir():
        if file.startswith(".auth_cache_") and file.endswith(".json"):
            with open(file, "r") as f:
                cached_user = json.load(f)
                st.session_state["user"] = cached_user
                break

# === Logged In View ===
if "user" in st.session_state:
    st.success("✅ Logged in as: " + st.session_state["user"]["email"])
    if st.button("🚪 Log Out"):
        clear_auth_cache(st.session_state["user"]["email"])
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
                user["email"] = email
                st.session_state["user"] = user
                if remember:
                    save_auth_cache(email, user)
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
