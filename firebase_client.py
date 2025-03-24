# firebase_client.py
from google.cloud import firestore
from google.oauth2 import service_account
import os
import json
import streamlit as st

# === 🔥 Initialize Firestore ===
def init_firestore():
    try:
        # ✅ Hosted (Streamlit Cloud) — load credentials from st.secrets
        if "GOOGLE_APPLICATION_CREDENTIALS" in st.secrets:
            creds_dict = json.loads(st.secrets["GOOGLE_APPLICATION_CREDENTIALS"])
            creds = service_account.Credentials.from_service_account_info(creds_dict)
            return firestore.Client(credentials=creds, project=creds_dict["project_id"])

        # ✅ Local environment — use path to service account JSON file
        elif os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            return firestore.Client()

        else:
            st.error("❌ Firestore credentials not found. Please check your secrets or environment variable.")
            return None

    except Exception as e:
        st.error(f"❌ Firestore init failed: {e}")
        return None

# === 🔧 Firestore Helpers ===
def get_doc(collection, doc_id):
    db = init_firestore()
    if db is None:
        return {}
    doc = db.collection(collection).document(doc_id).get()
    return doc.to_dict() if doc.exists else {}

def save_doc(collection, doc_id, data):
    db = init_firestore()
    if db:
        db.collection(collection).document(doc_id).set(data)

def update_doc(collection, doc_id, data):
    db = init_firestore()
    if db:
        db.collection(collection).document(doc_id).update(data)

def delete_doc(collection, doc_id):
    db = init_firestore()
    if db:
        db.collection(collection).document(doc_id).delete()

def get_all_docs(collection):
    db = init_firestore()
    if db is None:
        return []
    return [doc.to_dict() for doc in db.collection(collection).stream()]
