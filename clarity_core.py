import json
from datetime import datetime

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

# Load clarity data
def load_clarity():
    with open(CLARITY_DATA_PATH, "r") as f:
        return json.load(f)

# Save clarity data
def save_clarity(data):
    with open(CLARITY_DATA_PATH, "w") as f:
        json.dump(data, f, indent=4)

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

# Example usage (you can import and call this in Streamlit or any backend)
if __name__ == "__main__":
    clarity = load_clarity()
    clarity = apply_trait_xp(clarity, "journal")  # e.g., user uploads journal
    save_clarity(clarity)
    print(f"Updated clarity level: {clarity['clarity_level']}")
