import streamlit as st
import datetime
import os
import json
import openai
from dotenv import load_dotenv
from user_memory import update_user_memory, load_user_clarity, save_user_clarity
from clarity_tracker import log_clarity_change
from long_memory import load_long_memory
import ast

# === 🔐 Load API Keys ===
load_dotenv()
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# === 🔒 Require Login ===
if "user" not in st.session_state:
    st.warning("🔐 You must log in first.")
    st.stop()

user_id = st.session_state["user"]["localId"]

# === ⚙️ Load User Settings ===
settings_path = f"user_data/{user_id}/settings.json"
if os.path.exists(settings_path):
    with open(settings_path, "r") as f:
        settings = json.load(f)
else:
    settings = {"dark_mode": False, "voice_id": "3Tjd0DlL3tjpqnkvDu9j", "enable_voice_response": True}

# === 🌒 Apply Dark Mode ===
if settings.get("dark_mode"):
    st.markdown("""
        <style>
        .stApp { background-color: #0e1117; color: white; }
        </style>
    """, unsafe_allow_html=True)

# === 🧠 Dynamic Prompt Generator ===
def generate_prompt(user_id):
    clarity = load_user_clarity(user_id)
    memory = load_long_memory(user_id)

    tone = []
    if clarity["traits"]["humor"]["score"] > 60: tone.append("playful and witty")
    if clarity["traits"]["empathy"]["score"] > 60: tone.append("deeply understanding and emotionally intelligent")
    if clarity["traits"]["ambition"]["score"] > 60: tone.append("motivational and driven")
    if clarity["traits"]["flirtiness"]["score"] > 60: tone.append("charming or flirtatious")

    tone_description = ", and ".join(tone) if tone else "neutral"

    return f"""
You're MirrorMe — insightful, calm, reflective.
Use this tone: {tone_description}.
First reflect on the user's mindset, then suggest adjustments (-1 to 1) to clarity traits:
humor, empathy, ambition, flirtiness.

Return ONLY valid Python-style dictionary in this format (no explanation):
{{'reflection': '...', 'adjustments': {{'humor': 0.5, 'empathy': -0.5}}}}

Avoid extra commentary or notes.
Long-Term Memory:
- Values: {', '.join(memory['core_values'])}
- Goals: {', '.join(memory['goals'])}
- Personality Summary: {memory['personality_summary']}
"""

# === UI Setup ===
st.set_page_config(page_title="Journal Mode", page_icon="📝")
st.title("📝 MirrorMe Journal")

st.markdown("""
Welcome to your private journal.  
Write freely. MirrorMe will reflect back, extract insight, and update its understanding of you.
""")

# === Journal Input ===
today = datetime.date.today().isoformat()
journal_text = st.text_area("What's on your mind today?", height=250)
submit = st.button("🔒 Save & Reflect")

if submit and journal_text:
    user_dir = os.path.join("user_journals", user_id)
    os.makedirs(user_dir, exist_ok=True)

    with open(os.path.join(user_dir, f"{today}.txt"), "w") as f:
        f.write(journal_text)

    prompt = [
        {"role": "system", "content": generate_prompt(user_id)},
        {"role": "user", "content": f"Journal Entry on {today}:\n\n{journal_text}"}
    ]

    with st.spinner("Reflecting & Updating..."):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=prompt
            )
            raw = response.choices[0].message.content.strip()

            try:
                parsed = ast.literal_eval(raw)
            except Exception:
                st.error("⚠️ Could not parse GPT response. Here's the raw output:")
                st.code(raw)
                st.stop()

            reflection = parsed.get("reflection", "No reflection provided.")
            adjustments = parsed.get("adjustments", {})

            st.success("🪞 Your Reflection:")
            st.markdown(f"_{reflection}_")

            update_user_memory(user_id, journal_text, reflection)

            # Update traits correctly
            clarity = load_user_clarity(user_id)
            for trait, delta in adjustments.items():
                if trait in clarity["traits"]:
                    score = clarity["traits"][trait]["score"]
                    new_score = round(min(100, max(0, score + (delta * 10))), 2)
                    clarity["traits"][trait]["score"] = new_score
                    clarity["traits"][trait]["xp"] += int(abs(delta * 10))  # Optional XP bump

            save_user_clarity(user_id, clarity)
            log_clarity_change(user_id, source="journal")

            st.success("🧠 Mirror's clarity has evolved.")

        except Exception as e:
            st.error(f"❌ Error during reflection or clarity update: {e}")

# === Past Entries ===
user_dir = os.path.join("user_journals", user_id)
if os.path.exists(user_dir):
    st.markdown("---")
    st.markdown("### 📅 Past Entries")
    entries = sorted(os.listdir(user_dir), reverse=True)

    for entry in entries:
        with open(os.path.join(user_dir, entry), "r") as f:
            content = f.read()
        with st.expander(entry.replace(".txt", "")):
            st.text(content)
