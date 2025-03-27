import streamlit as st
import requests
import os
from google.cloud import firestore
from dotenv import load_dotenv
import tempfile
import time
from components.feedback_button import feedback_button
from streamlit_webrtc import webrtc_streamer
import soundfile as sf
from io import BytesIO
import numpy as np

# === Page Config ===
st.set_page_config(page_title="MirrorMe - Voice Setup", page_icon="🎙️")
st.title("🎙️ Mirror Voice Setup")
st.markdown("Record your voice directly here or upload a sample to create your Mirror's voice.")

# === 🔐 Require Login ===
if "user" not in st.session_state:
    st.session_state.user = None

if "voice_id" not in st.session_state:
    st.session_state.voice_id = None

if "recording_path" not in st.session_state:
    st.session_state.recording_path = None

if not st.session_state.user:
    st.warning("⚠️ Please Log In to Access This Page.")
    if st.button("🔐 Login"):
        st.switch_page("pages/Login.py")
    st.stop()

user_id = st.session_state.user["localId"]

# === Load API Key ===
load_dotenv()
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")

# === Load Current Settings ===
current = get_doc("settings", user_id) or {}
current_id = current.get("voice_id", "21m00Tcm4TlvDq8ikWAM")
current_voice_name = next((k for k, v in preset_voices.items() if v == current_id), None)

# === Predefined Voice Options ===
preset_voices = {
    "Uthman Vibe (Calm + Smooth)": "3Tjd0DlL3tjpqnkvDu9j",
    "Witty Confidant": "EXAVITQu4vr4xnSDxMaL",
    "Playful Narrator": "ErXwobaYiN019PkySvjV",
    "Chill Deep (Default)": "21m00Tcm4TlvDq8ikWAM"
}

# === Load Current Settings ===
current = get_doc("settings", user_id) or {}
current_id = current.get("voice_id", "21m00Tcm4TlvDq8ikWAM")
current_voice_name = next((k for k, v in preset_voices.items() if v == current_id), None)

# === UI: Select Voice Style ===
st.markdown("### 🎙️ Pick a Pre-Trained Voice")
chosen_voice = st.selectbox(
    "Choose a voice style:",
    options=list(preset_voices.keys()),
    index=list(preset_voices.keys()).index(current_voice_name) if current_voice_name else 0
)

selected_voice_id = preset_voices[chosen_voice]

# === Auto Preview: Generate & Play Voice ===
st.markdown("#### 🧪 Hear how your Mirror sounds")
test_phrase = "Hey, I'm your Mirror. Let's see how I sound."

def speak(text, voice_id):
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
        headers = {
            "xi-api-key": ELEVEN_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.9
            }
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            audio_path = f"preview_{voice_id}.mp3"
            with open(audio_path, "wb") as f:
                f.write(response.content)
            st.audio(audio_path, format="audio/mp3")
        else:
            st.error("❌ Failed to fetch voice preview.")
    except Exception as e:
        st.error(f"Error: {e}")

speak(test_phrase, selected_voice_id)

# === Save Selection ===
if st.button("✅ Save Voice Selection"):
    save_doc("settings", user_id, {
        "voice_id": selected_voice_id,
        "enable_voice_response": True
    })
    st.success("✅ Your Mirror voice is set!")

# === Upload Custom Voice ===
st.markdown("### 🧬 Upload Your Own Voice (optional)")
st.caption("_This is just for future cloning, not used yet._")

# Create tabs for recording and uploading
tab1, tab2 = st.tabs(["�� Record Voice", "📁 Upload File"])

with tab1:
    st.subheader("🎤 Record Your Voice")
    st.markdown("Click 'Start' to begin recording. Speak naturally for 30-60 seconds.")
    
    # WebRTC recorder
    rec = webrtc_streamer(
        key="voice_recorder",
        mode="sendonly",
        audio_receiver_size=1024,
        media_stream_constraints={"audio": True, "video": False},
        async_processing=True
    )
    
    # Process recorded audio
    if rec.audio_receiver:
        audio_frames = []
        while True:
            try:
                frame = rec.audio_receiver.get_frames(timeout=1)[0]
                audio_frames.append(frame)
            except:
                break

        if audio_frames:
            # Convert frames to audio data
            pcm_audio = b''.join([f.to_ndarray().tobytes() for f in audio_frames])
            
            # Save as WAV
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                sf.write(tmp_file.name, np.frombuffer(pcm_audio, dtype=np.float32), samplerate=44100)
                st.session_state.recording_path = tmp_file.name
            
            # Play preview
            st.audio(st.session_state.recording_path)
            
            # Upload button
            if st.button("🚀 Upload Recording to ElevenLabs"):
                voice_id = create_voice_in_elevenlabs(user_id, st.session_state.recording_path)
                if voice_id:
                    if save_voice_id_to_firestore(user_id, voice_id):
                        st.session_state.voice_id = voice_id
                        st.success("✅ Voice profile created successfully!")
                        # Clean up temporary file
                        os.unlink(st.session_state.recording_path)
                    else:
                        st.error("Failed to save voice ID to database.")

with tab2:
    st.subheader("📁 Upload Voice Sample")
    uploaded_file = st.file_uploader("Upload a voice sample (MP3 or WAV)", type=["mp3", "wav"])
    
    if uploaded_file:
        with st.spinner("Processing audio file..."):
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_file_path = tmp_file.name
            
            # Preview uploaded file
            st.audio(tmp_file_path)
            
            if st.button("🚀 Upload to ElevenLabs"):
                voice_id = create_voice_in_elevenlabs(user_id, tmp_file_path)
                if voice_id:
                    if save_voice_id_to_firestore(user_id, voice_id):
                        st.session_state.voice_id = voice_id
                        st.success("✅ Voice profile created successfully!")
                    else:
                        st.error("Failed to save voice ID to database.")
                
                # Clean up temporary file
                os.unlink(tmp_file_path)

# === Test voice button ===
if st.session_state.voice_id:
    st.subheader("🔊 Test Your Mirror Voice")
    if st.button("Play Test Message"):
        audio = generate_voice_response(
            "Hey, it's your Mirror. I'm excited to be speaking with you in your own voice!",
            st.session_state.voice_id
        )
        if audio:
            st.audio(audio, format="audio/mp3")

# === Voice settings ===
if st.session_state.voice_id:
    st.subheader("⚙️ Voice Settings")
    use_voice = st.checkbox(
        "Use my voice for Mirror responses",
        value=True,
        help="When enabled, Mirror will speak in your voice. When disabled, it will use the default voice."
    )
    
    # Save voice preference to Firestore
    if use_voice:
        db = get_firestore_client()
        if db:
            ref = db.collection("users").document(user_id).collection("personality").document("voice")
            ref.update({"use_voice": True})

# === Helpful tips ===
st.markdown("""
### 💡 Tips for Best Results
1. Record in a quiet environment
2. Speak naturally and clearly
3. Include a variety of sentences
4. Avoid background noise
5. Keep the recording between 30-60 seconds

Your voice will be used to make Mirror's responses feel more personal and natural.
""")

# === Footer ===
st.markdown("---")
st.caption("This voice will be used every time your Mirror speaks.")
feedback_button(user_id)
st.markdown("### 🪞 Mirror Identity Tagline")
tagline = st.text_input("Describe how your Mirror should behave (tone, attitude, etc.):", max_chars=150)

if tagline:
    st.session_state["mirror_tagline"] = tagline
    st.success("✅ Tagline saved for prompt injection.")
