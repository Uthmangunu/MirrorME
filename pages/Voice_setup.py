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
st.set_page_config(page_title="MirrorMe - Voice Setup", page_icon="🎙️", layout="wide")

# Add custom CSS
st.markdown("""
<style>
.recording-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    background: linear-gradient(145deg, #ffffff, #f0f0f0);
    border-radius: 20px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin: 2rem auto;
    max-width: 600px;
}

.recording-button {
    font-size: 80px;
    text-align: center;
    padding: 30px;
    border-radius: 100%;
    background-color: #FF4B4B;
    color: white;
    cursor: pointer;
    transition: all 0.3s ease;
    margin: 1rem 0;
}

.recording-button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 20px rgba(255, 75, 75, 0.3);
}

.recording-button.recording {
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(255,75,75, 0.7); }
    70% { box-shadow: 0 0 0 30px rgba(255,75,75, 0); }
    100% { box-shadow: 0 0 0 0 rgba(255,75,75, 0); }
}

.timer {
    font-size: 2rem;
    font-weight: bold;
    color: #FF4B4B;
    margin: 1rem 0;
    font-family: 'Helvetica Neue', sans-serif;
}

.recording-text {
    font-size: 1.2rem;
    color: #666;
    margin: 0.5rem 0;
    font-family: 'Helvetica Neue', sans-serif;
}

.waveform-container {
    width: 100%;
    height: 100px;
    margin: 1rem 0;
    background: rgba(255, 75, 75, 0.1);
    border-radius: 10px;
    overflow: hidden;
}

.tab-content {
    padding: 2rem;
    background: white;
    border-radius: 20px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin: 1rem 0;
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

# === Auto Preview: Generate & Play Voice ===
st.title("🎙️ Mirror Voice Setup")
st.markdown("Record your voice directly here or upload a sample to create your Mirror's voice.")

# Check for existing voice ID
if st.session_state.voice_id:
    st.success("✅ You already have a voice profile set up!")

# === Create tabs for recording and uploading ===
tab1, tab2 = st.tabs(["🎙️ Record", "📁 Upload"])

with tab1:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    
    # Create centered recording container
    st.markdown('<div class="recording-container">', unsafe_allow_html=True)
    
    # Title and instructions
    st.markdown("### 🎙️ Record Your Voice")
    st.markdown("Speak naturally for 30-60 seconds to create your Mirror voice")
    
    # Recording button and status
    recording_class = "recording-button recording" if st.session_state.is_recording else "recording-button"
    st.markdown(f'<div class="{recording_class}">🎙️</div>', unsafe_allow_html=True)
    
    # Timer display
    if st.session_state.is_recording:
        elapsed_time = time.time() - st.session_state.recording_start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        st.markdown(f'<div class="timer">{minutes:02d}:{seconds:02d}</div>', unsafe_allow_html=True)
        st.markdown('<div class="recording-text">Recording in progress...</div>', unsafe_allow_html=True)
    
    # Waveform visualization
    if st.session_state.is_recording and st.session_state.audio_levels:
        st.markdown('<div class="waveform-container">', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            y=st.session_state.audio_levels[-50:],
            mode='lines',
            line=dict(color='#ff4b4b', width=2),
            fill='tozeroy',
            fillcolor='rgba(255, 75, 75, 0.2)'
        ))
        fig.update_layout(
            height=100,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, showticklabels=False, range=[0, 1])
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # WebRTC recorder (hidden)
    rec = webrtc_streamer(
        key="voice_recorder",
        mode=WebRtcMode.SENDONLY,
        audio_receiver_size=1024,
        media_stream_constraints={"audio": True, "video": False},
        async_processing=True
    )
    
    # Handle recording state
    if rec.state.playing and not st.session_state.is_recording:
        st.session_state.is_recording = True
        st.session_state.recording_start_time = time.time()
        st.session_state.audio_levels = []
        st.session_state.audio_data = []
    elif not rec.state.playing and st.session_state.is_recording:
        st.session_state.is_recording = False
        st.session_state.recording_start_time = None
        st.session_state.show_preview = True
    
    # Update audio levels and collect data
    if rec.audio_receiver and st.session_state.is_recording:
        try:
            frame = rec.audio_receiver.get_frames(timeout=0.1)[0]
            audio_data = frame.to_ndarray()
            level = np.abs(audio_data).mean()
            st.session_state.audio_levels.append(level)
            st.session_state.audio_data.extend(audio_data.flatten())
        except:
            pass
    
    # Close recording container
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Preview section
    if st.session_state.show_preview and st.session_state.audio_data:
        st.markdown("### 🎵 Preview Recording")
        
        # Convert audio data to WAV format
        audio_data = np.array(st.session_state.audio_data)
        sample_rate = 48000
        
        # Create a temporary WAV file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            wavfile.write(temp_file.name, sample_rate, audio_data)
            
            # Display audio player
            st.audio(temp_file.name)
            
            # Add buttons for actions
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Use This Recording"):
                    st.session_state.recording_path = temp_file.name
                    st.success("Recording saved! You can now proceed with voice setup.")
            with col2:
                if st.button("🔄 Record Again"):
                    st.session_state.show_preview = False
                    st.session_state.audio_data = []
                    st.session_state.audio_levels = []
                    st.experimental_rerun()
    
    # Close tab content
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.subheader("📁 Upload Voice Sample")
    uploaded_file = st.file_uploader("Upload a voice sample (MP3 or WAV)", type=["mp3", "wav"])
    
    if uploaded_file:
        with st.spinner("Processing audio file..."):
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_file_path = tmp_file.name
            
            # Show file info
            st.markdown("### 📊 File Information")
            st.markdown(f"- File Name: {uploaded_file.name}")
            st.markdown(f"- File Size: {uploaded_file.size / 1024:.1f} KB")
            st.markdown(f"- File Type: {uploaded_file.type}")
            
            # Preview uploaded file
            st.markdown("### 🎵 Preview Your Audio")
            st.audio(tmp_file_path)
            
            if st.button("🚀 Upload to ElevenLabs"):
                with st.spinner("Processing your voice sample..."):
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
