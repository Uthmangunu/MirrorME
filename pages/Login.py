import streamlit as st
from firebase_auth import signup, login

st.set_page_config(page_title="Login", page_icon="🔐")
st.title("🔐 MirrorMe Login")

# === Logged In View ===
if "user" in st.session_state:
    st.success(f"✅ Logged in as: {st.session_state['user']['email']}")
    if st.button("🚪 Log Out"):
        del st.session_state["user"]
        st.rerun()

# === Login / Sign Up Form ===
else:
    st.subheader("🔑 Access MirrorMe")
    mode = st.radio("Mode", ["Login", "Sign Up"], horizontal=True)
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("🚀 Submit"):
        try:
            user = login(email, password) if mode == "Login" else signup(email, password)
            if user:
                user["email"] = email  # Store for UI display
                st.session_state["user"] = user
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
