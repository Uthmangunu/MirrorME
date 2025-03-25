
import streamlit as st

st.set_page_config(page_title="MirrorMe", page_icon="🪞", layout="centered")

st.title("🪞 Welcome to MirrorMe")
st.markdown("### Your AI reflection — not your assistant.")

st.markdown(
    '''
    MirrorMe builds a digital version of **you** — trained on your tone, thoughts, and vibe.
    
    - 🎭 Speaks in your style  
    - 🧠 Remembers your beliefs  
    - 🎤 Talks back in your voice  

    Whether you're building a coach, a clone, or a companion — it's time to meet your Mirror.
    '''
)

st.image("https://mirror-me-assets.s3.amazonaws.com/mirror_mockup.gif", use_column_width=True)

st.markdown("---")

st.markdown("### Ready to train your Mirror?")
if st.button("🔐 Login to Begin"):
    st.switch_page("pages/Login.py")  # Match the correct filename path
