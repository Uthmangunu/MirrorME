import streamlit as st
from components.topbar import topbar

# === Page Config ===
st.set_page_config(
    page_title="MirrorMe - Welcome",
    page_icon="🪞",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# === Custom CSS ===
st.markdown("""
<style>
/* Hide sidebar navigation */
[data-testid="stSidebar"] { 
    display: none; 
}

/* Main container */
.main {
    background-color: #0E1117;
    color: white;
}

/* Hero section */
.hero-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 85vh;
    text-align: center;
    padding: 2rem;
    background: linear-gradient(135deg, #1a1d23 0%, #0E1117 100%);
}

.logo {
    font-size: 4rem;
    margin-bottom: 1rem;
    animation: float 3s ease-in-out infinite;
}

.tagline {
    font-size: 2.5rem;
    font-weight: bold;
    color: white;
    margin-bottom: 1rem;
    background: linear-gradient(45deg, #FF4B4B, #FF6B6B);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtagline {
    font-size: 1.2rem;
    color: #a0a0a0;
    margin-bottom: 3rem;
    max-width: 600px;
}

/* Button styling */
.button-container {
    display: flex;
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.stButton>button {
    padding: 0.8rem 2rem;
    font-size: 1.1rem;
    border-radius: 8px;
    transition: all 0.3s ease;
    background: #FF4B4B;
    color: white;
    border: none;
}

.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3);
    background: #e03e3e;
}

/* Features section */
.features {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    padding: 4rem 2rem;
    background: #1a1d23;
}

.feature-card {
    background: rgba(255, 255, 255, 0.05);
    padding: 2rem;
    border-radius: 12px;
    transition: all 0.3s ease;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.feature-card:hover {
    transform: translateY(-5px);
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(255, 75, 75, 0.3);
}

.feature-icon {
    font-size: 2.5rem;
    margin-bottom: 1rem;
}

.feature-title {
    font-size: 1.4rem;
    font-weight: bold;
    color: white;
    margin-bottom: 0.8rem;
}

.feature-description {
    color: #a0a0a0;
    font-size: 1rem;
    line-height: 1.6;
}

/* Animations */
@keyframes float {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
    100% { transform: translateY(0px); }
}

/* Footer */
.footer {
    text-align: center;
    padding: 2rem;
    color: #666;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

# === Hero Section ===
st.markdown('<div class="hero-container">', unsafe_allow_html=True)

# Logo and Tagline
st.markdown('<div class="logo">🪞</div>', unsafe_allow_html=True)
st.markdown('<div class="tagline">Not just an assistant — a reflection.</div>', unsafe_allow_html=True)
st.markdown('<div class="subtagline">Your AI companion that learns, adapts, and mirrors your personality.</div>', unsafe_allow_html=True)

# Action Buttons
st.markdown('<div class="button-container">', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    if st.button("🧠 Start Building Your Mirror", key="start"):
        st.switch_page("pages/Clarity.py")
with col2:
    if st.button("🔐 Login / Register", key="login"):
        st.switch_page("pages/Login.py")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# === Features Section ===
st.markdown('<div class="features">', unsafe_allow_html=True)

# Feature 1
st.markdown("""
<div class="feature-card">
    <div class="feature-icon">🧠</div>
    <div class="feature-title">Personalized AI</div>
    <div class="feature-description">An AI that learns your personality and adapts to your communication style, becoming a true reflection of your cognitive patterns.</div>
</div>
""", unsafe_allow_html=True)

# Feature 2
st.markdown("""
<div class="feature-card">
    <div class="feature-icon">🎙️</div>
    <div class="feature-title">Voice Cloning</div>
    <div class="feature-description">Hear your Mirror speak in your own voice, making interactions feel natural and deeply personal.</div>
</div>
""", unsafe_allow_html=True)

# Feature 3
st.markdown("""
<div class="feature-card">
    <div class="feature-icon">📓</div>
    <div class="feature-title">Personal Journal</div>
    <div class="feature-description">Track your thoughts and emotions with an AI that understands your context and helps you reflect.</div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# === Footer ===
st.markdown('<div class="footer">', unsafe_allow_html=True)
st.caption("⚠️ MirrorMe reflects more than just your words. Emotional stability not included.")
st.markdown('</div>', unsafe_allow_html=True) 