import streamlit as st
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
from components.feedback_button import feedback_button
feedback_button(user_id)


# Load environment variables (optional for backend use)
load_dotenv()

st.set_page_config(page_title="Mirror Clarity System", page_icon="🫠")
st.title("🫠 MirrorMe Clarity System")
st.subheader("Let us calibrate your Mirror")

st.markdown("""
This system helps us build a digital version of you that's **not just smart**, but deeply **you**. Answer honestly — the better the data, the more _you_ your Mirror becomes.
""")

# === SLIDER + SELECT-BASED PERSONALITY TRAITS ===
st.divider()
st.markdown("### 🔍 Trait-Based Sliders")

clarity_data = {}

clarity_data["humor"] = st.slider("😄 Humor (Dry vs. Playful)", 0, 10, 5)
clarity_data["empathy"] = st.slider("❤️ Empathy (Blunt vs. Compassionate)", 0, 10, 5)
clarity_data["ambition"] = st.slider("🔥 Drive (Laid-back vs. Ruthless)", 0, 10, 5)
clarity_data["flirtiness"] = st.slider("😍 Flirtiness", 0, 10, 4)

# Categorical traits
clarity_data["temperament"] = st.selectbox("🌪️ Temperament", ["Calm", "Chaotic", "Balanced"])
clarity_data["politics"] = st.selectbox("🏰 Political Vibe", ["Apolitical", "Left", "Right", "Centrist", "Libertarian"])
clarity_data["depth"] = st.selectbox("🧠 Depth", ["Surface-level", "Balanced", "Philosopher-core"])

# === RADAR CHART ===
if st.button("🌈 Visualize Personality"):
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})  # ✅ THIS LINE IS CRUCIAL
    labels = ["Humor", "Empathy", "Ambition", "Flirtiness"]
    values = [clarity_data["humor"], clarity_data["empathy"], clarity_data["ambition"], clarity_data["flirtiness"]]
    values += values[:1]  # Close the radar chart loop
    angles = [n / float(len(labels)) * 2 * 3.14159 for n in range(len(labels))]
    angles += angles[:1]

    ax.set_theta_offset(3.14159 / 2)
    ax.set_theta_direction(-1)
    ax.plot(angles, values, linewidth=1, linestyle='solid')
    ax.fill(angles, values, alpha=0.3)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    
    st.pyplot(fig)


# === DEEP PERSONALITY QUESTIONS ===
st.divider()
st.markdown("### 🔮 Personality Blueprint (Open Questions)")

q1 = st.text_area("1. What do you believe people often misunderstand about you?")
q2 = st.text_area("2. What are you like when you're in love or deeply inspired?")
q3 = st.text_area("3. Describe your humor — what actually makes you laugh?")
q4 = st.text_area("4. What is one core belief you would defend at all costs?")
q5 = st.text_area("5. How do you handle conflict or disrespect?")

clarity_data.update({
    "misunderstood": q1,
    "love_state": q2,
    "humor_desc": q3,
    "core_belief": q4,
    "conflict_response": q5
})

# === SUBMIT BUTTON ===
if st.button("🌟 Generate My Mirror"):
    prompt = f"""
You are the Mirror of the user. This is their mental blueprint:

Traits:
- Humor (0-10): {clarity_data['humor']}
- Empathy (0-10): {clarity_data['empathy']}
- Ambition (0-10): {clarity_data['ambition']}
- Flirtiness (0-10): {clarity_data['flirtiness']}
- Temperament: {clarity_data['temperament']}
- Politics: {clarity_data['politics']}
- Depth: {clarity_data['depth']}

Personality Insights:
- Misunderstood Aspects: {clarity_data['misunderstood']}
- In Love / Inspired: {clarity_data['love_state']}
- Humor Description: {clarity_data['humor_desc']}
- Core Belief: {clarity_data['core_belief']}
- Conflict Response: {clarity_data['conflict_response']}

Act like this person. Respond with their tone, wit, emotional range, and logic.
You are not generic ChatGPT — you are their digital mirror.
"""

    st.session_state["system_prompt"] = prompt
    st.session_state["clarity_data"] = clarity_data
    st.success("Mirror personality generated. You can now chat with it in the main app.")
    st.balloons()