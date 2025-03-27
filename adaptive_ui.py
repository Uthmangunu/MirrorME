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
def set_mood_background(mood):
    """Set the background color based on the current mood."""
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
        .stApp {{
            background-color: #0e1117;
            color: white;
        }}
        .stButton>button {{
            background-color: {color}40;
            color: white;
            border: 1px solid {color}80;
        }}
        .stButton>button:hover {{
            background-color: {color}60;
        }}
        .stTextInput>div>div>input {{
            background-color: #1a1d23;
            color: white;
            border: 1px solid {color}40;
        }}
        .stSelectbox>div>div>select {{
            background-color: #1a1d23;
            color: white;
            border: 1px solid {color}40;
        }}
        .stTextArea>div>div>textarea {{
            background-color: #1a1d23;
            color: white;
            border: 1px solid {color}40;
        }}
        .stMarkdown {{
            color: white;
        }}
        .message-box {{
            background-color: #1a1d23;
            border: 1px solid {color}40;
            color: white;
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

def create_trait_slider(trait_name, value, key=None):
    """Create a slider for a personality trait with a unique key."""
    if key is None:
        key = f"trait_{trait_name.lower()}"
    
    return st.slider(
        trait_name,
        min_value=0,
        max_value=100,
        value=value,
        key=key,
        help=f"Adjust your Mirror's {trait_name} level"
    )

def create_value_checkbox(label, options, selected_values=None, key=None):
    """Create a multi-select checkbox for values with a unique key."""
    if key is None:
        key = f"values_{label.lower().replace(' ', '_')}"
    if selected_values is None:
        selected_values = []
    
    return st.multiselect(
        label,
        options=options,
        default=selected_values,
        key=key,
        help=f"Select your {label.lower()}"
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

def create_animated_input(mood, size=20, animation_class=""):
    """Creates an animated input box with mood indicator."""
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
        .stChatInputContainer {{
            position: relative;
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        
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
            flex-shrink: 0;
            margin-right: 10px;
            z-index: 1000;
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
            z-index: 1001;
        }}
        
        .mood-indicator:hover + .mood-tooltip {{
            opacity: 1;
        }}
        
        .stTextInput>div>div>input {{
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin: 0 !important;
            background: transparent !important;
        }}
        </style>
        <div class="mood-indicator {animation_class}" title="{mood.title()}"></div>
        <div class="mood-tooltip">{mood.title()}</div>
    """, unsafe_allow_html=True)
