import streamlit as st
import datetime
import openai
import os
import ast
from dotenv import load_dotenv
from user_memory import update_user_memory, load_user_clarity, save_user_clarity
from clarity_tracker import log_clarity_change
from long_memory import load_long_memory
from journal_memory import save_journal_entry, get_journal_entries

# === 🔐 Load API Key ===
load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === Require Login ===
if "user" not in st.session_state:
    st.warning("🔒 You must log in first.")
    st.stop()
user_id = st.session_state["user"]["localId"]

# === UI Setup ===
st.set_page_config(page_title="Journal Mode", page_icon="📝")
st.title("📝 MirrorMe Journal")
st.markdown("""
Welcome to your private journal.  
Write freely. MirrorMe will reflect back, extract insight, and update its understanding of you.
""")

# === Generate Prompt ===
def generate_prompt(user_id):
    clarity = load_user_clarity(user_id)
    memory = load_long_memory(user_id)
    tone = []
    traits = clarity.get("traits", {})
    if traits.get("humor", {}).get("score", 0) > 60: tone.append("playful and witty")
    if traits.get("empathy", {}).get("score", 0) > 60: tone.append("deeply understanding and emotionally intelligent")
    if traits.get("ambition", {}).get("score", 0) > 60: tone.append("motivational and driven")
    if traits.get("flirtiness", {}).get("score", 0) > 60: tone.append("charming or flirtatious")
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

# === Journal Input ===
journal_text = st.text_area("What's on your mind today?", height=250)
submit = st.button("🔒 Save & Reflect")

if submit and journal_text:
    prompt = [
        {"role": "system", "content": generate_prompt(user_id)},
        {"role": "user", "content": f"Journal Entry:\n\n{journal_text}"}
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

            clarity = load_user_clarity(user_id)
            for trait, delta in adjustments.items():
                if trait in clarity["traits"]:
                    score = clarity["traits"][trait]["score"]
                    new_score = round(min(100, max(0, score + (delta * 10))), 2)
                    clarity["traits"][trait]["score"] = new_score
                    clarity["traits"][trait]["xp"] += int(abs(delta * 10))

            save_user_clarity(user_id, clarity)
            log_clarity_change(user_id, source="journal")
            save_journal_entry(user_id, journal_text, reflection, adjustments)

            st.success("🧠 Mirror's clarity has evolved.")

        except Exception as e:
            st.error(f"❌ Error during reflection or clarity update: {e}")

# === Past Entries ===
entries = get_journal_entries(user_id)
if entries:
    st.markdown("---")
    st.markdown("### 📅 Past Entries")
    for entry in entries:
        with st.expander(entry["date"]):
            st.text_area("Text", entry["text"], height=100, disabled=True)
            st.caption(f"Reflection: {entry.get('reflection', '')}")
