import random
import time
import numpy as np

def post_process_text(text, mood="neutral", traits=None):
    """
    Adjusts text output to sound more natural, conversational, and human.
    Includes filler words, emotional variation, and pacing markers.
    """
    traits = traits or {}

    # Tone-based fillers
    soft_fillers = ["Hmm...", "You know,", "Honestly,", "Well,", "Let me think...", "Right,"]
    excited_fillers = ["Yo!", "Wait—", "Okay so", "You won't believe this—"]
    empathetic_starters = ["That must feel like...", "I totally get that.", "That's heavy."]

    # Inject based on mood
    if mood == "excited":
        text = f"{random.choice(excited_fillers)} {text}"
    elif mood == "sad":
        text = f"{random.choice(soft_fillers)} {text.lower()}"
    elif mood == "empathetic" or traits.get("Empathy", 0) > 70:
        text = f"{random.choice(empathetic_starters)} {text}"
    elif traits.get("Humor", 0) > 70:
        if random.random() > 0.5:
            text = text + " (Don't quote me on that tho 😅)"
    elif traits.get("Boldness", 0) > 70:
        text = "Real talk — " + text

    # Add pacing breaks
    text = text.replace(",", ", ").replace(".", ". ").replace("...", "... ")
    text = text.replace("  ", " ")
    return text

def get_voice_settings(mood):
    """
    Returns voice settings based on mood for ElevenLabs API
    """
    settings = {
        "stability": 0.4,
        "similarity_boost": 0.8
    }
    if mood == "sad":
        settings = {"stability": 0.6, "similarity_boost": 0.6}
    elif mood == "angry":
        settings = {"stability": 0.2, "similarity_boost": 1.0}
    elif mood == "calm":
        settings = {"stability": 0.4, "similarity_boost": 0.8}
    elif mood == "excited":
        settings = {"stability": 0.3, "similarity_boost": 0.9}
    return settings

def add_human_delay():
    """
    Adds a random delay to simulate human thinking time
    """
    time.sleep(np.random.uniform(0.4, 1.3)) 