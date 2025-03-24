from firebase_client import get_doc, save_doc

# === 🧠 Memory Logging ===
def update_user_memory(user_id, user_input, assistant_reply):
    memory = get_doc("memories", user_id).get("entries", [])
    memory.append({"user": user_input, "assistant": assistant_reply})
    save_doc("memories", user_id, {"entries": memory})

def get_user_memory_as_string(user_id):
    memory = get_doc("memories", user_id).get("entries", [])
    if not memory:
        return "No memory yet."
    return "\n".join([f"You: {m['user']}\nMirrorMe: {m['assistant']}" for m in memory[-5:]])

# === 🔍 Memory Summarization ===
import openai
from dotenv import load_dotenv
load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize_user_memory(user_id):
    memory = get_doc("memories", user_id).get("entries", [])
    if not memory:
        return "Nothing to summarize yet."
    history = "\n".join([f"You: {m['user']}\nMirrorMe: {m['assistant']}" for m in memory[-10:]])
    prompt = [
        {"role": "system", "content": "You are a calm, analytical assistant summarizing emotional and behavioral patterns."},
        {"role": "user", "content": f"Summarize this chat history and extract patterns or emotional insights:\n\n{history}"}
    ]
    try:
        response = client.chat.completions.create(model="gpt-4o", messages=prompt)
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Summary error: {e}"

# === 💡 Trait Management ===
def load_user_clarity(user_id):
    return get_doc("clarities", user_id)

def save_user_clarity(user_id, clarity_data):
    save_doc("clarities", user_id, clarity_data)
