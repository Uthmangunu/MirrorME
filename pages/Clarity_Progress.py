# pages/Clarity_Progress.py
import streamlit as st
import json
import os
import matplotlib.pyplot as plt
from datetime import datetime
st.markdown("### 🚧 Clarity Progress (In Progress)")
st.caption("This feature is under development — the Mirror still tracks your growth behind the scenes.")


st.set_page_config(page_title="Clarity Progress", page_icon="📈")
st.title("📈 Clarity Evolution")

# 🧑 Require login
if "user" not in st.session_state:
    st.warning("🔐 Please log in to view your clarity evolution.")
    st.stop()

user_id = st.session_state["user"]["localId"]
log_path = f"user_data/{user_id}/clarity_history.json"

if not os.path.exists(log_path):
    st.info("No clarity history yet. Try journaling or giving feedback.")
    st.stop()

# 🧾 Load history
with open(log_path, "r") as f:
    history = json.load(f)

traits = ["humor", "empathy", "ambition", "flirtiness"]

# === 🧠 Trait Evolution Line Charts ===
st.subheader("📊 Trait Progress Over Time")
for trait in traits:
    timestamps = [datetime.fromisoformat(entry["timestamp"]) for entry in history]
    values = [entry["clarity"][trait] for entry in history]

    fig, ax = plt.subplots()
    ax.plot(timestamps, values, marker='o')
    ax.set_title(f"{trait.capitalize()} Over Time")
    ax.set_ylabel("Score (0–10)")
    ax.set_xlabel("Date")
    st.pyplot(fig)

# === 🕸️ Radar Chart Snapshot ===
st.subheader("🕸️ Current Trait Snapshot")
latest = history[-1]["clarity"]
labels = traits + [traits[0]]
values = [latest[t] for t in traits] + [latest[traits[0]]]

angles = [n / float(len(traits)) * 2 * 3.14159 for n in range(len(traits))]
angles += angles[:1]

fig, ax = plt.subplots(subplot_kw=dict(polar=True))
ax.plot(angles, values, linewidth=1.5)
ax.fill(angles, values, alpha=0.4)
ax.set_xticks(angles[:-1])
ax.set_xticklabels(traits)
st.pyplot(fig)
