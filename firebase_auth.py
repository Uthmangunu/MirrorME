import pyrebase
import streamlit as st

# === 🔐 Firebase Config from Streamlit Secrets ===
firebase_config = {
    "apiKey": st.secrets["FIREBASE_API_KEY"],
    "authDomain": st.secrets["FIREBASE_AUTH_DOMAIN"],
    "projectId": st.secrets["FIREBASE_PROJECT_ID"],
    "storageBucket": st.secrets["FIREBASE_STORAGE_BUCKET"],
    "messagingSenderId": st.secrets["FIREBASE_MESSAGING_SENDER_ID"],
    "appId": st.secrets["FIREBASE_APP_ID"],
    "measurementId": st.secrets["FIREBASE_MEASUREMENT_ID"],
    "databaseURL": ""  # Optional, can be left empty for auth-only apps
}

# === 🔧 Initialize Firebase ===
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()


# === 🔑 Login User ===
def login(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return user
    except Exception as e:
        error_msg = extract_firebase_error(e)
        st.error(f"Login failed: {error_msg}")
        return None


# === 🆕 Register New User ===
def signup(email, password):
    try:
        user = auth.create_user_with_email_and_password(email, password)
        return user
    except Exception as e:
        error_msg = extract_firebase_error(e)
        st.error(f"Signup failed: {error_msg}")
        return None


# === 🧠 Error Extraction Helper ===
def extract_firebase_error(error):
    try:
        # Firebase error comes inside a nested JSON
        error_dict = error.args[1]
        error_data = eval(error_dict) if isinstance(error_dict, str) else error_dict
        return error_data['error']['message']
    except Exception:
        return "An unknown error occurred."
