import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from dotenv import load_dotenv
import os
from clarity_core import (
    extract_values_from_text, 
    detect_mood_from_text, 
    apply_trait_xp,
    analyze_feedback,
    load_clarity,
    save_clarity
)
from adaptive_ui import set_mood_background, adjust_ui_for_persona, create_trait_slider, create_value_checkbox
from components.feedback_button import feedback_button
from google.cloud import firestore
from datetime import datetime
import time
import json
from components.topbar import topbar
from firebase_client import get_doc, save_doc

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

.clarity-title {
    text-align: center;
    font-size: 2rem;
    margin-bottom: 2rem;
    color: white;
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

if "traits" not in st.session_state:
    st.session_state.traits = {
        "Humor": 50,
        "Empathy": 50,
        "Logic": 50,
        "Boldness": 50,
        "Memory": 50,
        "Depth": 50,
        "Adaptability": 50
    }

if "values" not in st.session_state:
    st.session_state.values = {
        "core_values": [],
        "beliefs": [],
        "goals": [],
        "interests": []
    }

if "persona_mode" not in st.session_state:
    st.session_state.persona_mode = "Balanced"

if "current_mood" not in st.session_state:
    st.session_state.current_mood = "Neutral"

if "mood_changed" not in st.session_state:
    st.session_state.mood_changed = False

if "last_mood_change_time" not in st.session_state:
    st.session_state.last_mood_change_time = time.time()

if "show_settings" not in st.session_state:
    st.session_state.show_settings = False

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
st.session_state.mirror_tagline = current.get("mirror_tagline", "")

# Load existing clarity data
clarity_data = load_clarity()

# Update session state with existing data if available
if clarity_data and "values" in clarity_data:
    st.session_state.values.update(clarity_data["values"])

# === Main UI ===
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🧠 MirrorMe — Personality Settings")
with col2:
    if st.button("⚙️ Settings"):
        st.session_state.show_settings = not st.session_state.show_settings

# Settings Panel
if st.session_state.show_settings:
    with st.expander("⚙️ Settings", expanded=True):
        st.subheader("🎭 Persona Mode")
        persona_mode = st.selectbox(
            "Choose How Your Mirror Should Behave",
            ["Balanced", "Empathetic", "Analytical", "Creative", "Professional"],
            index=["Balanced", "Empathetic", "Analytical", "Creative", "Professional"].index(st.session_state.persona_mode)
        )
        st.session_state.persona_mode = persona_mode

# === Trait Engine 2.0 ===
st.subheader("⚙️ Trait Engine 2.0")
st.caption("Adjust Your Mirror's Core Personality Traits")

# Create two columns for trait sliders
col1, col2 = st.columns(2)

with col1:
    st.session_state.traits["Humor"] = create_trait_slider("Humor", st.session_state.traits["Humor"], key="trait_humor")
    st.session_state.traits["Empathy"] = create_trait_slider("Empathy", st.session_state.traits["Empathy"], key="trait_empathy")
    st.session_state.traits["Logic"] = create_trait_slider("Logic", st.session_state.traits["Logic"], key="trait_logic")
    st.session_state.traits["Boldness"] = create_trait_slider("Boldness", st.session_state.traits["Boldness"], key="trait_boldness")

with col2:
    st.session_state.traits["Memory"] = create_trait_slider("Memory", st.session_state.traits["Memory"], key="trait_memory")
    st.session_state.traits["Depth"] = create_trait_slider("Depth", st.session_state.traits["Depth"], key="trait_depth")
    st.session_state.traits["Adaptability"] = create_trait_slider("Adaptability", st.session_state.traits["Adaptability"], key="trait_adaptability")

# === Trait Visualization ===
st.subheader("📊 Trait Distribution")
trait_names = list(st.session_state.traits.keys())
trait_values = list(st.session_state.traits.values())

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

# === Values Section ===
st.subheader("💫 Core Values & Beliefs")
st.caption("Share What Matters Most to You")

# Ensure values dictionary exists
if "values" not in st.session_state:
    st.session_state.values = {
        "core_values": [],
        "beliefs": [],
        "goals": [],
        "interests": []
    }

# Core Values
st.markdown("#### Core Values")
core_values_options = ["Honesty", "Integrity", "Creativity", "Growth", "Connection", "Freedom", "Justice", "Balance"]
selected_core_values = create_value_checkbox(
    "What Are Your Core Values?",
    core_values_options,
    st.session_state.values.get("core_values", []),
    key="core_values"
)
st.session_state.values["core_values"] = selected_core_values

# Beliefs
st.markdown("#### Beliefs")
beliefs_options = ["Personal Growth", "Social Justice", "Environmental Care", "Scientific Progress", "Spiritual Growth", "Community", "Innovation", "Tradition"]
selected_beliefs = create_value_checkbox(
    "What Do You Believe In?",
    beliefs_options,
    st.session_state.values.get("beliefs", []),
    key="beliefs"
)
st.session_state.values["beliefs"] = selected_beliefs

# Goals
st.markdown("#### Goals")
goals_options = ["Career Growth", "Personal Development", "Health & Wellness", "Relationships", "Learning", "Financial Success", "Creative Expression", "Social Impact"]
selected_goals = create_value_checkbox(
    "What Are Your Goals?",
    goals_options,
    st.session_state.values.get("goals", []),
    key="goals"
)
st.session_state.values["goals"] = selected_goals

# Interests
st.markdown("#### Interests")
interests_options = ["Technology", "Arts", "Science", "Philosophy", "Sports", "Travel", "Music", "Literature"]
selected_interests = create_value_checkbox(
    "What Are Your Interests?",
    interests_options,
    st.session_state.values.get("interests", []),
    key="interests"
)
st.session_state.values["interests"] = selected_interests

# Save personality data
if st.button("💾 Save Profile"):
    try:
        # Ensure values dictionary exists
        if "values" not in st.session_state:
            st.session_state.values = {
                "core_values": [],
                "beliefs": [],
                "goals": [],
                "interests": []
            }
        
        # Get values from session state
        values = {
            "core_values": st.session_state.values.get("core_values", []),
            "beliefs": st.session_state.values.get("beliefs", []),
            "goals": st.session_state.values.get("goals", []),
            "interests": st.session_state.values.get("interests", [])
        }
        
        # Save to Firestore
        db = get_firestore_client()
        if db:
            personality_ref = db.collection("users").document(user_id).collection("personality").document("values")
            personality_ref.set(values)
            
            # Update clarity data
            clarity_data = load_clarity()
            clarity_data["values"] = values
            save_clarity(clarity_data)
            
            st.success("✅ Profile Saved Successfully!")
        else:
            st.error("Failed to Connect to Database. Please Try Again Later.")
    except Exception as e:
        st.error(f"❌ Error Saving Profile: {str(e)}")

# Feedback system
st.subheader("💡 Feedback")
feedback = st.text_area(
    "How Well Does Your Mirror Reflect Your Personality?",
    height=100
)

if feedback:
    # Analyze feedback and apply XP to relevant traits
    trait_xp = analyze_feedback(feedback)
    for trait, xp in trait_xp.items():
        apply_trait_xp(trait, xp)
    
    # Update session state traits based on new XP
    clarity = load_clarity()
    st.session_state.traits = clarity.get("traits", st.session_state.traits)
    st.success("✅ Feedback Processed Successfully!")

def get_firestore_client():
    """Initialize and return a Firestore client."""
    try:
        from google.cloud import firestore
        return firestore.Client()
    except Exception as e:
        st.error(f"Failed to initialize Firestore client: {str(e)}")
        return None

# Add feedback button after user authentication
feedback_button(user_id)

st.markdown("""
This system helps us build a digital version of you that's **not just smart**, but deeply **you**. Answer honestly — the better the data, the more _you_ your Mirror becomes.
""")