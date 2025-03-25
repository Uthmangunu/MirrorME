import streamlit as st
from firebase_client import get_all_docs
import datetime

# === SET YOUR ADMIN EMAIL HERE ===
ADMIN_EMAIL = "us1233208@gmail.com"  # 🔁 Replace this with your real email

# === 🔒 Check if current user is admin ===
if "user" not in st.session_state or st.session_state["user"]["email"] != ADMIN_EMAIL:
    st.set_page_config(page_title="Hidden", layout="centered")
    st.title("⛔ Access Denied")
    st.warning("You do not have permission to view this page.")
    st.stop()

# === PAGE CONFIG ===
st.set_page_config(page_title="📬 Admin Feedback Inbox", page_icon="🛠️")
st.title("📬 Feedback Inbox")
st.caption("Only visible to the admin.")

# === LOAD FEEDBACK ===
feedback_logs = get_all_docs("feedback_logs")

if not feedback_logs:
    st.info("No feedback yet.")
else:
    for user_id, doc in feedback_logs.items():
        st.markdown(f"### 🧑 From: `{user_id}`")
        for entry in doc.get("entries", []):
            st.markdown(f"- 🕒 `{entry.get('timestamp', 'N/A')}`")
            st.code(entry.get("error", 'No error provided.'))
        st.markdown("---")
