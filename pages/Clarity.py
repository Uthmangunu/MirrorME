
import streamlit as st
import matplotlib.pyplot as plt
import json
import os

from clarity_tracker import load_clarity_logs
from components.feedback_button import feedback_button

st.set_page_config(page_title="Clarity Tracker", page_icon="📊")

# === Session Check ===
if "user" not in st.session_state:
    st.warning("🔐 Please log in to view your Mirror's clarity.")
    st.stop()

user_id = st.session_state["user"]["localId"]

st.title("📊 Mirror Clarity Progress")
st.markdown("Track how your Mirror is evolving based on your inputs.")

# === Feedback Button (Visible only for admin) ===
if st.session_state["user"].get("email") == "uthman.admin@mirrorme.app":
    feedback_button(user_id)

# === Load and visualize clarity logs ===
logs_path = f"clarity_logs/{user_id}_history.json"
if not os.path.exists(logs_path):
    st.info("No clarity logs yet. Interact more with your Mirror to start tracking.")
    st.stop()

with open(logs_path, "r") as f:
    logs = json.load(f)

# === Prepare data
traits = ["humor", "empathy", "ambition", "flirtiness", "logic", "memory"]
data = {trait: [] for trait in traits}
timestamps = []

for entry in logs:
    timestamps.append(entry.get("timestamp", f"Log {len(timestamps)+1}"))
    for trait in traits:
        data[trait].append(entry.get("traits", {}).get(trait, 0))

# === Line Charts
st.subheader("📈 Trait Growth Over Time")
fig, ax = plt.subplots(figsize=(10, 4))
for trait in traits:
    ax.plot(timestamps, data[trait], label=trait.title())
ax.legend()
ax.set_ylabel("Score")
ax.set_xlabel("Interaction")
ax.set_title("Clarity Trait Evolution")
st.pyplot(fig)

# === Radar Chart (Latest Snapshot)
st.subheader("🧬 Current Trait Profile")
import numpy as np
from math import pi

values = [data[trait][-1] if data[trait] else 0 for trait in traits]
num_vars = len(traits)

angles = [n / float(num_vars) * 2 * pi for n in range(num_vars)]
values += values[:1]
angles += angles[:1]

fig2, ax2 = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
ax2.plot(angles, values, linewidth=1, linestyle='solid')
ax2.fill(angles, values, alpha=0.4)
ax2.set_xticks(angles[:-1])
ax2.set_xticklabels([t.title() for t in traits])
ax2.set_title("Latest Mirror Trait Snapshot")
st.pyplot(fig2)
