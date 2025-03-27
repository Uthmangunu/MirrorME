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
    Set the UI theme based on the user's mood.
    Only affects accent colors, not background.
    """
    # Define color schemes for different moods
    mood_colors = {
        "calm": {
            "text_color": "#2C3E50",
            "accent_color": "#3498DB"
        },
        "sad": {
            "text_color": "#34495E",
            "accent_color": "#95A5A6"
        },
        "excited": {
            "text_color": "#E65100",
            "accent_color": "#F1C40F"
        },
        "angry": {
            "text_color": "#B71C1C",
            "accent_color": "#E74C3C"
        },
        "playful": {
            "text_color": "#4A148C",
            "accent_color": "#9B59B6"
        },
        "thoughtful": {
            "text_color": "#1B5E20",
            "accent_color": "#2ECC71"
        },
        "neutral": {
            "text_color": "#000000",
            "accent_color": "#2196F3"
        }
    }
    
    # Get color scheme for current mood
    colors = mood_colors.get(mood, mood_colors["neutral"])
    
    # Apply custom CSS - only affecting accent colors
    st.markdown(f"""
        <style>
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

def render_mood_indicator(mood, size=20, animation_class=""):
    """Renders a morphable mood indicator with enhanced animations."""
    mood_colors = {
        "happy": "#FFD700",  # Gold
        "sad": "#4682B4",    # Steel Blue
        "angry": "#FF4500",  # Orange Red
        "neutral": "#808080", # Gray
        "excited": "#FF69B4", # Hot Pink
        "calm": "#98FB98",   # Pale Green
        "anxious": "#DDA0DD", # Plum
        "confident": "#FFA500", # Orange
        "curious": "#20B2AA",  # Light Sea Green
        "playful": "#FFB6C1",  # Light Pink
        "thoughtful": "#B0C4DE", # Light Steel Blue
        "energetic": "#FFD700",  # Gold
        "focused": "#4B0082",    # Indigo
        "creative": "#FF69B4",   # Hot Pink
        "determined": "#FF4500", # Orange Red
        "default": "#808080"     # Gray
    }
    
    color = mood_colors.get(mood.lower(), mood_colors["default"])
    
    st.markdown(f"""
        <style>
        .mood-indicator {{
            width: {size}px;
            height: {size}px;
            background: {color};
            border-radius: 50%;
            display: inline-block;
            position: relative;
            transition: all 0.3s ease;
            cursor: pointer;
            box-shadow: 0 0 10px {color}40;
        }}
        
        .mood-indicator:hover {{
            transform: scale(1.2);
            box-shadow: 0 0 20px {color}80;
        }}
        
        .mood-indicator::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border-radius: inherit;
            background: radial-gradient(circle at 30% 30%, rgba(255,255,255,0.8), transparent);
            opacity: 0.5;
            transition: opacity 0.3s ease;
        }}
        
        .mood-indicator:hover::before {{
            opacity: 0.8;
        }}
        
        .mood-indicator::after {{
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 60%;
            height: 60%;
            border-radius: inherit;
            background: radial-gradient(circle at center, transparent, {color}40);
            animation: pulse 2s infinite;
        }}
        
        .mood-indicator:hover::after {{
            animation: pulse 1s infinite;
        }}
        
        .mood-indicator.mood-changed {{
            animation: moodChange 1s ease-in-out;
        }}
        
        @keyframes pulse {{
            0% {{ transform: translate(-50%, -50%) scale(1); opacity: 0.5; }}
            50% {{ transform: translate(-50%, -50%) scale(1.2); opacity: 0.3; }}
            100% {{ transform: translate(-50%, -50%) scale(1); opacity: 0.5; }}
        }}
        
        @keyframes moodChange {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.5); }}
            100% {{ transform: scale(1); }}
        }}
        
        .mood-tooltip {{
            position: absolute;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 12px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.3s ease;
            z-index: 1000;
        }}
        
        .mood-indicator:hover + .mood-tooltip {{
            opacity: 1;
        }}
        </style>
        <div class="mood-indicator {animation_class}" title="{mood.title()}"></div>
        <div class="mood-tooltip">{mood.title()}</div>
    """, unsafe_allow_html=True)
