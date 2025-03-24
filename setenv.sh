#!/bin/bash
# Run this before launching MirrorMe

export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/firebase_service_account.json"
echo "✅ Firestore credentials loaded."
echo "🚀 Launching MirrorMe..."
streamlit run Home.py
