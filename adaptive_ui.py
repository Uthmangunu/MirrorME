import streamlit as st
import time
from typing import Dict, Any

# === Mood to Color Mapping ===
MOOD_COLOR_MAP = {
    "calm": "#2E8B57",
    "sad": "#4169E1",
    "angry": "#B22222",
    "happy": "#FFD700",
    "neutral": "#708090"
}

# === Determine Mood from Text ===
def detect_mood(text):
    lowered = text.lower()
    if any(word in lowered for word in ["sad", "tired", "lonely", "depressed", "cry", "blue"]):
        return "sad"
    elif any(word in lowered for word in ["angry", "annoyed", "pissed", "frustrated"]):
        return "angry"
    elif any(word in lowered for word in ["happy", "excited", "grateful", "glad", "joyful"]):
        return "happy"
    elif any(word in lowered for word in ["calm", "relaxed", "peaceful", "okay"]):
        return "calm"
    else:
        return "neutral"

# === Mood-Based Highlight Styling ===
def set_mood_background(mood: str) -> None:
    """
    Set the UI background and theme based on the user's mood.
    """
    # Define color schemes for different moods
    mood_colors = {
        "calm": {
            "bg_color": "#E6F3FF",
            "text_color": "#2C3E50",
            "accent_color": "#3498DB"
        },
        "sad": {
            "bg_color": "#F5F5F5",
            "text_color": "#34495E",
            "accent_color": "#95A5A6"
        },
        "excited": {
            "bg_color": "#FFF3E0",
            "text_color": "#E65100",
            "accent_color": "#FF9800"
        },
        "angry": {
            "bg_color": "#FFEBEE",
            "text_color": "#B71C1C",
            "accent_color": "#F44336"
        },
        "playful": {
            "bg_color": "#F3E5F5",
            "text_color": "#4A148C",
            "accent_color": "#9C27B0"
        },
        "thoughtful": {
            "bg_color": "#E8F5E9",
            "text_color": "#1B5E20",
            "accent_color": "#4CAF50"
        },
        "neutral": {
            "bg_color": "#FFFFFF",
            "text_color": "#000000",
            "accent_color": "#2196F3"
        }
    }
    
    # Get color scheme for current mood
    colors = mood_colors.get(mood, mood_colors["neutral"])
    
    # Apply custom CSS
    st.markdown(f"""
        <style>
        .stApp {{
            background-color: {colors['bg_color']};
            color: {colors['text_color']};
        }}
        .stButton>button {{
            background-color: {colors['accent_color']};
            color: white;
            border: none;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            transition: all 0.3s ease;
        }}
        .stButton>button:hover {{
            background-color: {colors['accent_color']}dd;
            transform: translateY(-2px);
        }}
        .stTextInput>div>div>input {{
            background-color: white;
            border: 1px solid {colors['accent_color']};
            border-radius: 5px;
        }}
        </style>
    """, unsafe_allow_html=True)

# === Typing Animation Effect ===
def animated_response(text, delay=0.015):
    animated = ""
    placeholder = st.empty()
    for char in text:
        animated += char
        placeholder.markdown(f"**🧠 MirrorMe:** {animated}█")
        time.sleep(delay)
    placeholder.markdown(f"**🧠 MirrorMe:** {animated}")

# === Display Read-Only Clarity Sliders (Integer-Only) ===
def render_trait_snapshot(clarity):
    st.markdown("### 🎯 Current Trait Snapshot")
    for trait, value in clarity.items():
        st.slider(
            label=trait.capitalize(),
            min_value=0,
            max_value=10,
            value=int(value),
            disabled=True
        )

def adjust_ui_for_persona(persona: str) -> None:
    """
    Adjust UI elements based on the selected persona mode.
    """
    persona_styles = {
        "Professional": {
            "font_family": "Helvetica, Arial, sans-serif",
            "font_size": "14px",
            "spacing": "1.5rem"
        },
        "Friendly": {
            "font_family": "Comic Sans MS, cursive",
            "font_size": "16px",
            "spacing": "1rem"
        },
        "Creative": {
            "font_family": "Georgia, serif",
            "font_size": "16px",
            "spacing": "2rem"
        }
    }
    
    style = persona_styles.get(persona, persona_styles["Professional"])
    
    st.markdown(f"""
        <style>
        .stApp {{
            font-family: {style['font_family']};
            font-size: {style['font_size']};
        }}
        .stMarkdown {{
            margin-bottom: {style['spacing']};
        }}
        </style>
    """, unsafe_allow_html=True)

def create_trait_slider(trait: str, min_val: float = 0.0, max_val: float = 1.0, 
                       default: float = 0.5, key: str = None) -> float:
    """
    Create a styled slider for trait adjustment.
    """
    if key is None:
        key = f"trait_{trait}"
    
    return st.slider(
        trait,
        min_value=min_val,
        max_value=max_val,
        value=default,
        key=key,
        help=f"Adjust your {trait.lower()} level"
    )

def create_value_checkbox(value: str, key: str = None) -> bool:
    """
    Create a styled checkbox for value selection.
    """
    if key is None:
        key = f"value_{value}"
    
    return st.checkbox(
        value,
        key=key,
        help=f"Select if {value.lower()} is one of your core values"
    )
