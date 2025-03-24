import firebase_admin
from firebase_admin import credentials, auth
import streamlit as st

# Initialize Firebase Admin SDK
cred = credentials.Certificate("firebase_service_account.json")
firebase_admin.initialize_app(cred)

# Firebase Authentication functions

# Signup function (uses Firebase Admin SDK)
def signup(email: str, password: str):
    try:
        user = auth.create_user(
            email=email,
            password=password
        )
        return user.uid  # Return user UID after successful signup
    except Exception as e:
        st.error(f"Signup failed: {e}")
        return None

# Sign-in function (uses Firebase Admin SDK)
def signin_with_email(email: str, password: str):
    try:
        # Firebase Admin SDK doesn't directly handle password authentication.
        # We can use Firebase client SDK for client-side login (which is recommended)
        # For server-side, this method would only fetch user data if login is valid.
        # Assuming user authentication happens on the client-side (using Firebase JS SDK, for example)
        
        # Just return user information for now (you should integrate Firebase client SDK for full auth flow)
        user = auth.get_user_by_email(email)
        return user.uid  # Return user UID after successful authentication
    except Exception as e:
        st.error(f"Login failed: {e}")
        return None

