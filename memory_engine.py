import json
import os
import openai
from dotenv import load_dotenv

load_dotenv()
MEMORY_FILE = "mirror_memory.json"
openai.api_key = os.getenv("OPENAI_API_KEY")


# === Load memory from file ===
def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return []
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []  # fallback if file is corrupted


# === Save memory to file ===
def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


# === Add new interaction ===
def update_memory(user_input, mirror_reply):
    memory = load_memory()
    memory.append({
        "user": user_input.strip(),
        "mirror": mirror_reply.strip()
    })
    save_memory(memory)


# === Display Memory Log in Sidebar ===
def get_memory_as_string():
    memory = load_memory()
    formatted = []

    for i, entry in enumerate(memory, start=1):
        user = entry.get("user")
        mirror = entry.get("mirror")
        if user and mirror:
            formatted.append(f"🧍 You #{i}: {user}\n🪞 Mirror: {mirror}")
    return "\n\n".join(formatted) if formatted else "📭 No memory entries yet."


# === GPT Summary of Last 10 Exchanges ===
def summarize_memory():
    memory = load_memory()
    last_entries = [f"You: {m['user']}\nMirror: {m['mirror']}" for m in memory if "user" in m and "mirror" in m]

    if not last_entries:
        return "📭 No conversations to summarize."

    prompt = (
        "Summarize these conversations into 3–5 high-level insights about the user's mindset, behavior, or interests. "
        "Focus on tone, personality patterns, and repeated themes:\n\n" +
        "\n\n".join(last_entries[-10:])
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You're a psychological profiling assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Summary error: {e}"
