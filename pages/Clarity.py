import streamlit as st
import matplotlib.pyplot as plt
from components.topbar import topbar
from firebase_client import get_doc, save_doc
import json
from datetime import datetime

# === Page Config === (Must be first Streamlit command)
st.set_page_config(
    page_title="MirrorMe - Clarity",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# === Custom CSS ===
st.markdown("""
<style>
.main {
    background-color: #0E1117;
    color: white;
}

.settings-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
}

.section {
    background: rgba(255, 255, 255, 0.05);
    padding: 2rem;
    border-radius: 12px;
    margin-bottom: 2rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.section-title {
    font-size: 1.5rem;
    font-weight: bold;
    color: white;
    margin-bottom: 1rem;
}

.section-description {
    color: #a0a0a0;
    margin-bottom: 1.5rem;
}

.value-option {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem;
    border-radius: 8px;
    transition: all 0.3s ease;
}

.value-option:hover {
    background: rgba(255, 255, 255, 0.1);
}

.value-option.selected {
    background: rgba(255, 75, 75, 0.2);
    border: 1px solid rgba(255, 75, 75, 0.3);
}

.save-button {
    background: #FF4B4B;
    color: white;
    padding: 0.8rem 2rem;
    border-radius: 8px;
    border: none;
    font-size: 1.1rem;
    cursor: pointer;
    transition: all 0.3s ease;
}

.save-button:hover {
    background: #e03e3e;
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3);
}

.success-message {
    color: #4CAF50;
    padding: 1rem;
    border-radius: 8px;
    background: rgba(76, 175, 80, 0.1);
    margin-top: 1rem;
}

.error-message {
    color: #f44336;
    padding: 1rem;
    border-radius: 8px;
    background: rgba(244, 67, 54, 0.1);
    margin-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

# === Initialize Session State ===
if "user" not in st.session_state:
    st.session_state.user = None

if "core_values" not in st.session_state:
    st.session_state.core_values = []

if "personality_traits" not in st.session_state:
    st.session_state.personality_traits = {
        "humor": 50,
        "empathy": 50,
        "logic": 50
    }

if "mirror_tagline" not in st.session_state:
    st.session_state.mirror_tagline = ""

# === Require Login ===
if "user" not in st.session_state or not st.session_state.user:
    st.warning("⚠️ Please Log In to Access This Page.")
    if st.button("🔐 Login"):
        st.switch_page("pages/Login.py")
    st.stop()

user_id = st.session_state.user["localId"]
username = st.session_state.user.get("displayName", "User")

# Add topbar
topbar(username)

# === Load Current Settings ===
current = get_doc("settings", user_id) or {}
st.session_state.core_values = current.get("core_values", [])
st.session_state.personality_traits = current.get("personality_traits", {
    "humor": 50,
    "empathy": 50,
    "logic": 50
})
st.session_state.mirror_tagline = current.get("mirror_tagline", "")

# === Main UI ===
st.markdown('<div class="settings-container">', unsafe_allow_html=True)

# === Core Values Section ===
st.title("🧠 Mirror Clarity")
st.markdown("""
<div class="section-description">
    Define your core values and personality traits to create a Mirror that truly reflects who you are.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="section">
    <div class="section-title">Core Values</div>
    <div class="section-description">Select the values that define your character and guide your decisions.</div>
</div>
""", unsafe_allow_html=True)

# Core values options
core_values_options = [
    "Authenticity", "Growth", "Creativity", "Integrity", "Empathy",
    "Excellence", "Innovation", "Leadership", "Resilience", "Wisdom",
    "Balance", "Curiosity", "Justice", "Passion", "Service"
]

# Create three columns for core values
col1, col2, col3 = st.columns(3)

selected_core_values = []
with col1:
    for value in core_values_options[:5]:
        if st.checkbox(value, key=f"value_{value}", value=value in st.session_state.core_values):
            selected_core_values.append(value)

with col2:
    for value in core_values_options[5:10]:
        if st.checkbox(value, key=f"value_{value}", value=value in st.session_state.core_values):
            selected_core_values.append(value)

with col3:
    for value in core_values_options[10:]:
        if st.checkbox(value, key=f"value_{value}", value=value in st.session_state.core_values):
            selected_core_values.append(value)

# Update session state
st.session_state.core_values = selected_core_values

# === Personality Traits Section ===
st.markdown("""
<div class="section">
    <div class="section-title">Personality Traits</div>
    <div class="section-description">Adjust the sliders to match your personality characteristics.</div>
</div>
""", unsafe_allow_html=True)

# Personality Traits Sliders
for trait, value in st.session_state.personality_traits.items():
    st.session_state.personality_traits[trait] = st.slider(
        trait.title(),
        min_value=0,
        max_value=100,
        value=value,
        key=f"trait_{trait}"
    )

# === Mirror Tagline Section ===
st.markdown("""
<div class="section">
    <div class="section-title">Mirror Tagline</div>
    <div class="section-description">Create a short tagline that captures your Mirror's essence.</div>
</div>
""", unsafe_allow_html=True)

st.session_state.mirror_tagline = st.text_input(
    "Your Mirror's Tagline",
    value=st.session_state.mirror_tagline,
    placeholder="e.g., 'A reflection of growth and authenticity'"
)

# === Trait Visualization ===
st.subheader("📊 Trait Distribution")
trait_names = list(st.session_state.personality_traits.keys())
trait_values = list(st.session_state.personality_traits.values())

# Create bar chart
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(trait_names, trait_values, color='#FF4B4B')
ax.set_ylim(0, 100)
ax.set_title("Your Mirror's Personality Traits")
ax.set_ylabel("Trait Level")

# Add value labels on top of bars
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height)}%',
            ha='center', va='bottom')

# Rotate x-axis labels for better readability
plt.xticks(rotation=45, ha='right')

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Display the chart
st.pyplot(fig)

# === Save Button ===
if st.button("💾 Save Settings", key="save_settings"):
    try:
        # Prepare settings data
        settings = {
            "core_values": st.session_state.core_values,
            "personality_traits": st.session_state.personality_traits,
            "mirror_tagline": st.session_state.mirror_tagline,
            "updated_at": datetime.now().isoformat()
        }
        
        # Save to Firestore
        success = save_doc("settings", user_id, settings)
        
        if success:
            st.success("✅ Settings saved successfully!")
            # Redirect to Home after successful save
            st.switch_page("Home.py")
        else:
            st.error("❌ Failed to save settings. Please check your connection and try again.")
            st.info("If the problem persists, try refreshing the page or logging out and back in.")
            
    except Exception as e:
        st.error(f"❌ Error saving settings: {str(e)}")
        st.info("Please try again or contact support if the issue persists.")

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
This system helps us build a digital version of you that's **not just smart**, but deeply **you**. 
Select your core values and adjust your personality traits to create a Mirror that truly reflects who you are.
""")