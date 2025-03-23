# pages/Clarity_Progress.py
import streamlit as st
import json
import os
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="Clarity Progress", page_icon="📈")
st.title("📈 MirrorMe — Clarity Evolution")

log_path = "clarity_logs/history.json"
if not os.path.exists(log_path):
    st.warning("No clarity history found yet.")
    st.stop()

with open(log_path, "r") as f:
    history = json.load(f)

traits = ["humor", "empathy", "ambition", "flirtiness"]

# === Line Graph ===
st.subheader("📊 Trait Change Over Time")
for trait in traits:
    times = [datetime.fromisoformat(entry["timestamp"]) for entry in history]
    values = [entry["clarity"][trait] for entry in history]

    fig, ax = plt.subplots()
    ax.plot(times, values, marker='o')
    ax.set_title(f"{trait.capitalize()} Over Time")
    ax.set_xlabel("Time")
    ax.set_ylabel("Value (0–10)")
    st.pyplot(fig)

# === Radar Chart (Latest Snapshot) ===
st.subheader("🕸️ Latest Clarity Snapshot")
latest = history[-1]["clarity"]
labels = traits + [traits[0]]
values = [latest[t] for t in traits] + [latest[traits[0]]]

angles = [n / float(len(traits)) * 2 * 3.14159 for n in range(len(traits))]
angles += angles[:1]

fig, ax = plt.subplots(subplot_kw=dict(polar=True))
ax.plot(angles, values, linewidth=1, linestyle='solid')
ax.fill(angles, values, alpha=0.3)
ax.set_xticks(angles[:-1])
ax.set_xticklabels(traits)
st.pyplot(fig)
