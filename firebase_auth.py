import pyrebase
import streamlit as st

# ✅ Load Firebase config from Render secrets
firebase_config = {
    "apiKey": st.secrets["FIREBASE_API_KEY"],
    "authDomain": st.secrets["FIREBASE_AUTH_DOMAIN"],
    "projectId": st.secrets["FIREBASE_PROJECT_ID"],
    "storageBucket": st.secrets["FIREBASE_STORAGE_BUCKET"],
    "messagingSenderId": st.secrets["FIREBASE_MESSAGING_SENDER_ID"],
    "appId": st.secrets["FIREBASE_APP_ID"],
    "measurementId": st.secrets.get("FIREBASE_MEASUREMENT_ID", ""),
    "databaseURL": ""  # Optional
}

# ✅ Initialize Firebase safely
try:
    firebase = pyrebase.initialize_app(firebase_config)
    auth = firebase.auth()
except Exception as e:
    st.error("❌ Firebase failed to initialize.")
    st.stop()

# ✅ LOGIN
def login(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return {
            "localId": user.get("localId"),
            "email": email,
            "idToken": user.get("idToken")
        }
    except Exception as e:
        raise Exception(extract_firebase_error(e))

# ✅ SIGNUP
def signup(email, password):
    try:
        user = auth.create_user_with_email_and_password(email, password)
        return {
            "localId": user.get("localId"),
            "email": email,
            "idToken": user.get("idToken")
        }
    except Exception as e:
        raise Exception(extract_firebase_error(e))

# ✅ CLEAN ERROR HANDLING
def extract_firebase_error(error):
    try:
        error_dict = error.args[1]
        error_data = eval(error_dict) if isinstance(error_dict, str) else error_dict
        return error_data['error']['message']
    except Exception:
        return "An unknown Firebase error occurred."
