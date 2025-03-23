# firebase_auth.py
import pyrebase
import streamlit as st

firebase_config = {
    "apiKey": "AIzaSyAmqxGUCPDdZzelaunj6bxX5jVlKjljPqc",
    "authDomain": "mirrorme-60800.firebaseapp.com",
    "projectId": "mirrorme-60800",
    "storageBucket": "mirrorme-60800.appspot.com",
    "messagingSenderId": "909007885081",
    "appId": "1:909007885081:web:f52febf51f231c49112b88",
    "measurementId": "G-MTMHPX5Z79",
    "databaseURL": ""  # Required for Pyrebase
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

def signup(email, password):
    try:
        return auth.create_user_with_email_and_password(email, password)
    except Exception as e:
        st.error(f"❌ Signup failed: {e}")
        return None

def login(email, password):
    try:
        return auth.sign_in_with_email_and_password(email, password)
    except Exception as e:
        st.error(f"❌ Login failed: {e}")
        return None
