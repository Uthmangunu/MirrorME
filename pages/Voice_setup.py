import streamlit as st
import requests
import os
from google.cloud import firestore
from dotenv import load_dotenv
import tempfile
import time
from components.feedback_button import feedback_button
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import soundfile as sf
from io import BytesIO
import numpy as np
from firebase_client import get_doc, save_doc
import plotly.graph_objects as go
from scipy.io import wavfile

# === Page Config ===
st.set_page_config(page_title="MirrorMe - Voice Setup", page_icon="🎙️", layout="centered")

# Add minimal CSS
st.markdown("""
<style>
.main {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
}

.recording-container {
    background: white;
    padding: 2rem;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin: 1rem 0;
}

.timer {
    font-size: 2rem;
    font-weight: bold;
    color: #FF4B4B;
    text-align: center;
    margin: 1rem 0;
}

.waveform {
    height: 60px;
    background: #f5f5f5;
    border-radius: 5px;
    margin: 1rem 0;
    overflow: hidden;
}

.stButton>button {
    width: 100%;
    margin: 0.5rem 0;
    border-radius: 5px;
}

/* Hide WebRTC elements */
.stWebRtc {
    display: none !important;
}

.preview-container {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 5px;
    margin: 1rem 0;
}

.recording-status {
    text-align: center;
    color: #FF4B4B;
    font-weight: bold;
    margin: 0.5rem 0;
}

.recording-timer {
    font-size: 2rem;
    font-weight: bold;
    color: #FF4B4B;
    text-align: center;
    margin: 1rem 0;
    font-family: monospace;
}

.waveform-container {
    height: 60px;
    background: #f5f5f5;
    border-radius: 5px;
    margin: 1rem 0;
    overflow: hidden;
    position: relative;
}
</style>
""", unsafe_allow_html=True)

# === 🔐 Require Login ===
if "user" not in st.session_state:
    st.session_state.user = None

if "voice_id" not in st.session_state:
    st.session_state.voice_id = None

if "recording_path" not in st.session_state:
    st.session_state.recording_path = None

if "recording_start_time" not in st.session_state:
    st.session_state.recording_start_time = None

if "is_recording" not in st.session_state:
    st.session_state.is_recording = False

if "audio_levels" not in st.session_state:
    st.session_state.audio_levels = []

if "audio_data" not in st.session_state:
    st.session_state.audio_data = []

if "show_preview" not in st.session_state:
    st.session_state.show_preview = False

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

# === Main UI ===
st.title("Voice Setup")

# Check for existing voice ID
if st.session_state.voice_id:
    st.success("✅ Voice profile already set up")
    if st.button("🔊 Test Voice"):
        audio = generate_voice_response(
            "Hey, it's your Mirror. I'm excited to be speaking with you in your own voice!",
            st.session_state.voice_id
        )
        if audio:
            st.audio(audio, format="audio/mp3")
    st.stop()

# === Recording Interface ===
st.markdown('<div class="recording-container">', unsafe_allow_html=True)

# Recording controls
if not st.session_state.is_recording:
    if st.button("🎙️ Start Recording"):
        st.session_state.is_recording = True
        st.session_state.recording_start_time = time.time()
        st.session_state.audio_levels = []
        st.session_state.audio_data = []
else:
    if st.button("⏹️ Stop Recording"):
        st.session_state.is_recording = False
        st.session_state.recording_start_time = None
        
        # Calculate actual recording duration
        sample_rate = 48000
        duration = len(st.session_state.audio_data) / sample_rate
        
        # Debug info
        st.info(f"🧪 Recorded {len(st.session_state.audio_data)} samples (~{duration:.2f} sec)")
        
        # Validate recording length
        if duration < 2.5:
            st.error(f"Recording too short ({duration:.2f} sec). Please speak for at least 3 seconds.")
            st.session_state.show_preview = False
        else:
            st.session_state.show_preview = True
            
            # Process recorded audio
            audio_data = np.array(st.session_state.audio_data)
            
            # Create a temporary WAV file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                wavfile.write(temp_file.name, sample_rate, audio_data)
                st.session_state.recording_path = temp_file.name

