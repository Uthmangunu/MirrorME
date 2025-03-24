import streamlit as st
from firebase_auth import signup, login, signin_with_email
import json
import os

st.set_page_config(page_title="Login", page_icon="🔐")
st.title("🔐 MirrorMe Login")

# === Auth Cache Path ===
AUTH_CACHE = ".auth_cache.json"

# Function to save user data to cache
def save_auth_cache(user):
    with open(AUTH_CACHE, "w") as f:
        json.dump(user, f)

# Function to load cached user data
def load_auth_cache():
    if os.path.exists(AUTH_CACHE):
        with open(AUTH_CACHE, "r") as f:
            return json.load(f)
    return None

# Function to clear cached user data
def clear_auth_cache():
    if os.path.exists(AUTH_CACHE):
        os.remove(AUTH_CACHE)

# === Load Cached User ===
if "user" not in st.session_state:
    cached_user = load_auth_cache()
    if cached_user:
        st.session_state["user"] = cached_user

# === Check if User is Logged In ===
if "user" in st.session_state:
    st.success("✅ You are already logged in.")
    if st.button("Log Out"):
        clear_auth_cache()  # Clear cache on logout
        del st.session_state["user"]
        st.rerun()
else:
    # === Login / Signup UI ===
    mode = st.radio("Choose mode", ["Login", "Sign Up"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    remember_me = st.checkbox("Remember Me")  # Checkbox for remember me feature

    if st.button("Submit"):
        # Handle Login or Signup process
        if mode == "Login":
            user = signin_with_email(email, password)  # Use the login function
        else:
            user = signup(email, password)  # Use the signup function

        if user:
            st.session_state["user"] = user  # Store the user in session state

            if remember_me:
                save_auth_cache(user)  # Save user data if "Remember Me" is checked
            st.success("✅ Success! You are now logged in.")
            st.experimental_rerun()  # Rerun the app to navigate to home page or other pages

        else:
            st.error("❌ Invalid credentials. Please try again.")
