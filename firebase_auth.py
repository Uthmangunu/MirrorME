import pyrebase
import streamlit as st

# === 🔐 Firebase Config from Streamlit Secrets ===
try:
    firebase_config = {
        "apiKey": st.secrets["FIREBASE_API_KEY"],
        "authDomain": st.secrets["FIREBASE_AUTH_DOMAIN"],
        "projectId": st.secrets["FIREBASE_PROJECT_ID"],
        "storageBucket": st.secrets["FIREBASE_STORAGE_BUCKET"],
        "messagingSenderId": st.secrets["FIREBASE_MESSAGING_SENDER_ID"],
        "appId": st.secrets["FIREBASE_APP_ID"],
        "measurementId": st.secrets["FIREBASE_MEASUREMENT_ID"],
        "databaseURL": st.secrets.get("FIREBASE_DATABASE_URL", "")  # Optional if you're not using Firebase Realtime DB
    }
except KeyError as e:
    st.error(f"❌ Missing required Firebase configuration: {e}")
    raise

# === 🔧 Initialize Firebase ===
try:
    firebase = pyrebase.initialize_app(firebase_config)
    auth = firebase.auth()
except Exception as e:
    st.error(f"❌ Failed to initialize Firebase: {e}")
    raise

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
