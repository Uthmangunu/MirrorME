import json
import os
from collections import Counter

MEMORY_FILE = "memory.json"


def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {
        "topics": [],
        "beliefs": [],
        "phrases": [],
        "tone": ""
    }


def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


def update_memory(user_input, mirror_reply):
    memory = load_memory()

    # Extract keywords from user input
    keywords = [w.lower() for w in user_input.split() if len(w) > 4]
    memory["topics"].extend(keywords)

    # Keep only the 10 most common topics
    topic_counter = Counter(memory["topics"])
    memory["topics"] = [t[0] for t in topic_counter.most_common(10)]

    # Extract a phrase from the reply
    if mirror_reply.endswith("?") is False:
        phrase = mirror_reply.split(".")[0].strip()
        if phrase and phrase not in memory["phrases"]:
            memory["phrases"].append(phrase)
            memory["phrases"] = memory["phrases"][-5:]  # last 5 phrases only

    # Example tone tuning based on message style (primitive for now)
    if "hmm" in mirror_reply.lower() or "let me think" in mirror_reply.lower():
        memory["tone"] = "reflective"
    elif "bro" in mirror_reply.lower() or "nah" in mirror_reply.lower():
        memory["tone"] = "casual"

    save_memory(memory)
    return memory
