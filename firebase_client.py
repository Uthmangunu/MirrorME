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
            try:
                creds_path = st.secrets["GOOGLE_APPLICATION_CREDENTIALS"]
                
                # If it's a path to a file
                if isinstance(creds_path, str) and os.path.isfile(creds_path):
                    try:
                        with open(creds_path, 'r') as f:
                            creds_dict = json.load(f)
                    except Exception as e:
                        st.error(f"❌ Error reading credentials file: {e}")
                        return None
                # If it's a JSON string
                elif isinstance(creds_path, str):
                    try:
                        creds_dict = json.loads(creds_path)
                    except json.JSONDecodeError as e:
                        st.error(f"❌ Invalid JSON in credentials string: {e}")
                        return None
                # If it's already a dictionary
                else:
                    creds_dict = creds_path
                
                # Clean the credentials dictionary
                creds_dict = {k: v for k, v in creds_dict.items() if v is not None}
                
                creds = service_account.Credentials.from_service_account_info(creds_dict)
                return firestore.Client(credentials=creds, project=creds_dict.get("project_id"))
            except Exception as e:
                st.error(f"❌ Error processing credentials: {e}")
                return None

        # ✅ Local environment — use path to service account JSON file
        elif os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            try:
                return firestore.Client()
            except Exception as e:
                st.error(f"❌ Error initializing Firestore client: {e}")
                return None

        else:
            st.error("❌ Firestore credentials not found. Please check your secrets or environment variable.")
            return None

    except Exception as e:
        st.error(f"❌ Firestore init failed: {str(e)}")
        return None

# === 🔧 Firestore Helpers ===
def get_doc(collection, doc_id):
    db = init_firestore()
    if db is None:
        return {}
    doc = db.collection(collection).document(doc_id).get()
    return doc.to_dict() if doc.exists else {}

def save_doc(collection, user_id, data, append_to_array=None):
    db = init_firestore()
    if db:
        doc_ref = db.collection(collection).document(user_id)
        if append_to_array:
            doc_ref.set({append_to_array: firestore.ArrayUnion([data])}, merge=True)
        else:
            doc_ref.set(data)

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
