import pyrebase
import streamlit as st
import json

firebase_config = {
    "apiKey": st.secrets["firebase"]["api_key"],
    "authDomain": st.secrets["firebase"]["auth_domain"],
    "projectId": st.secrets["firebase"]["project_id"],
    "storageBucket": st.secrets["firebase"]["storage_bucket"],
    "messagingSenderId": st.secrets["firebase"]["messaging_sender_id"],
    "appId": st.secrets["firebase"]["app_id"],
    "measurementId": st.secrets["firebase"]["measurement_id"],
    "databaseURL": ""
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

# Optional: Admin functionality with service account (if needed later)
with open("firebase_service_account.json") as f:
    service_account = json.load(f)

# Signup
def signup(email: str, password: str):
    try:
        user = auth.create_user_with_email_and_password(email, password)
        return user
    except Exception as e:
        st.error(f"Signup Error: {e}")
        return None

# Login
def login(email: str, password: str):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return user
    except Exception as e:
        st.error(f"Login Error: {e}")
        return None
