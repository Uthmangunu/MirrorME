# firebase_client.py
from google.cloud import firestore
from google.oauth2 import service_account
import os
import json
import streamlit as st

# === 🔥 Initialize Firestore ===
def init_firestore():
    try:
        # Debug: Print available secrets
        st.write("Available secrets:", list(st.secrets.keys()))
        
        # Check if we have the service account credentials
        if "GOOGLE_APPLICATION_CREDENTIALS" in st.secrets:
            try:
                # Get the credentials from secrets
                creds_data = st.secrets["GOOGLE_APPLICATION_CREDENTIALS"]
                
                # If it's a string, try to parse it as JSON
                if isinstance(creds_data, str):
                    try:
                        creds_dict = json.loads(creds_data)
                    except json.JSONDecodeError as e:
                        st.error(f"❌ Invalid JSON in credentials: {e}")
                        return None
                else:
                    creds_dict = creds_data
                
                # Clean the credentials dictionary
                creds_dict = {k: v for k, v in creds_dict.items() if v is not None}
                
                # Ensure private_key is properly formatted
                if "private_key" in creds_dict:
                    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
                
                # Create credentials object
                creds = service_account.Credentials.from_service_account_info(creds_dict)
                
                # Initialize Firestore client
                return firestore.Client(credentials=creds, project=creds_dict.get("project_id"))
            except Exception as e:
                st.error(f"❌ Error processing credentials: {e}")
                return None
        else:
            st.error("❌ Service account credentials not found in secrets. Please add GOOGLE_APPLICATION_CREDENTIALS to your secrets.")
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
