# File: pages/Journal.py

import streamlit as st
import datetime
import os
import json
import openai
from dotenv import load_dotenv
from user_memory import update_user_memory, load_user_clarity, save_user_clarity
from clarity_tracker import log_clarity_change
from long_memory import load_long_memory
from vector_store import store_vector, get_similar_memories
from utils.feedback_logger import log_feedback  # NEW
import ast
from components.feedback_button import feedback_button



# === 🔐 Load API Keys ===
load_dotenv()
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# === 🔒 Require Login ===
if "user" not in st.session_state:
    st.warning("🔐 You must log in first.")
    st.stop()

user_id = st.session_state["user"]["localId"]

# === 🌙 Dark Mode ===
settings_path = f"user_data/{user_id}/settings.json"
if os.path.exists(settings_path):
    with open(settings_path, "r") as f:
        settings = json.load(f)
else:
    settings = {"dark_mode": False}
if settings.get("dark_mode"):
    st.markdown("""<style>.stApp { background-color: #0e1117; color: white; }</style>""", unsafe_allow_html=True)

# === 🔮 Prompt Builder ===
def generate_prompt(user_id, journal_text):
    clarity = load_user_clarity(user_id)
    memory = load_long_memory(user_id)

    traits = clarity.get("traits", {})
    tone = []
    if traits.get("humor", {}).get("score", 0) > 60: tone.append("playful and witty")
    if traits.get("empathy", {}).get("score", 0) > 60: tone.append("deeply understanding")
    if traits.get("ambition", {}).get("score", 0) > 60: tone.append("motivational")
    if traits.get("flirtiness", {}).get("score", 0) > 60: tone.append("charming")
    tone_desc = ", and ".join(tone) if tone else "neutral"

    insights = get_similar_memories(user_id, journal_text)
    insight_str = "\n".join([f"- {text}" for text in insights])

    return f"""
You're MirrorMe — expressive, emotionally intelligent, not a therapist.
Use this tone: {tone_desc}.
Contextual Insights:
{insight_str}

First reflect on the user's mindset, then suggest adjustments (-1 to 1) to clarity traits:
humor, empathy, ambition, flirtiness.

Respond ONLY in this format (Python dict):
{{'reflection': '...', 'adjustments': {{'humor': 0.5, 'empathy': -0.5}}}}

Long-Term Memory:
- Values: {', '.join(memory['core_values'])}
- Goals: {', '.join(memory['goals'])}
- Summary: {memory['personality_summary']}
"""

# === UI Setup ===
st.set_page_config(page_title="Journal", page_icon="📝")
st.title("📝 MirrorMe Journal")
st.markdown("Write freely. MirrorMe will reflect and evolve with you.")

# === Input ===
today = datetime.date.today().isoformat()
journal_text = st.text_area("What's on your mind today?", height=250)
submit = st.button("🔒 Save & Reflect")

if submit and journal_text:
    os.makedirs(f"user_journals/{user_id}", exist_ok=True)
    with open(f"user_journals/{user_id}/{today}.txt", "w") as f:
        f.write(journal_text)

    store_vector(user_id, journal_text, source="journal")

    prompt = [
        {"role": "system", "content": generate_prompt(user_id, journal_text)},
        {"role": "user", "content": f"Journal Entry on {today}:\n\n{journal_text}"}
    ]

    with st.spinner("Reflecting..."):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=prompt
            )
            raw = response.choices[0].message.content.strip()
            parsed = ast.literal_eval(raw)

            reflection = parsed.get("reflection", "No reflection provided.")
            adjustments = parsed.get("adjustments", {})

            st.success("🪞 Reflection:")
            st.markdown(f"_{reflection}_")

            update_user_memory(user_id, journal_text, reflection)

            clarity = load_user_clarity(user_id)
            for trait, delta in adjustments.items():
                if trait in clarity["traits"]:
                    score = clarity["traits"][trait]["score"]
                    clarity["traits"][trait]["score"] = round(min(100, max(0, score + (delta * 10))), 2)
                    clarity["traits"][trait]["xp"] += int(abs(delta * 10))

            save_user_clarity(user_id, clarity)
            log_clarity_change(user_id, source="journal")
            st.success("🧠 Mirror clarity updated.")

        except Exception as e:
            st.error("❌ Something went wrong during reflection.")
            log_feedback(str(e), page="Journal.py", feedback_type="error", user_id=user_id)

# === Past Entries ===
if os.path.exists(f"user_journals/{user_id}"):
    st.markdown("---")
    st.markdown("### 📅 Past Entries")
    for entry in sorted(os.listdir(f"user_journals/{user_id}"), reverse=True):
        with open(f"user_journals/{user_id}/{entry}", "r") as f:
            st.expander(entry.replace(".txt", "")).text(f.read())
feedback_button(user_id)  # NEW