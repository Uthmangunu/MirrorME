import json
from datetime import datetime
import openai
import os
from dotenv import load_dotenv

CLARITY_DATA_PATH = "clarity_data.json"

# XP thresholds for each clarity level
XP_THRESHOLDS = {
    0: 0,
    1: 100,
    2: 200,
    3: 400,
    4: 700,
    5: 1100
}

# Trait impact map for different input types
TRAIT_XP_BIAS = {
    "journal": {"empathy": 40, "memory": 20},
    "dm": {"humor": 20, "memory": 20},
    "rant": {"boldness": 30, "logic": 30},
    "philosophy": {"logic": 50},
    "flirt": {"humor": 25, "boldness": 25},
    "tag_feedback": {"memory": 10},
    "rate_reply": {"memory": 10},
}

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load clarity data
def load_clarity():
    """Load clarity data with error handling."""
    try:
        if not os.path.exists(CLARITY_DATA_PATH):
            # Initialize default clarity data if file doesn't exist
            default_data = {
                "total_xp": 0,
                "clarity_level": 0,
                "xp_to_next_level": XP_THRESHOLDS[1],
                "evolution": {
                    "level_history": {},
                    "last_updated": datetime.utcnow().isoformat()
                },
                "traits": {
                    trait: {"xp": 0, "score": 50} 
                    for trait in ["humor", "empathy", "logic", "boldness", "memory", "depth", "adaptability", "ambition", "flirtiness"]
                }
            }
            save_clarity(default_data)
            return default_data
            
        with open(CLARITY_DATA_PATH, "r") as f:
            data = json.load(f)
            
            # Ensure all required fields exist
            if "traits" not in data:
                data["traits"] = {}
                
            # Ensure all required traits exist with default values
            required_traits = ["humor", "empathy", "logic", "boldness", "memory", "depth", "adaptability", "ambition", "flirtiness"]
            for trait in required_traits:
                if trait not in data["traits"]:
                    data["traits"][trait] = {"xp": 0, "score": 50}
                    
            # Ensure other required fields exist
            if "total_xp" not in data:
                data["total_xp"] = 0
            if "clarity_level" not in data:
                data["clarity_level"] = 0
            if "xp_to_next_level" not in data:
                data["xp_to_next_level"] = XP_THRESHOLDS[1]
            if "evolution" not in data:
                data["evolution"] = {
                    "level_history": {},
                    "last_updated": datetime.utcnow().isoformat()
                }
                
            return data
    except Exception as e:
        print(f"Error loading clarity data: {e}")
        return None

# Save clarity data
def save_clarity(data):
    """Save clarity data with error handling."""
    try:
        with open(CLARITY_DATA_PATH, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving clarity data: {e}")
        raise

# Add XP and level up if threshold is crossed
def apply_xp_gain(data, xp_gain):
    data["total_xp"] += xp_gain

    current_level = data["clarity_level"]
    while current_level < 5 and data["total_xp"] >= XP_THRESHOLDS[current_level + 1]:
        current_level += 1
        data["clarity_level"] = current_level
        data["xp_to_next_level"] = XP_THRESHOLDS.get(current_level + 1, 0)
        now = datetime.utcnow().isoformat()
        data["evolution"]["level_history"][str(current_level)] = now
        data["evolution"]["last_updated"] = now

    return data

# Add XP to specific traits based on input type
def apply_trait_xp(data, input_type):
    if input_type not in TRAIT_XP_BIAS:
        return data  # No trait match for this input type

    trait_map = TRAIT_XP_BIAS[input_type]
    total_xp = 0

    for trait, xp in trait_map.items():
        if trait in data["traits"]:
            data["traits"][trait]["xp"] += xp
            # Optional: boost score based on XP if you want
            data["traits"][trait]["score"] += xp * 0.1
            data["traits"][trait]["score"] = min(data["traits"][trait]["score"], 100)
            total_xp += xp

    return apply_xp_gain(data, total_xp)

def extract_values_from_text(text: str) -> dict:
    """
    Extract core values and beliefs from user text using GPT.
    Returns a dictionary of boolean values indicating presence of different values.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """
                Extract core values and beliefs from the user's text.
                Return a JSON object with boolean values for these keys:
                - honesty
                - freedom
                - social_approval
                - ambition
                - creativity
                - tradition
                - innovation
                - spirituality
                - materialism
                - altruism
                - individualism
                - collectivism
                - stability
                - adventure
                - knowledge
                - power
                - pleasure
                - duty
                - justice
                - beauty
                
                Example: "I value honesty and freedom, but don't care about social approval"
                Returns: {"honesty": true, "freedom": true, "social_approval": false, ...}
                """},
                {"role": "user", "content": text}
            ],
            temperature=0.3
        )
        
        # Parse the response and return as dictionary
        values = eval(response.choices[0].message.content)
        return values
    except Exception as e:
        print(f"Error extracting values: {e}")
        return {}

def detect_mood_from_text(text: str) -> str:
    """
    Detect the user's mood from their text using GPT.
    Returns one of: calm, sad, excited, angry, playful, thoughtful, neutral
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """
                Detect the user's mood from their text.
                Return exactly one of these moods:
                - calm
                - sad
                - excited
                - angry
                - playful
                - thoughtful
                - neutral
                
                Example: "I'm so happy about my new job!"
                Returns: "excited"
                """},
                {"role": "user", "content": text}
            ],
            temperature=0.3
        )
        
        mood = response.choices[0].message.content.strip().lower()
        return mood if mood in ["calm", "sad", "excited", "angry", "playful", "thoughtful", "neutral"] else "neutral"
    except Exception as e:
        print(f"Error detecting mood: {e}")
        return "neutral"

def analyze_feedback(feedback_text: str) -> dict:
    """
    Analyze user feedback to determine which traits should receive XP.
    Returns a dictionary of traits and their XP gains.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """
                Analyze the user's feedback and determine which traits should receive XP.
                Return a JSON object with trait names as keys and XP amounts as values.
                Consider these traits:
                - humor
                - empathy
                - logic
                - boldness
                - memory
                - depth
                - adaptability
                
                Example: "The Mirror was really funny and understood my feelings well"
                Returns: {"humor": 2, "empathy": 2}
                """},
                {"role": "user", "content": feedback_text}
            ],
            temperature=0.3
        )
        
        return eval(response.choices[0].message.content)
    except Exception as e:
        print(f"Error analyzing feedback: {e}")
        return {}

def apply_trait_xp(trait: str, amount: int = 1) -> None:
    """
    Apply experience points to a trait, potentially leveling it up.
    """
    try:
        # Load current clarity data
        clarity = load_clarity()
        if not clarity:
            print("Failed to load clarity data")
            return
        
        # Apply XP to trait
        if trait in clarity["traits"]:
            clarity["traits"][trait]["xp"] += amount
            # Update trait score based on XP
            clarity["traits"][trait]["score"] = min(
                clarity["traits"][trait]["score"] + (amount * 0.1),
                100
            )
            
            # Save updated data
            save_clarity(clarity)
        else:
            print(f"Trait {trait} not found in clarity data")
    except Exception as e:
        print(f"Error applying trait XP: {e}")

# Example usage (you can import and call this in Streamlit or any backend)
if __name__ == "__main__":
    clarity = load_clarity()
    clarity = apply_trait_xp(clarity, "journal")  # e.g., user uploads journal
    save_clarity(clarity)
    print(f"Updated clarity level: {clarity['clarity_level']}")
