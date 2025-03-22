from elevenlabs import generate, set_api_key

set_api_key("YOUR_API_KEY")  # Replace with your real ElevenLabs API key

audio = generate(
    text="MirrorMe is speaking. If you hear this, everything works.",
    voice="YOUR_VOICE_ID"  # Replace with your real voice ID
)

with open("output.mp3", "wb") as f:
    f.write(audio)
