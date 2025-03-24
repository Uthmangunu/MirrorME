import pyrebase4 as pyrebase
import streamlit as st
import json
import os

# Load Firebase config from Streamlit secrets
firebase_config = {
    "apiKey": st.secrets["FIREBASE_API_KEY"],
    "authDomain": st.secrets["FIREBASE_AUTH_DOMAIN"],
    "projectId": st.secrets["FIREBASE_PROJECT_ID"],
    "storageBucket": st.secrets["FIREBASE_STORAGE_BUCKET"],
    "messagingSenderId": st.secrets["FIREBASE_MESSAGING_SENDER_ID"],
    "appId": st.secrets["FIREBASE_APP_ID"],
    "measurementId": st.secrets["FIREBASE_MEASUREMENT_ID"]
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

def signup(email, password):
    try:
        user = auth.create_user_with_email_and_password(email, password)
        return user
    except Exception as e:
        st.error("Signup failed: {}".format(e))
        return None

def login(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return user
    except Exception as e:
        st.error("Login failed: {}".format(e))
        return None
