# journal.py
import streamlit as st
import datetime
import os
import json
import openai
from dotenv import load_dotenv
from user_memory import update_user_memory, load_user_clarity, save_user_clarity
from clarity_tracker import log_clarity_change

# === 🔐 Load API Key ===
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# === 🔒 Require Login ===
if "user" not in st.session_state:
    st.warning("🔐 You must log in first.")
    st.stop()

user_id = st.session_state["user"]["localId"]

# === 📝 Journal Page Config ===
st.set_page_config(page_title="Journal Mode", page_icon="📝")
st.title("📝 MirrorMe Journal")

st.markdown("""
Welcome to your private journal.  
Write freely. MirrorMe will reflect back, extract insight, and update its understanding of you.
""")

# === 📅 Journal Entry Input ===
today = datetime.date.today().isoformat()
journal_text = st.text_area("What's on your mind today?", height=250)
submit = st.button("🔒 Save & Reflect")

# === 🔄 Handle Journal Submission ===
if submit and journal_text:
    user_dir = os.path.join("user_journals", user_id)
    os.makedirs(user_dir, exist_ok=True)

    # Save raw journal entry
    with open(os.path.join(user_dir, f"{today}.txt"), "w") as f:
        f.write(journal_text)

    # === 🔁 GPT Reflection + Clarity Update Prompt ===
    reflection_prompt = [
        {
            "role": "system",
            "content": (
                "You're MirrorMe — insightful, calm, reflective.\n"
                "First, reflect on the emotional and mental state of the user.\n"
                "Then, based on tone and themes, suggest clarity trait adjustments (-1 to +1):\n"
                "humor, empathy, ambition, flirtiness.\n"
                "Return a JSON: {'reflection': '...', 'adjustments': {'trait': value}}"
            )
        },
        {
            "role": "user",
            "content": f"Journal Entry on {today}:\n\n{journal_text}"
        }
    ]

    with st.spinner("Reflecting & Updating..."):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=reflection_prompt
            )
            raw = response.choices[0].message.content.strip()

            # === Parse GPT Output ===
            import ast
            parsed = ast.literal_eval(raw)

            reflection = parsed["reflection"]
            adjustments = parsed["adjustments"]

            st.success("🪞 Your Reflection:")
            st.markdown(f"> {reflection}")

            update_user_memory(user_id, journal_text, reflection)

            clarity = load_user_clarity(user_id)
            for trait, delta in adjustments.items():
                if trait in clarity:
                    clarity[trait] = round(min(10, max(0, clarity[trait] + delta)), 2)

            save_user_clarity(user_id, clarity)
            log_clarity_change(user_id, source="journal")

            st.success("🧠 Mirror's clarity has evolved based on your reflection.")

        except Exception as e:
            st.error(f"❌ Error during reflection or clarity update: {e}")

# === 📚 View Past Entries ===
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