# pages/Feedback_Inbox.py

import streamlit as st
from firebase_client import get_all_docs

st.set_page_config(page_title="🛠 Feedback Inbox", page_icon="📬")
st.title("📬 MirrorMe Feedback Inbox")

# You can add a check here if you want to restrict to admins only:
# if st.session_state["user"]["email"] != "your@email.com":
#     st.stop()

feedback_entries = get_all_docs("feedback_logs")

if not feedback_entries:
    st.info("No feedback submitted yet.")
else:
    sorted_entries = sorted(feedback_entries, key=lambda x: x.get("timestamp", ""), reverse=True)

    for entry in sorted_entries:
        with st.expander(f"🗓 {entry['timestamp']} — {entry['type'].title()} from {entry['user_id']}"):
            st.markdown(f"**Page:** `{entry.get('page', 'unknown')}`")
            st.markdown(f"**Type:** `{entry.get('type', 'general')}`")
            st.markdown("**Content:**")
            st.code(entry["content"])
