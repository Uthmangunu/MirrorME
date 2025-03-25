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
    "databaseURL": ""  # Optional if you're not using Firebase Realtime DB
}

# === 🔧 Initialize Firebase ===
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

# === 🔑 Login User ===
def login(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return {
            "localId": user["localId"],
            "email": email,
            "idToken": user["idToken"]
        }
    except Exception as e:
        raise Exception(extract_firebase_error(e))


def signup(email, password):
    try:
        user = auth.create_user_with_email_and_password(email, password)
        return {
            "localId": user["localId"],
            "email": email,
            "idToken": user["idToken"]
        }
    except Exception as e:
        raise Exception(extract_firebase_error(e))
