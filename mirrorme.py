import openai
import requests
import os
from pydub import AudioSegment
from pydub.playback import play

# 🔐 API Keys
openai.api_key = os.getenv("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")
eleven_api_key = os.getenv("sk_73e13db9cbf905924180777628650af3774c9cc3aad5df53")
voice_id = ("3Tjd0DlL3tjpqnkvDu9j")

# 📄 Load System Prompt
with open("uthman_prompt.txt", "r") as f:
    system_prompt = f.read()

# 🧠 Get GPT Response
def get_gpt_reply(user_input):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("❌ OpenAI Error:", e)
        return "Sorry, I had a glitch. Try again."

# 🔊 Speak with ElevenLabs
def speak_with_elevenlabs(text):
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
            "similarity_boost": 0.75
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            with open("response.mp3", "wb") as f:
                f.write(response.content)
            audio = AudioSegment.from_file("response.mp3", format="mp3")
            print("🔊 Speaking...")
            play(audio)
            os.remove("response.mp3")
        else:
            print("❌ ElevenLabs Error:", response.text)
    except Exception as e:
        print("❌ ElevenLabs Exception:", e)

# 💬 Main Loop
print("🤖 MirrorMe is ready. Type 'exit' to quit.")
while True:
    user_input = input("You: ")
    if user_input.lower() in ["quit", "exit"]:
        print("👋 Exiting MirrorMe.")
        break
    reply = get_gpt_reply(user_input)
    print("UthmanGPT:", reply)
    speak_with_elevenlabs(reply)

