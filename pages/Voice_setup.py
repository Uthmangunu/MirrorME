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
from firebase_client import get_doc, save_doc

# === Page Config ===
st.set_page_config(page_title="MirrorMe - Voice Setup", page_icon="🎙️")

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
st.session_state.voice_id = current.get("voice_id")

# === Auto Preview: Generate & Play Voice ===
st.title("🎙️ Mirror Voice Setup")
st.markdown("Record your voice directly here or upload a sample to create your Mirror's voice.")

# Check for existing voice ID
if st.session_state.voice_id:
    st.success("✅ You already have a voice profile set up!")

# === Create tabs for recording and uploading ===
tab1, tab2 = st.tabs(["🎤 Record Voice", "📁 Upload File"])

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

def get_firestore_client():
    """Initialize and return a Firestore client."""
    try:
        return firestore.Client()
    except Exception as e:
        st.error(f"Failed to initialize Firestore client: {str(e)}")
        return None

def create_voice_in_elevenlabs(user_id, file_path):
    """Create a voice clone in ElevenLabs."""
    url = "https://api.elevenlabs.io/v1/voices/add"
    headers = {
        "xi-api-key": os.getenv("ELEVENLABS_API_KEY")
    }
    
    try:
        with open(file_path, 'rb') as f:
            files = {
                'files': f
            }
            data = {
                "name": f"MirrorVoice_{user_id}",
                "description": "MirrorMe clone voice",
                "labels": {"user_id": user_id}
            }
            response = requests.post(url, headers=headers, files=files, data=data)

            if response.status_code == 200:
                return response.json().get("voice_id")
            else:
                st.error(f"Voice creation failed: {response.text}")
                return None
    except Exception as e:
        st.error(f"Error creating voice: {str(e)}")
        return None

def save_voice_id_to_firestore(user_id, voice_id):
    """Save the voice ID to Firestore."""
    try:
        db = get_firestore_client()
        if db:
            ref = db.collection("users").document(user_id).collection("personality").document("voice")
            ref.set({
                "voice_id": voice_id,
                "created_at": firestore.SERVER_TIMESTAMP
            })
            return True
        return False
    except Exception as e:
        st.error(f"Error saving voice ID: {str(e)}")
        return False

def get_voice_id_from_firestore(user_id):
    """Retrieve the voice ID from Firestore."""
    try:
        db = get_firestore_client()
        if db:
            doc = db.collection("users").document(user_id).collection("personality").document("voice").get()
            if doc.exists:
                return doc.to_dict().get("voice_id")
        return None
    except Exception as e:
        st.error(f"Error retrieving voice ID: {str(e)}")
        return None

def generate_voice_response(text, voice_id):
    """Generate audio from text using ElevenLabs."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": os.getenv("ELEVENLABS_API_KEY"),
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "voice_settings": {
            "stability": 0.4,
            "similarity_boost": 0.8
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.ok:
            return response.content
        else:
            st.error(f"Voice generation failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error generating voice: {str(e)}")
        return None
