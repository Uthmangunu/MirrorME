import streamlit as st
import time
from typing import Dict, Any

# === Mood to Color Mapping ===
MOOD_COLORS = {
    "calm": {
        "color": "#3498DB",  # Soft blue
        "glow": "#3498DB33"  # Semi-transparent version for glow
    },
    "sad": {
        "color": "#95A5A6",  # Muted gray
        "glow": "#95A5A633"
    },
    "playful": {
        "color": "#F1C40F",  # Bright yellow
        "glow": "#F1C40F33"
    },
    "excited": {
        "color": "#2ECC71",  # Vibrant green
        "glow": "#2ECC7133"
    },
    "angry": {
        "color": "#E74C3C",  # Deep red
        "glow": "#E74C3C33"
    },
    "thoughtful": {
        "color": "#9B59B6",  # Purple
        "glow": "#9B59B633"
    },
    "neutral": {
        "color": "#BDC3C7",  # Light gray
        "glow": "#BDC3C733"
    }
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
    Now uses a more subtle approach with the mood indicator.
    """
    # Define color schemes for different moods
    mood_colors = {
        "calm": {
            "bg_color": "#FFFFFF",
            "text_color": "#2C3E50",
            "accent_color": "#3498DB"
        },
        "sad": {
            "bg_color": "#FFFFFF",
            "text_color": "#34495E",
            "accent_color": "#95A5A6"
        },
        "excited": {
            "bg_color": "#FFFFFF",
            "text_color": "#E65100",
            "accent_color": "#F1C40F"
        },
        "angry": {
            "bg_color": "#FFFFFF",
            "text_color": "#B71C1C",
            "accent_color": "#E74C3C"
        },
        "playful": {
            "bg_color": "#FFFFFF",
            "text_color": "#4A148C",
            "accent_color": "#9B59B6"
        },
        "thoughtful": {
            "bg_color": "#FFFFFF",
            "text_color": "#1B5E20",
            "accent_color": "#2ECC71"
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

def render_mood_indicator(mood: str, size: int = 20) -> None:
    """
    Render a small, colored circle indicator for the current mood.
    Includes hover effect and animation.
    """
    colors = MOOD_COLORS.get(mood, MOOD_COLORS["neutral"])
    
    st.markdown(f"""
        <style>
        .mood-indicator {{
            display: inline-block;
            width: {size}px;
            height: {size}px;
            background-color: {colors['color']};
            border-radius: 50%;
            margin-left: 10px;
            position: relative;
            animation: pulse 2s infinite;
        }}
        .mood-indicator::after {{
            content: "Mood: {mood.capitalize()}";
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            background-color: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 12px;
            white-space: nowrap;
            opacity: 0;
            transition: opacity 0.3s;
            pointer-events: none;
        }}
        .mood-indicator:hover::after {{
            opacity: 1;
        }}
        @keyframes pulse {{
            0% {{
                box-shadow: 0 0 0 0 {colors['glow']};
            }}
            70% {{
                box-shadow: 0 0 0 10px {colors['glow']}00;
            }}
            100% {{
                box-shadow: 0 0 0 0 {colors['glow']}00;
            }}
        }}
        </style>
        <div class="mood-indicator"></div>
    """, unsafe_allow_html=True)
