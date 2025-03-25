import streamlit as st
from firebase_client import get_all_docs
import pandas as pd

st.set_page_config(page_title="🛠 Admin Feedback Viewer", page_icon="📬")
st.title("🛠 Feedback Viewer")

st.markdown("Here are the latest user-submitted feedback messages.")

# Load all feedback entries
entries = get_all_docs("feedback")

if not entries:
    st.info("No feedback submitted yet.")
    st.stop()

# Convert to DataFrame for filtering and sorting
df = pd.DataFrame(entries)

# === Filter & Sort Options ===
col1, col2 = st.columns(2)
with col1:
    filter_type = st.selectbox("Filter by Type", ["All"] + sorted(df["type"].unique()))
with col2:
    sort_order = st.radio("Sort", ["Newest First", "Oldest First"], horizontal=True)

if filter_type != "All":
    df = df[df["type"] == filter_type.lower()]

df = df.sort_values(by="timestamp", ascending=(sort_order == "Oldest First"))

# === Display Feedback Entries ===
for i, row in df.iterrows():
    st.markdown("---")
    st.markdown(f"**🗂 Type:** `{row['type'].capitalize()}`")
    st.markdown(f"**📅 Timestamp:** `{row['timestamp']}`")
    st.markdown(f"**🧑 User ID:** `{row.get('user_id', 'N/A')}`")
    st.markdown(f"**📄 Page:** `{row.get('page', 'Unknown')}`")
    st.markdown(f"**🧠 Message:**\n\n{row['message']}")
    if "device" in row:
        dev = row["device"]
        st.caption(f"📟 {dev.get('platform')} ({dev.get('hostname')})")

st.markdown("---")
st.success(f"Showing {len(df)} feedback entr{'y' if len(df)==1 else 'ies'}.")
