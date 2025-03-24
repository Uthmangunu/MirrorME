import streamlit as st
from clarity_core import load_clarity, save_clarity

st.set_page_config(page_title="🧬 Mirror Archetype Quiz", page_icon="🪞")
st.title("🧠 MirrorMe Archetype Test")
st.markdown("Answer a few quick questions to discover your baseline Mirror identity.")

archetype_scores = {k: 0 for k in ["Strategist", "Marcher", "Ponderer", "Spark", "Oracle", "Heartbeat", "Renegade", "Sculptor", "Coquette", "Phantom"]}

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
    # More questions here...
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
