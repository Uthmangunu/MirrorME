import streamlit as st

def topbar(username=None):
    """Create a top navigation bar with links to main sections."""
    st.markdown("""
    <style>
    .navbar {
        background-color: white;
        padding: 0.5rem 1rem;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 1000;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .nav-links {
        display: flex;
        gap: 1.5rem;
        align-items: center;
    }
    
    .nav-links a {
        color: #333;
        text-decoration: none;
        font-weight: 500;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        transition: all 0.2s ease;
    }
    
    .nav-links a:hover {
        background-color: #f0f0f0;
        color: #FF4B4B;
    }
    
    .user-section {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .user-section span {
        color: #666;
        font-size: 0.9rem;
    }
    
    /* Add padding to main content to account for fixed navbar */
    .main {
        padding-top: 4rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="navbar">
        <div class="nav-links">
            <a href="/Clarity">🧠 Clarity</a>
            <a href="/Journal">📓 Journal</a>
            <a href="/Voice_setup">🎙️ Voice</a>
            <a href="/Profile">👤 Profile</a>
        </div>
        <div class="user-section">
            <span>👋 {}</span>
        </div>
    </div>
    """.format(username or "Guest"), unsafe_allow_html=True) 