# firebase_auth.py (🔥 using Firebase REST API)
import streamlit as st
import requests

API_KEY = st.secrets["FIREBASE_API_KEY"]

FIREBASE_SIGNUP_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
FIREBASE_LOGIN_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"

def signup(email, password):
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    try:
        response = requests.post(FIREBASE_SIGNUP_URL, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Signup failed: {response.json().get('error', {}).get('message', str(e))}")
        return None

def login(email, password):
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    try:
        response = requests.post(FIREBASE_LOGIN_URL, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Login failed: {response.json().get('error', {}).get('message', str(e))}")
        return None
