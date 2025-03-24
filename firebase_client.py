import streamlit as st
from google.cloud import firestore
from google.oauth2 import service_account
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# === 🔥 FIREBASE CLIENT WRAPPER ===
def init_firestore():
    try:
        # Streamlit secrets or local .env with inline JSON
        creds_str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

        if creds_str and creds_str.strip().startswith("{"):
            creds_dict = json.loads(creds_str)
            creds = service_account.Credentials.from_service_account_info(creds_dict)
            return firestore.Client(credentials=creds, project=creds_dict.get("project_id"))

        # Local JSON path fallback
        elif os.path.exists("firebase_service_account.json"):
            creds = service_account.Credentials.from_service_account_file("firebase_service_account.json")
            return firestore.Client(credentials=creds)

        else:
            st.error("❌ Firestore credentials not found. Please set GOOGLE_APPLICATION_CREDENTIALS or provide firebase_service_account.json")
            return None

    except Exception as e:
        st.error(f"❌ Firestore init failed: {e}")
        return None

# === 🔧 DOCUMENT HELPERS ===
def get_doc(collection, user_id):
    db = init_firestore()
    if db is None:
        return {}
    doc = db.collection(collection).document(user_id).get()
    return doc.to_dict() if doc.exists else {}

def save_doc(collection, user_id, data):
    db = init_firestore()
    if db:
        db.collection(collection).document(user_id).set(data)

def update_doc(collection, user_id, data):
    db = init_firestore()
    if db:
        db.collection(collection).document(user_id).update(data)

def delete_doc(collection, user_id):
    db = init_firestore()
    if db:
        db.collection(collection).document(user_id).delete()
