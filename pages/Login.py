# pages/Auth.py
import streamlit as st
from firebase_auth import signup, login

st.set_page_config(page_title="Login", page_icon="🔐")
st.title("🔐 MirrorMe Login")

mode = st.radio("Choose mode", ["Login", "Sign Up"])
email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Submit"):
    user = login(email, password) if mode == "Login" else signup(email, password)
    if user:
        st.session_state['user'] = user
        st.success("✅ Success! You’re logged in.")
        st.info("Go to the Home tab to start chatting with MirrorMe.")
