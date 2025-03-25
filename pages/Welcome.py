import streamlit as st
from clarity_core import load_clarity, save_clarity
import matplotlib.pyplot as plt
from components.feedback_button import feedback_button
feedback_button(user_id)


st.set_page_config(page_title="Welcome to MirrorMe", page_icon="🪞")
st.title("🪞 Welcome to MirrorMe")
st.markdown("Before we begin, help us **tune your Mirror**. This will only take a few minutes and helps MirrorMe reflect your personality with greater clarity.")

clarity = load_clarity()

# === Option to skip setup ===
if "skip_setup" not in st.session_state:
    st.session_state.skip_setup = False

# === Reset guard ===
if clarity.get("archetype") and clarity.get("traits") and not st.session_state.get("force_reset"):
    st.success("✅ Setup already complete. You can go to the main MirrorMe chat.")
    if st.button("➡️ Continue to Mirror"):
        st.switch_page("Home.py")
    st.stop()

if st.button("⏭️ Skip Setup (Not Recommended)"):
    st.session_state.skip_setup = True
    st.switch_page("Home.py")
    st.stop()

# === Step 1: Archetype Test ===
st.subheader("🎭 Step 1: Discover Your Archetype")

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
    {
        "q": "In a group, you are usually the one who...",
        "options": {
            "Observes quietly and speaks last": ["Oracle", "Sculptor"],
            "Brings the jokes and energy": ["Spark", "Coquette"],
            "Takes the lead and drives results": ["Marcher", "Strategist"],
            "Keeps people calm and connected": ["Heartbeat", "Ponderer"]
        }
    }
]

responses = []
with st.form("archetype_and_clarity"):
    st.markdown("#### Answer a few questions to reveal your type:")
    for idx, q in enumerate(questions):
        choice = st.radio(f"**Q{idx+1}: {q['q']}**", list(q["options"].keys()), key=f"q{idx}")
        responses.append(q["options"][choice])

    st.markdown("---")
    st.markdown("#### Rate your traits from 0–10")
    humor = st.slider("😄 Humor", 0, 10, 5)
    empathy = st.slider("❤️ Empathy", 0, 10, 5)
    ambition = st.slider("🔥 Ambition", 0, 10, 5)
    flirtiness = st.slider("😏 Flirtiness", 0, 10, 5)

    temperament = st.selectbox("🌪️ Temperament", ["Calm", "Chaotic", "Balanced"])
    politics = st.selectbox("🏰 Politics", ["Apolitical", "Left", "Right", "Centrist", "Libertarian"])
    depth = st.selectbox("🧠 Depth", ["Surface-level", "Balanced", "Philosopher-core"])

    submitted = st.form_submit_button("🌟 Finalize My Mirror")

if submitted:
    for answer in responses:
        for archetype in answer:
            archetype_scores[archetype] += 1

    top_archetype = max(archetype_scores, key=archetype_scores.get)
    emoji, desc = archetype_meta[top_archetype]

    clarity["archetype"] = top_archetype
    clarity["archetype_meta"] = {"emoji": emoji, "desc": desc}

    clarity["traits"] = {
        "humor": {"score": humor, "xp": 0},
        "empathy": {"score": empathy, "xp": 0},
        "ambition": {"score": ambition, "xp": 0},
        "flirtiness": {"score": flirtiness, "xp": 0}
    }

    clarity["personality_meta"] = {
        "temperament": temperament,
        "politics": politics,
        "depth": depth
    }

    st.session_state["force_reset"] = False
    save_clarity(clarity)

    st.success(f"🎭 You are a {emoji} **{top_archetype}**")
    st.markdown(f"_{desc}_")
    st.balloons()
    st.success("✅ Mirror Personality Profile Saved. You’re ready.")
    if st.button("🚀 Launch My Mirror"):
        st.switch_page("Home.py")