# Timer display
if st.session_state.is_recording:
    elapsed_time = int(time.time() - st.session_state.recording_start_time)
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60
    st.markdown(f'<div class="recording-timer">{minutes:02d}:{seconds:02d}</div>', unsafe_allow_html=True)
    st.markdown('<div class="recording-status">Recording in progress...</div>', unsafe_allow_html=True)

# WebRTC recorder (hidden)
with st.container():
    rec = webrtc_streamer(
        key="voice_recorder",
        mode=WebRtcMode.SENDONLY,
        audio_receiver_size=1024,
        media_stream_constraints={"audio": True, "video": False},
        async_processing=True
    )

# Real-time waveform update
if rec.audio_receiver and st.session_state.is_recording:
    waveform_container = st.empty()
    
    while st.session_state.is_recording:
        try:
            frame = rec.audio_receiver.get_frames(timeout=0.1)[0]
            audio_data = frame.to_ndarray()
            level = np.abs(audio_data).mean()
            st.session_state.audio_levels.append(level)
            st.session_state.audio_data.extend(audio_data.flatten())

            # Only update waveform if we have enough data
            if len(st.session_state.audio_levels) >= 50:
                # Live waveform display
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    y=st.session_state.audio_levels[-50:],
                    mode='lines',
                    line=dict(color='#ff4b4b', width=2),
                    fill='tozeroy',
                    fillcolor='rgba(255, 75, 75, 0.2)'
                ))
                fig.update_layout(
                    height=60,
                    margin=dict(l=0, r=0, t=0, b=0),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    showlegend=False,
                    xaxis=dict(showgrid=False, showticklabels=False),
                    yaxis=dict(showgrid=False, showticklabels=False, range=[0, 1])
                )
                waveform_container.plotly_chart(fig, use_container_width=True)

            time.sleep(0.1)  # Reduced update frequency for better performance
        except:
            continue

st.markdown('</div>', unsafe_allow_html=True)

# Preview section
if st.session_state.show_preview and st.session_state.recording_path:
    st.markdown('<div class="preview-container">', unsafe_allow_html=True)
    st.markdown("### Preview Recording")
    
    # Display audio player
    st.audio(st.session_state.recording_path)
    
    # Add buttons for actions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Use This Recording"):
            with st.spinner("🧬 Sending to ElevenLabs and cloning your voice..."):
                voice_id = create_voice_in_elevenlabs(user_id, st.session_state.recording_path)
                
                if voice_id:
                    if save_voice_id_to_firestore(user_id, voice_id):
                        st.session_state.voice_id = voice_id
                        st.success("✅ Voice profile created!")
                        
                        # Play test audio
                        test_audio = generate_voice_response(
                            "Hey, it's your Mirror. I'm excited to be speaking with you in your own voice!",
                            voice_id
                        )
                        if test_audio:
                            st.audio(test_audio, format="audio/mp3")
                    else:
                        st.error("Failed to save voice ID")
                else:
                    st.error("Failed to create voice profile")
                
                # Clean up
                os.unlink(st.session_state.recording_path)
                st.session_state.show_preview = False
                st.session_state.recording_path = None
                st.session_state.audio_data = []
                st.session_state.audio_levels = []
    
    with col2:
        if st.button("🔄 Record Again"):
            st.session_state.show_preview = False
            st.session_state.recording_path = None
            st.session_state.audio_data = []
            st.session_state.audio_levels = []
    
    st.markdown('</div>', unsafe_allow_html=True)

# === Helpful tips ===
st.markdown("""
### Tips
- Record in a quiet environment
- Speak naturally for 30-60 seconds
- Avoid background noise
""")

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
        "xi-api-key": ELEVEN_API_KEY
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
                voice_id = response.json().get("voice_id")
                if voice_id:
                    st.info(f"🔍 Voice ID: {voice_id}")  # Show voice ID for debugging
                    return voice_id
                else:
                    st.error("No voice ID returned from ElevenLabs API")
                    return None
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
                "created_at": firestore.SERVER_TIMESTAMP,
                "updated_at": firestore.SERVER_TIMESTAMP
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
        "xi-api-key": ELEVEN_API_KEY,
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
