import streamlit as st
from google.cloud import firestore
import os
import json
from dotenv import load_dotenv

# Load Firebase service account if using local
load_dotenv()

# === 🔥 FIREBASE CLIENT WRAPPER ===
def init_firestore():
    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.path.exists("firebase_service_account.json"):
        return firestore.Client()
    else:
        st.error("Firestore credentials not found. Set GOOGLE_APPLICATION_CREDENTIALS or upload JSON.")
        return None

# === 🔧 DOCUMENT HELPERS ===
def get_doc(collection, user_id):
    db = init_firestore()
    doc = db.collection(collection).document(user_id).get()
    return doc.to_dict() if doc.exists else {}

def save_doc(collection, user_id, data):
    db = init_firestore()
    db.collection(collection).document(user_id).set(data)

def update_doc(collection, user_id, data):
    db = init_firestore()
    db.collection(collection).document(user_id).update(data)

def delete_doc(collection, user_id):
    db = init_firestore()
    db.collection(collection).document(user_id).delete()
