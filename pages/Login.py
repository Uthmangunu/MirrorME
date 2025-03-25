import streamlit as st
from firebase_auth import signup, login
from components.feedback_button import feedback_button
feedback_button(user_id)


st.set_page_config(page_title="Login", page_icon="🔐")
st.title("🔐 MirrorMe Login")

# === Auto Login via Query Param ===
params = st.experimental_get_query_params()
if "uid" in params and "user" not in st.session_state:
    st.session_state["user"] = {"email": "Remembered", "localId": params["uid"][0]}
    st.rerun()

# === Logged In View ===
if "user" in st.session_state:
    st.success("✅ Logged in as: " + st.session_state["user"].get("email", "Remembered"))
    if st.button("🚪 Log Out"):
        st.experimental_set_query_params()  # Clear query params
        del st.session_state["user"]
        st.rerun()
    st.stop()

# === Login Form ===
st.subheader("🔑 Access MirrorMe")
mode = st.radio("Mode", ["Login", "Sign Up"], horizontal=True)
email = st.text_input("Email")
password = st.text_input("Password", type="password")
remember = st.checkbox("Remember Me")

if st.button("🚀 Submit"):
    try:
        user = login(email, password) if mode == "Login" else signup(email, password)
        if user:
            st.session_state["user"] = {"email": email, "localId": user["localId"]}
            if remember:
                st.experimental_set_query_params(uid=user["localId"])
            st.success("🎉 Welcome, you're in.")
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
