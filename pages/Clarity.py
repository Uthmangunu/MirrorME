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

.clarity-container {
    max-width: 800px;
    margin: 2rem auto;
    padding: 2rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.stButton>button {
    width: 100%;
    background: #FF4B4B;
    color: white;
    border: none;
    padding: 0.8rem;
    border-radius: 8px;
    font-size: 1.1rem;
    transition: all 0.3s ease;
}

.stButton>button:hover {
    background: #e03e3e;
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3);
}

.stCheckbox>label {
    color: white;
}

.stRadio>label {
    color: white;
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
        "Humor": 50,
        "Empathy": 50,
        "Logic": 50,
        "Boldness": 50,
        "Memory": 50,
        "Depth": 50,
        "Adaptability": 50
    }

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
st.session_state.personality_traits = current.get("personality_traits", st.session_state.personality_traits)

# === Main UI ===
st.title("🧠 MirrorMe — Personality Settings")

# === Core Values Section ===
st.subheader("💫 Core Values")
st.caption("Select the values that best represent you")

# Core values options
core_values_options = [
    "Authenticity", "Empathy", "Growth", "Integrity", "Creativity",
    "Resilience", "Curiosity", "Compassion", "Excellence", "Balance",
    "Innovation", "Harmony", "Leadership", "Wisdom", "Joy"
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
st.subheader("⚙️ Personality Traits")
st.caption("Adjust your Mirror's core personality traits")

# Create two columns for trait sliders
col1, col2 = st.columns(2)

with col1:
    st.session_state.personality_traits["Humor"] = st.slider(
        "Humor",
        min_value=0,
        max_value=100,
        value=st.session_state.personality_traits["Humor"],
        key="trait_humor"
    )
    st.session_state.personality_traits["Empathy"] = st.slider(
        "Empathy",
        min_value=0,
        max_value=100,
        value=st.session_state.personality_traits["Empathy"],
        key="trait_empathy"
    )
    st.session_state.personality_traits["Logic"] = st.slider(
        "Logic",
        min_value=0,
        max_value=100,
        value=st.session_state.personality_traits["Logic"],
        key="trait_logic"
    )
    st.session_state.personality_traits["Boldness"] = st.slider(
        "Boldness",
        min_value=0,
        max_value=100,
        value=st.session_state.personality_traits["Boldness"],
        key="trait_boldness"
    )

with col2:
    st.session_state.personality_traits["Memory"] = st.slider(
        "Memory",
        min_value=0,
        max_value=100,
        value=st.session_state.personality_traits["Memory"],
        key="trait_memory"
    )
    st.session_state.personality_traits["Depth"] = st.slider(
        "Depth",
        min_value=0,
        max_value=100,
        value=st.session_state.personality_traits["Depth"],
        key="trait_depth"
    )
    st.session_state.personality_traits["Adaptability"] = st.slider(
        "Adaptability",
        min_value=0,
        max_value=100,
        value=st.session_state.personality_traits["Adaptability"],
        key="trait_adaptability"
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
if st.button("💾 Save Settings"):
    try:
        # Prepare settings data
        settings = {
            "core_values": st.session_state.core_values,
            "personality_traits": st.session_state.personality_traits,
            "updated_at": datetime.now().isoformat()
        }
        
        # Save to Firestore
        success = save_doc("settings", user_id, settings)
        
        if success:
            st.success("✅ Settings saved successfully!")
            # Update local state to match saved data
            st.session_state.core_values = settings["core_values"]
            st.session_state.personality_traits = settings["personality_traits"]
        else:
            st.error("❌ Failed to save settings. Please check your connection and try again.")
            st.info("If the problem persists, try refreshing the page or logging out and back in.")
            
    except Exception as e:
        st.error(f"❌ Error saving settings: {str(e)}")
        st.info("Please try again or contact support if the issue persists.")

st.markdown("""
This system helps us build a digital version of you that's **not just smart**, but deeply **you**. 
Select your core values and adjust your personality traits to create a Mirror that truly reflects who you are.
""")