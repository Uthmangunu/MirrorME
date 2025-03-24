from google.cloud import firestore
from google.oauth2 import service_account
import os
import json
import streamlit as st

def init_firestore():
    try:
        # Streamlit Cloud: read full JSON string from secrets
        if "GOOGLE_APPLICATION_CREDENTIALS" in st.secrets:
            info = json.loads(st.secrets["GOOGLE_APPLICATION_CREDENTIALS"])
            creds = service_account.Credentials.from_service_account_info(info)
            return firestore.Client(credentials=creds, project=info["project_id"])
        
        # Local: use key file
        elif os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            return firestore.Client()
        
        else:
            st.error("❌ No Firestore credentials found.")
            return None
    except Exception as e:
        st.error(f"❌ Firestore init failed: {e}")
        return None
