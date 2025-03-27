import streamlit as st
from firebase_auth import signup, login
import os
import json

st.set_page_config(page_title="MirrorMe - Login", page_icon="🔐")

# Add custom CSS for better UI
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        margin-top: 1rem;
        background-color: #FF4B4B;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #FF6B6B;
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
    }
    .stRadio>div {
        flex-direction: row;
        justify-content: center;
        gap: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Main title with emoji
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
    user_id = st.session_state["user"].get("localId", "N/A")
    email = st.session_state["user"].get("email", "Unknown")
    st.success(f"✅ Logged In As: {email}")

    if email == "uthman.admin@mirrorme.app":
        from components.feedback_button import feedback_button
        feedback_button(user_id)

    if st.button("🚪 Log Out"):
        clear_auth_cache()
        del st.session_state["user"]
        st.rerun()

# === Login / Sign Up Form ===
else:
    st.subheader("🔑 Access MirrorMe")
    
    # Warning for shared computers
    st.warning("⚠️ If You're Using a Shared Computer, Please Do Not Check 'Remember Me'.")
    
    # Mode selection with better styling
    mode = st.radio(
        "Select Mode",
        ["Login", "Sign Up"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    # Input fields with better styling
    email = st.text_input("Email Address")
    password = st.text_input("Password", type="password")
    remember = st.checkbox("Remember Me", value=False)
    
    # Submit button
    if st.button("🚀 Continue"):
        try:
            # Clear any existing cache before new login
            clear_auth_cache()
            
            auth_fn = login if mode == "Login" else signup
            user = auth_fn(email, password)

            if user and "localId" in user:
                user["email"] = email  # Attach email for local UI
                st.session_state["user"] = user
                if remember:
                    save_auth_cache(user)
                st.success("🎉 Welcome to MirrorMe!")
                st.rerun()
            else:
                st.error("❌ Authentication Failed: No User Data Returned.")

        except Exception as e:
            error_msg = str(e)
            if "INVALID_PASSWORD" in error_msg:
                st.error("❌ Incorrect Password.")
            elif "EMAIL_NOT_FOUND" in error_msg:
                st.error("❌ Email Not Found. Try Signing Up.")
            elif "EMAIL_EXISTS" in error_msg:
                st.error("❌ Email Already in Use. Try Logging In.")
            else:
                st.error(f"❌ Authentication Failed: {error_msg}")
