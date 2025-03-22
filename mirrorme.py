import openai
import requests
from pydub import AudioSegment
from pydub.playback import play

# 🔐 API Keys and Voice ID (Insert Yours Below)
openai.api_key = "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"
eleven_api_key = "sk_7ee42cf8b7b08258d1574786ade96b7a632a79160d8de978"
voice_id = "3Tjd0DlL3tjpqnkvDu9j"  # e.g., "EXAVITQu4vr4xnSDxMaL"

# 📄 Load Your Personality Prompt
with open("uthman_prompt.txt", "r") as f:
    system_prompt = f.read()

# 🧠 Get GPT-4 Response
def get_gpt_reply(user_input):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content.strip()

# 🔊 Convert GPT Reply to Voice with ElevenLabs
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

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        with open("response.mp3", "wb") as f:
            f.write(response.content)
        audio = AudioSegment.from_file("response.mp3", format="mp3")
        play(audio)
    else:
        print("❌ ElevenLabs Error:", response.text)

# 💬 Main Interaction Loop
while True:
    user_input = input("You: ")
    if user_input.lower() in ["quit", "exit"]:
        print("👋 Exiting MirrorMe.")
        break

    reply = get_gpt_reply(user_input)
    print("UthmanGPT:", reply)
    speak_with_elevenlabs(reply)
