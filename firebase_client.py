# firebase_client.py
import firebase_admin
from firebase_admin import credentials, initialize_app
from google.cloud import firestore
from google.oauth2 import service_account
import os
import json
import streamlit as st

# === 🔥 Initialize Firebase Admin SDK ===
def init_firebase_admin():
    try:
        if not firebase_admin._apps:
            if "GOOGLE_APPLICATION_CREDENTIALS" in st.secrets:
                try:
                    # Get credentials from secrets
                    service_account_info = json.loads(st.secrets["GOOGLE_APPLICATION_CREDENTIALS"])
                    
                    # Clean the credentials dictionary
                    service_account_info = {k: v for k, v in service_account_info.items() if v is not None}
                    
                    # Ensure private_key is properly formatted
                    if "private_key" in service_account_info:
                        service_account_info["private_key"] = service_account_info["private_key"].replace("\\n", "\n")
                    
                    # Initialize Firebase Admin SDK
                    cred = credentials.Certificate(service_account_info)
                    initialize_app(cred)
                    print("✅ Firebase Admin SDK initialized successfully")
                    return True
                except json.JSONDecodeError as e:
                    st.error(f"❌ Invalid JSON in credentials: {e}")
                    return False
                except Exception as e:
                    st.error(f"❌ Firebase Admin SDK initialization failed: {e}")
                    return False
            else:
                st.error("❌ GOOGLE_APPLICATION_CREDENTIALS not found in secrets")
                return False
        return True
    except Exception as e:
        st.error(f"❌ Firebase Admin SDK initialization failed: {e}")
        return False

# === 🔥 Initialize Firestore ===
def init_firestore():
    try:
        # Initialize Firebase Admin SDK first
        if not init_firebase_admin():
            return None
            
        # Debug: Print available secrets
        print("Available secrets:", list(st.secrets.keys()))
        
        # Check if we have the service account credentials
        if "GOOGLE_APPLICATION_CREDENTIALS" in st.secrets:
            try:
                # Get the credentials from secrets
                service_account_info = json.loads(st.secrets["GOOGLE_APPLICATION_CREDENTIALS"])
                
                # Clean the credentials dictionary
                service_account_info = {k: v for k, v in service_account_info.items() if v is not None}
                
                # Ensure private_key is properly formatted
                if "private_key" in service_account_info:
                    service_account_info["private_key"] = service_account_info["private_key"].replace("\\n", "\n")
                
                # Create credentials object
                creds = service_account.Credentials.from_service_account_info(service_account_info)
                
                # Initialize Firestore client
                return firestore.Client(credentials=creds, project=service_account_info.get("project_id"))
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
    try:
        db = init_firestore()
        if not db:
            return False
            
        doc_ref = db.collection(collection).document(user_id)
        if append_to_array:
            doc_ref.set({append_to_array: firestore.ArrayUnion([data])}, merge=True)
        else:
            doc_ref.set(data, merge=True)
        return True
    except Exception as e:
        st.error(f"❌ Error saving document: {str(e)}")
        return False

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
