import openai
import requests
import os
from pydub import AudioSegment
from pydub.playback import play

# === 🔐 API KEYS (Insert Your Actual Keys) ===
openai.api_key = "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"  # Your real OpenAI API key here
eleven_api_key = "sk_73e13db9cbf905924180777628650af3774c9cc3aad5df53"      # Your real ElevenLabs API key here
voice_id = "3Tjd0DlL3tjpqnkvDu9j"  # Your ElevenLabs voice ID

# === 📄 Load Your System Prompt ===
with open("uthmanprompt.txt", "r") as f:
    system_prompt = f.read()

# === 🧠 Get GPT-4 Reply (OpenAI v0.28 syntax) ===
def get_gpt_reply(user_input):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("❌ OpenAI Error:", e)
        return "Sorry, I had a glitch. Try again."

# === 🔊 ElevenLabs TTS Playback ===
def speak_with_elevenlabs(text):
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": eleven_api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.99
            }
        }

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            output_file = "uthman_response.mp3"
            with open(output_file, "wb") as f:
                f.write(response.content)
            print(f"🎧 Voice saved as '{output_file}'. Download it and play locally.")
        else:
            print("❌ ElevenLabs Error:", response.text)

    except Exception as e:
        print("❌ ElevenLabs Exception:", e)

# === 💬 Main Chat Loop ===
print("🤖 MirrorMe is ready. Type 'exit' to quit.")
while True:
    user_input = input("You: ")
    if user_input.strip().lower() in ["exit", "quit"]:
        print("👋 Exiting MirrorMe.")
        break
    if not user_input.strip():
        continue
    reply = get_gpt_reply(user_input)
    print("UthmanGPT:", reply)
    speak_with_elevenlabs(reply)
chat_history = [
    {"role": "system", "content": system_prompt}
]

while True:
    user_input = input("You: ")
    if user_input.strip().lower() in ["exit", "quit"]:
        print("👋 Exiting MirrorMe.")
        break
    if not user_input.strip():
        continue

    chat_history.append({"role": "user", "content": user_input})
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=chat_history[-10:]  # only keep last 10 messages
        )
        reply = response.choices[0].message.content.strip()
        print("UthmanGPT:", reply)
        chat_history.append({"role": "assistant", "content": reply})
        speak_with_elevenlabs(reply)

    except Exception as e:
        print("❌ OpenAI Error:", e)
