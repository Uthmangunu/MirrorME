# Updated ArchetypeTest.py that saves archetype info to clarity_data.json

updated_archetype_test_code = '''
import streamlit as st
from clarity_core import load_clarity, save_clarity

st.set_page_config(page_title="🧬 Mirror Archetype Quiz", page_icon="🪞")
st.title("🧠 MirrorMe Archetype Test")
st.markdown("Discover your baseline Mirror identity. Who are you at your core?")

# Archetypes: emoji + short description
archetype_meta = {
    "Strategist": ["♟️", "Strategic, calm, structured — always 3 steps ahead."],
    "Marcher": ["🤬", "Bold, driven, direct — you turn pressure into action."],
    "Ponderer": ["🌀", "Reflective, emotional, inward — you move through meaning."],
    "Spark": ["⚡", "Witty, chaotic, vibrant — you bring life into every room."],
    "Oracle": ["🔮", "Philosophical, abstract, observant — you see beneath things."],
    "Heartbeat": ["💗", "Loyal, grounding, emotionally present — you hold space."],
    "Renegade": ["😈", "Unfiltered, raw, honest — you challenge what doesn’t feel real."],
    "Sculptor": ["🗿", "Disciplined, precise, reserved — you build slowly and solidly."],
    "Coquette": ["😏", "Flirty, smooth, intuitive — you read between every line."],
    "Phantom": ["🕷", "Detached, elusive, hyper-logical — you stay unreadable."]
}

archetype_scores = {k: 0 for k in archetype_meta.keys()}

questions = [
    {
        "q": "How do you process emotion?",
        "options": {
            "Pause and reflect deeply": ["Ponderer", "Oracle"],
            "Feel it but stay composed": ["Heartbeat", "Coquette"],
            "Try to remove it from decision-making": ["Phantom", "Strategist"],
            "Say it directly and move on": ["Renegade", "Marcher"]
        }
    },
    {
        "q": "In a group, you tend to...",
        "options": {
            "Observe quietly and step in later": ["Oracle", "Sculptor"],
            "Take the lead and organize": ["Marcher", "Strategist"],
            "Keep the energy high and fun": ["Spark", "Coquette"],
            "Support and listen more than speak": ["Heartbeat", "Ponderer"]
        }
    },
    {
        "q": "People often say you are...",
        "options": {
            "Calm and wise": ["Oracle", "Phantom"],
            "Fun and magnetic": ["Spark", "Coquette"],
            "Bold and honest": ["Marcher", "Renegade"],
            "Kind and supportive": ["Heartbeat", "Ponderer"]
        }
    },
    {
        "q": "Which energy feels most like you?",
        "options": {
            "Quiet precision and focus": ["Sculptor", "Phantom"],
            "Chaos, jokes, and ideas": ["Spark", "Coquette"],
            "Depth, emotions, and stillness": ["Ponderer", "Heartbeat"],
            "Directness, speed, and fire": ["Marcher", "Renegade"]
        }
    },
    {
        "q": "You value people who are...",
        "options": {
            "Emotionally intelligent": ["Heartbeat", "Ponderer"],
            "Independent thinkers": ["Strategist", "Phantom"],
            "Fun and confident": ["Spark", "Coquette"],
            "Straightforward and real": ["Marcher", "Renegade"]
        }
    }
]

responses = []
with st.form("archetype_form"):
    for idx, q in enumerate(questions):
        choice = st.radio(f"**Q{idx+1}: {q['q']}**", list(q["options"].keys()), key=f"q{idx}")
        responses.append(q["options"][choice])
    submitted = st.form_submit_button("🔮 Reveal My Archetype")

if submitted:
    for answer in responses:
        for archetype in answer:
            archetype_scores[archetype] += 1

    top_archetype = max(archetype_scores, key=archetype_scores.get)
    emoji, desc = archetype_meta[top_archetype]

    # Save to clarity_data.json
    clarity = load_clarity()
    clarity["archetype"] = top_archetype
    clarity["archetype_meta"] = {
        "emoji": emoji,
        "desc": desc
    }
    save_clarity(clarity)

    st.success(f"🎭 You are a {emoji} **{top_archetype}**")
    st.markdown(f"_{desc}_")
    st.balloons()
    st.info("Your Mirror will now reflect this identity at the beginning.")
'''

# Save it to the correct location
final_archetype_test_path = "/mnt/data/MirrorME-main/ArchetypeTest.py"
with open(final_archetype_test_path, "w") as f:
    f.write(updated_archetype_test_code)

final_archetype_test_path
