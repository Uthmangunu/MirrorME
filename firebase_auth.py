import os
from dotenv import load_dotenv
import pyrebase

load_dotenv()

firebase_config = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID"),
    "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID"),
    "databaseURL": ""
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

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

def extract_firebase_error(error):
    try:
        error_dict = error.args[1]
        error_data = eval(error_dict) if isinstance(error_dict, str) else error_dict
        return error_data['error']['message']
    except Exception:
        return "An unknown Firebase error occurred."
