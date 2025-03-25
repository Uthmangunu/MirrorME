# components/feedback_button.py

import streamlit as st
from firebase_client import save_doc
from datetime import datetime

def feedback_button(user_id):
    with st.expander("💬 Report an Issue", expanded=False):
        st.markdown("Tell us what went wrong or felt off. This goes straight to the developer.")
        feedback = st.text_area("Describe your experience:", key="feedback_text")
        if st.button("📨 Send Feedback", key="send_feedback"):
            if feedback.strip():
                now = datetime.utcnow().isoformat()
                doc = {
                    "user_id": user_id,
                    "timestamp": now,
                    "error": feedback.strip()
                }
                save_doc("feedback_logs", user_id, doc, append_to_array="entries")
                st.success("✅ Sent! Thanks for helping improve MirrorMe.")
            else:
                st.warning("Please type something before submitting.")
