# Create a new file for the archetype test implementation: ArchetypeTest.py
archetype_test_code = '''
import streamlit as st
import json
from clarity_core import load_clarity, save_clarity

st.set_page_config(page_title="🧠 Mirror Archetype Test", page_icon="🧪")

st.title("🧠 Discover Your Mirror Archetype")

# Archetype scoring map
archetype_scores = {
    "Strategist": 0,
    "Marcher": 0,
    "Ponderer": 0,
    "Spark": 0,
    "Oracle": 0,
    "Heartbeat": 0,
    "Renegade": 0,
    "Sculptor": 0,
    "Coquette": 0,
    "Phantom": 0
}

questions = [
    {
        "q": "How do you usually process emotion?",
        "options": {
            "Pause and reflect first": ["Ponderer", "Oracle"],
            "Feel deeply and speak when needed": ["Heartbeat", "Coquette"],
            "Stay logical and remove emotion": ["Phantom", "Strategist"],
            "Express it quickly and clearly": ["Marcher", "Renegade"]
        }
    },
    {
        "q": "How do you handle conflict?",
        "options": {
            "Stay quiet and calculate": ["Phantom", "Strategist"],
            "De-escalate and empathize": ["Heartbeat", "Ponderer"],
            "Say it straight, maybe too straight": ["Renegade", "Marcher"],
            "Deflect with humor or distraction": ["Spark", "Coquette"]
        }
    },
    {
        "q": "What kind of space energizes you?",
        "options": {
            "Solo, reflective environments": ["Oracle", "Ponderer"],
            "Goal-oriented, productive zones": ["Sculptor", "Strategist"],
            "Loud, vibrant group dynamics": ["Spark", "Coquette"],
            "Pressure-filled momentum moments": ["Marcher", "Phantom"]
        }
    },
    {
        "q": "What do people praise you for?",
        "options": {
            "Loyalty or emotional grounding": ["Heartbeat", "Ponderer"],
            "Sharp mind and insights": ["Oracle", "Strategist"],
            "Energy, charm, or presence": ["Spark", "Coquette"],
            "Bravery and honesty": ["Renegade", "Marcher"]
        }
    },
    {
        "q": "What do you value most in others?",
        "options": {
            "Emotional intelligence and patience": ["Heartbeat", "Ponderer"],
            "Drive and confidence": ["Marcher", "Renegade"],
            "Intellect and independence": ["Phantom", "Strategist"],
            "Creativity and boldness": ["Spark", "Coquette"]
        }
    },
    {
        "q": "What do you tend to hide from others?",
        "options": {
            "How deeply I feel": ["Phantom", "Sculptor"],
            "Fear of not being chosen": ["Coquette", "Spark"],
            "Self-doubt or hesitation": ["Marcher", "Renegade"],
            "Overthinking everything": ["Strategist", "Oracle", "Ponderer"]
        }
    }
]

responses = []

with st.form("archetype_form"):
    for idx, q in enumerate(questions):
        choice = st.radio(f"**Q{idx+1}. {q['q']}**", list(q["options"].keys()), key=f"q_{idx}")
        responses.append(q["options"][choice])
    submitted = st.form_submit_button("🔮 Reveal My Archetype")

if submitted:
    # Tally scores
    for answer in responses:
        for archetype in answer:
            archetype_scores[archetype] += 1

    # Get highest scoring archetype
    top_archetype = max(archetype_scores, key=archetype_scores.get)

    # Load clarity and assign archetype + base traits
    clarity = load_clarity()
    clarity["archetype"] = top_archetype
    clarity["clarity_level"] = 1
    clarity["total_xp"] = 0
    clarity["xp_to_next_level"] = 100
    clarity["evolution"]["level_history"] = {"1": "2025-03-24T00:00:00"}

    # Optional: assign starting trait scores if you want
    save_clarity(clarity)

    st.success(f"🎭 Your Archetype is: **{top_archetype}**")
    st.balloons()
    st.info("Your Mirror will now grow based on your unique archetype personality.")
'''

# Write ArchetypeTest.py file
archetype_test_path = "/mnt/data/MirrorME-main/MirrorME-main/ArchetypeTest.py"
with open(archetype_test_path, "w") as f:
    f.write(archetype_test_code)

archetype_test_path
