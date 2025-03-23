import json
import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

MEMORY_FILE = "mirror_memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def auto_summarize(user_input, assistant_reply):
    try:
        summary_prompt = f"""
Summarize the key insight from this exchange in 1 short sentence for long-term memory.
User said: "{user_input}"
Mirror replied: "{assistant_reply}"
Summary:"""

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You're a memory compressor for an AI assistant."},
                {"role": "user", "content": summary_prompt}
            ]
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print("❌ Auto-summarization error:", e)
        return f"User: {user_input} | Mirror: {assistant_reply}"

def update_memory(user_input, assistant_reply):
    memory = load_memory()
    summary = auto_summarize(user_input, assistant_reply)
    memory.append({"summary": summary})
    save_memory(memory)

def get_memory_as_string():
    memory = load_memory()
    return "\n".join([
        f"- 🧍 You: {entry.get('user', '[MISSING]')}\n  🪞 Mirror: {entry.get('mirror', '[MISSING]')}"
        for entry in memory
    ])

