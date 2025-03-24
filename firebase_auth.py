import pyrebase
import streamlit as st

# === 🔐 Firebase Config from secrets.toml ===
firebase_config = {
    "apiKey": st.secrets["FIREBASE_API_KEY"],
    "authDomain": st.secrets["FIREBASE_AUTH_DOMAIN"],
    "projectId": st.secrets["FIREBASE_PROJECT_ID"],
    "storageBucket": st.secrets["FIREBASE_STORAGE_BUCKET"],
    "messagingSenderId": st.secrets["FIREBASE_MESSAGING_SENDER_ID"],
    "appId": st.secrets["FIREBASE_APP_ID"],
    "measurementId": st.secrets["FIREBASE_MEASUREMENT_ID"]
}

# === 🔧 Initialize Firebase ===
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

# === 🔐 Sign Up ===
def signup(email, password):
    try:
        user = auth.create_user_with_email_and_password(email, password)
        return user
    except Exception as e:
        st.error(f"Signup failed: {e}")
        return None

# === 🔑 Login ===
def login(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return user
    except Exception as e:
        st.error(f"Login failed: {e}")
        return None
