import streamlit as st
import datetime
import os
import json
from memory_engine import update_memory
import openai
from dotenv import load_dotenv

# === 🔐 Load API Key ===
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# === 📝 Journal Page Config ===
st.set_page_config(page_title="Journal Mode", page_icon="📝")
st.title("📝 MirrorMe Journal")

st.markdown("""
Welcome to your private journal.  
Write freely. MirrorMe will reflect back, extract insight, and remember.
""")

# === 📅 Journal Entry Input ===
today = datetime.date.today().isoformat()
journal_text = st.text_area("What's on your mind today?", height=250)
submit = st.button("🔒 Save & Reflect")

# === 🔄 Handle Journal Submission ===
if submit and journal_text:
    os.makedirs("journals", exist_ok=True)

    # Save raw journal entry
    with open(f"journals/{today}.txt", "w") as f:
        f.write(journal_text)

    # Reflection prompt
    reflection_prompt = [
        {
            "role": "system",
            "content": "You're MirrorMe — insightful, calm, reflective. Analyze the journal entry and provide deep emotional insight, advice, or a grounding perspective."
        },
        {
            "role": "user",
            "content": f"Journal Entry on {today}:\n\n{journal_text}"
        }
    ]

    with st.spinner("Reflecting..."):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=reflection_prompt
            )
            reflection = response.choices[0].message.content.strip()

            st.success("🪞 Your Reflection:")
            st.markdown(f"> {reflection}")

            # Store into memory engine
            update_memory(journal_text, reflection)

        except Exception as e:
            st.error(f"Error generating reflection: {e}")

# === 📚 View Past Journal Entries ===
if os.path.exists("journals"):
    st.markdown("---")
    st.markdown("### 📅 Past Entries")
    entries = sorted(os.listdir("journals"), reverse=True)
    for entry in entries:
        with open(f"journals/{entry}", "r") as f:
            content = f.read()
        with st.expander(f"{entry.replace('.txt', '')}"):
            st.text(content)
