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
    load_clarity
)
from adaptive_ui import set_mood_background, adjust_ui_for_persona, create_trait_slider, create_value_checkbox
from components.feedback_button import feedback_button
from google.cloud import firestore
from datetime import datetime

# Set page config first (must be the first Streamlit command)
st.set_page_config(page_title="MirrorMe - Clarity", page_icon="🧠")

# Check if user is logged in
if "user" not in st.session_state or not st.session_state.user:
    st.warning("⚠️ Please log in to access this page.")
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
        "humor": 50,
        "empathy": 50,
        "logic": 50,
        "boldness": 50,
        "memory": 50,
        "depth": 50,
        "adaptability": 50
    }
if "values" not in st.session_state:
    st.session_state.values = {
        "core_values": [],
        "beliefs": [],
        "goals": [],
        "interests": []
    }
if "persona_mode" not in st.session_state:
    st.session_state.persona_mode = "balanced"  # Set default to match available options
if "current_mood" not in st.session_state:
    st.session_state.current_mood = "neutral"
if "mood_changed" not in st.session_state:
    st.session_state.mood_changed = False
if "last_mood_change_time" not in st.session_state:
    st.session_state.last_mood_change_time = 0

# Sidebar for persona selection and mood display
with st.sidebar:
    st.title("🔮 Mirror Settings")
    
    # Persona mode selection
    st.markdown("### 🎭 Mirror Persona")
    persona_mode = st.selectbox(
        "Choose how your Mirror should behave",
        options=["balanced", "professional", "casual", "creative", "analytical"],
        index=["balanced", "professional", "casual", "creative", "analytical"].index(st.session_state.persona_mode)
    )
    st.session_state.persona_mode = persona_mode
    
    # Display current mood
    st.markdown(f"### Current Mood: {st.session_state.current_mood.capitalize()}")
    
    # Mood detection from recent messages
    if 'recent_messages' in st.session_state:
        current_mood = detect_mood_from_text(" ".join(st.session_state.recent_messages[-3:]))
        if current_mood != st.session_state.current_mood:
            st.session_state.current_mood = current_mood
            st.experimental_rerun()

# Main content
st.title("MirrorMe Personality Mirror")

# Apply UI adjustments based on persona and mood
adjust_ui_for_persona(st.session_state.persona_mode)
set_mood_background(st.session_state.current_mood)

# Trait Engine 2.0
st.header("🎭 Trait Engine 2.0")
st.markdown("Adjust your Mirror's personality traits to match your own:")

# Create two columns for trait sliders
col1, col2 = st.columns(2)

with col1:
    st.session_state.traits['humor'] = create_trait_slider("Humor", key="trait_humor")
    st.session_state.traits['empathy'] = create_trait_slider("Empathy", key="trait_empathy")
    st.session_state.traits['logic'] = create_trait_slider("Logic", key="trait_logic")
    st.session_state.traits['boldness'] = create_trait_slider("Boldness", key="trait_boldness")

with col2:
    st.session_state.traits['memory'] = create_trait_slider("Memory", key="trait_memory")
    st.session_state.traits['depth'] = create_trait_slider("Depth", key="trait_depth")
    st.session_state.traits['adaptability'] = create_trait_slider("Adaptability", key="trait_adaptability")

# Values System
st.header("💫 Core Values")
st.markdown("Share your core values and beliefs:")

values_text = st.text_area(
    "Describe your values and beliefs:",
    height=150,
    help="Your Mirror will learn from your values to better reflect your personality"
)

if values_text:
    extracted_values = extract_values_from_text(values_text)
    
    # Update the appropriate category in values
    for category, values in extracted_values.items():
        if category in st.session_state.values:
            st.session_state.values[category] = values
    
    # Display extracted values
    st.markdown("### Detected Values:")
    for category, values in extracted_values.items():
        if values:  # Only show categories that have values
            st.markdown(f"#### {category.replace('_', ' ').title()}:")
            for value in values:
                st.markdown(f"- {value.capitalize()}")

# Personality Visualization
st.header("🎯 Personality Radar")
fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))

# Plot traits on radar chart
traits = list(st.session_state.traits.keys())
values = list(st.session_state.traits.values())

angles = np.linspace(0, 2*np.pi, len(traits), endpoint=False)
values = np.concatenate((values, [values[0]]))  # Close the plot
angles = np.concatenate((angles, [angles[0]]))  # Close the plot

ax.plot(angles, values)
ax.fill(angles, values, alpha=0.25)
ax.set_xticks(angles[:-1])
ax.set_xticklabels(traits)

plt.tight_layout()
st.pyplot(fig)

def get_firestore_client():
    """Initialize and return a Firestore client."""
    try:
        from google.cloud import firestore
        return firestore.Client()
    except Exception as e:
        st.error(f"Failed to initialize Firestore client: {str(e)}")
        return None

# Save personality data
if st.button("Save Personality Profile"):
    try:
        # Get current user's data
        user_data = {
            "user_id": user_id,
            "traits": st.session_state.traits,
            "values": st.session_state.values,
            "persona_mode": st.session_state.persona_mode,
            "current_mood": st.session_state.current_mood,
            "mood_changed": st.session_state.mood_changed,
            "last_mood_change_time": st.session_state.last_mood_change_time,
            "last_updated": datetime.now().isoformat()
        }
        
        # Save to Firestore
        db = get_firestore_client()
        if db:
            user_ref = db.collection('users').document(user_id)
            user_ref.set(user_data, merge=True)
            st.success("Personality profile saved successfully!")
        else:
            st.error("Failed to connect to database. Please try again later.")
    except Exception as e:
        st.error(f"Error saving profile: {str(e)}")

# Feedback system
st.header("💡 Feedback")
feedback = st.text_area(
    "How well does your Mirror reflect your personality?",
    height=100
)

if feedback:
    # Analyze feedback and apply XP to relevant traits
    trait_xp = analyze_feedback(feedback)
    for trait, xp in trait_xp.items():
        apply_trait_xp(trait, xp)
    
    # Update session state traits based on new XP
    clarity = load_clarity()
    for trait in st.session_state.traits:
        if trait in clarity["traits"]:
            st.session_state.traits[trait] = clarity["traits"][trait]["score"] / 100
    
    st.success("Thank you for your feedback! Your Mirror is learning...")
    st.experimental_rerun()

# Add feedback button after user authentication
feedback_button(user_id)

st.markdown("""
This system helps us build a digital version of you that's **not just smart**, but deeply **you**. Answer honestly — the better the data, the more _you_ your Mirror becomes.
""")