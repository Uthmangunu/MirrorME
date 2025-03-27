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

# Set page config first (must be the first Streamlit command)
st.set_page_config(page_title="MirrorMe - Clarity", page_icon="🧠")

# Check if user is logged in
if "user" not in st.session_state or not st.session_state.user:
    st.warning("⚠️ Please Log In to Access This Page.")
    if st.button("🔐 Login"):
        st.markdown("""
            <script>
                window.location.href = "Login";
            </script>
        """, unsafe_allow_html=True)
    st.stop()

# Get user ID from session state
user_id = st.session_state.user["localId"]

# Initialize session state for traits and values if not exists
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
        "Core Values": [],
        "Beliefs": [],
        "Goals": [],
        "Interests": []
    }
if "persona_mode" not in st.session_state:
    st.session_state.persona_mode = "Balanced"  # Set default to match available options
if "current_mood" not in st.session_state:
    st.session_state.current_mood = "Neutral"
if "mood_changed" not in st.session_state:
    st.session_state.mood_changed = False
if "last_mood_change_time" not in st.session_state:
    st.session_state.last_mood_change_time = time.time()

# Load existing clarity data
clarity_data = load_clarity()

# === Main UI ===
st.title("🧠 MirrorMe — Personality Settings")

# === Persona Mode Selection ===
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
    st.session_state.traits["Humor"] = create_trait_slider("Humor", st.session_state.traits["Humor"])
    st.session_state.traits["Empathy"] = create_trait_slider("Empathy", st.session_state.traits["Empathy"])
    st.session_state.traits["Logic"] = create_trait_slider("Logic", st.session_state.traits["Logic"])
    st.session_state.traits["Boldness"] = create_trait_slider("Boldness", st.session_state.traits["Boldness"])

with col2:
    st.session_state.traits["Memory"] = create_trait_slider("Memory", st.session_state.traits["Memory"])
    st.session_state.traits["Depth"] = create_trait_slider("Depth", st.session_state.traits["Depth"])
    st.session_state.traits["Adaptability"] = create_trait_slider("Adaptability", st.session_state.traits["Adaptability"])

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

# Core Values
st.markdown("#### Core Values")
st.session_state.values["Core Values"] = create_value_checkbox(
    "What Are Your Core Values?",
    ["Honesty", "Integrity", "Creativity", "Growth", "Connection", "Freedom", "Justice", "Balance"],
    st.session_state.values["Core Values"]
)

# Beliefs
st.markdown("#### Beliefs")
st.session_state.values["Beliefs"] = create_value_checkbox(
    "What Do You Believe In?",
    ["Personal Growth", "Social Justice", "Environmental Care", "Scientific Progress", "Spiritual Growth", "Community", "Innovation", "Tradition"],
    st.session_state.values["Beliefs"]
)

# Goals
st.markdown("#### Goals")
st.session_state.values["Goals"] = create_value_checkbox(
    "What Are Your Goals?",
    ["Career Growth", "Personal Development", "Health & Wellness", "Relationships", "Learning", "Financial Success", "Creative Expression", "Social Impact"],
    st.session_state.values["Goals"]
)

# Interests
st.markdown("#### Interests")
st.session_state.values["Interests"] = create_value_checkbox(
    "What Are Your Interests?",
    ["Technology", "Arts", "Science", "Philosophy", "Sports", "Travel", "Music", "Literature"],
    st.session_state.values["Interests"]
)

# Save personality data
if st.button("💾 Save Profile"):
    try:
        # Get values from session state
        core_values = st.session_state.core_values if hasattr(st.session_state, "core_values") else []
        beliefs = st.session_state.beliefs if hasattr(st.session_state, "beliefs") else []
        goals = st.session_state.goals if hasattr(st.session_state, "goals") else []
        interests = st.session_state.interests if hasattr(st.session_state, "interests") else []
        
        # Create values dictionary
        values = {
            "Core Values": core_values,
            "Beliefs": beliefs,
            "Goals": goals,
            "Interests": interests
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