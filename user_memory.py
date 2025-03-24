# user_memory.py
from firebase_client import get_doc, save_doc
import openai
from dotenv import load_dotenv
import os
import json

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === 🧠 Memory Logging ===
def update_user_memory(user_id, user_input, assistant_reply):
    doc = get_doc("memories", user_id) or {}
    history = doc.get("history", [])
    history.append({"user": user_input, "assistant": assistant_reply})
    save_doc("memories", user_id, {"history": history})

def get_user_memory_as_string(user_id):
    doc = get_doc("memories", user_id)
    if not doc or "history" not in doc:
        return "No memory yet."
    return "\n".join([f"You: {m['user']}\nMirrorMe: {m['assistant']}" for m in doc["history"][-5:]])

# === 🔍 Memory Summarization ===
def summarize_user_memory(user_id):
    doc = get_doc("memories", user_id)
    if not doc or "history" not in doc:
        return "Nothing to summarize yet."
    history = doc["history"][-10:]
    chat = "\n".join([f"You: {m['user']}\nMirrorMe: {m['assistant']}" for m in history])
    prompt = [
        {"role": "system", "content": "You are a calm, analytical assistant summarizing emotional and behavioral patterns."},
        {"role": "user", "content": f"Summarize this chat history and extract patterns or emotional insights:\n\n{chat}"}
    ]
    try:
        response = client.chat.completions.create(model="gpt-4o", messages=prompt)
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Summary error: {e}"

# === 💡 Trait Management ===
def load_user_clarity(user_id):
    doc = get_doc("clarities", user_id)
    if not doc:
        return {
            "traits": {
                "humor": {"score": 50, "xp": 0},
                "empathy": {"score": 50, "xp": 0},
                "ambition": {"score": 50, "xp": 0},
                "flirtiness": {"score": 50, "xp": 0}
            },
            "clarity_level": 0,
            "total_xp": 0,
            "xp_to_next_level": 100
        }
    return doc

def save_user_clarity(user_id, clarity_data):
    save_doc("clarities", user_id, clarity_data)
