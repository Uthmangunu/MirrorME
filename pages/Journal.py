import streamlit as st
import datetime
import os
import json
import openai
from dotenv import load_dotenv
from memory_engine import update_memory
from clarity_tracker import log_clarity_change
from mirror_feedback import load_clarity, save_clarity

# === 🔐 Load API Key ===
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

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
    os.makedirs("journals", exist_ok=True)

    # Save raw journal entry
    with open(f"journals/{today}.txt", "w") as f:
        f.write(journal_text)

    # === 🔁 GPT Reflection + Clarity Update Prompt ===
    reflection_prompt = [
        {
            "role": "system",
            "content": (
                "You're MirrorMe — insightful, calm, reflective.\n"
                "First, reflect on the emotional and mental state of the user.\n"
                "Then, based on the tone and themes, suggest adjustments (from -1 to +1) to their clarity traits:\n"
                "humor, empathy, ambition, flirtiness.\n"
                "Return a JSON block with the suggested changes.\n"
                "Example:\n"
                "{'reflection': 'Insight here...', 'adjustments': {'humor': +0.5, 'empathy': -0.5}}"
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

            # === Parse GPT Output
            import ast
            parsed = ast.literal_eval(raw)  # Safer than eval()

            reflection = parsed["reflection"]
            adjustments = parsed["adjustments"]

            st.success("🪞 Your Reflection:")
            st.markdown(f"> {reflection}")

            # === Update Memory
            update_memory(journal_text, reflection)

            # === Apply Clarity Adjustments
            clarity = load_clarity()
            for trait, delta in adjustments.items():
                if trait in clarity:
                    clarity[trait] = round(min(10, max(0, clarity[trait] + delta)), 2)

            save_clarity(clarity)
            log_clarity_change(source="journal")

            st.success("🧠 Mirror's clarity has evolved based on your reflection.")

        except Exception as e:
            st.error(f"❌ Error during reflection or clarity update: {e}")

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
