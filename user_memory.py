# user_memory.py
import os
import json
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# === File Path Helpers ===
def user_folder(user_id):
    path = f"user_data/{user_id}"
    os.makedirs(path, exist_ok=True)
    return path

def memory_path(user_id):
    return os.path.join(user_folder(user_id), "memory.json")

def clarity_path(user_id):
    return os.path.join(user_folder(user_id), "clarity.json")

# === 🧠 Memory Logging ===
def update_user_memory(user_id, user_input, assistant_reply):
    path = memory_path(user_id)
    if os.path.exists(path):
        with open(path, "r") as f:
            memory = json.load(f)
    else:
        memory = []

    memory.append({
        "user": user_input,
        "assistant": assistant_reply
    })

    with open(path, "w") as f:
        json.dump(memory, f, indent=2)

def get_user_memory_as_string(user_id):
    path = memory_path(user_id)
    if not os.path.exists(path):
        return "No memory yet."
    with open(path, "r") as f:
        memory = json.load(f)
    return "\n".join([f"You: {m['user']}\nMirrorMe: {m['assistant']}" for m in memory[-5:]])

# === 🔍 Memory Summarization ===
def summarize_user_memory(user_id):
    path = memory_path(user_id)
    if not os.path.exists(path):
        return "Nothing to summarize yet."
    with open(path, "r") as f:
        memory = json.load(f)

    history = "\n".join([f"You: {m['user']}\nMirrorMe: {m['assistant']}" for m in memory[-10:]])
    prompt = [
        {"role": "system", "content": "You are a calm, analytical assistant summarizing emotional and behavioral patterns."},
        {"role": "user", "content": f"Summarize this chat history and extract patterns or emotional insights:\n\n{history}"}
    ]

    try:
        response = openai.ChatCompletion.create(model="gpt-4o", messages=prompt)
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Summary error: {e}"

# === 💡 Trait Management ===
def load_user_clarity(user_id):
    path = clarity_path(user_id)
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            pass  # fallback below
    return {
        "humor": 5,
        "empathy": 5,
        "ambition": 5,
        "flirtiness": 5
    }

def save_user_clarity(user_id, clarity_data):
    path = clarity_path(user_id)
    with open(path, "w") as f:
        json.dump(clarity_data, f, indent=2)
