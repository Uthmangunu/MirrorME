import streamlit as st
import datetime
from firebase_client import save_doc, get_doc
import platform
import socket
import os

# Get user ID
user_id = st.session_state.get("user", {}).get("localId", "anonymous")

# Feedback types
types = ["Bug", "Suggestion", "Feature Request", "Other"]

st.set_page_config(page_title="📝 Send Feedback", page_icon="📮")
st.title("📮 Send Feedback to MirrorMe Admin")
st.caption("Tell us if something broke or you have an idea — Uthman will see it directly.")

feedback_type = st.selectbox("What type of feedback?", types)

# Optional context (autofilled on error screens)
current_page = st.text_input("What page were you on? (e.g. Home.py, Journal.py)")
feedback_msg = st.text_area("Write your feedback here...")

send = st.button("📤 Send to Admin")

if send and feedback_msg.strip():
    feedback_data = {
        "type": feedback_type.lower(),
        "message": feedback_msg.strip(),
        "page": current_page,
        "timestamp": datetime.datetime.now().isoformat(),
        "user_id": user_id,
        "device": {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "hostname": socket.gethostname()
        }
    }

    save_doc("feedback", f"{user_id}_{datetime.datetime.now().isoformat()}", feedback_data)
    st.success("✅ Feedback sent! Thank you.")
elif send:
    st.warning("⚠️ Please enter a message before submitting.")
