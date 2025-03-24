@echo off
REM Windows launcher for MirrorMe

SET GOOGLE_APPLICATION_CREDENTIALS=%cd%\firebase_service_account.json
ECHO ✅ Firestore credentials loaded.
ECHO 🚀 Launching MirrorMe...
streamlit run Home.py
PAUSE
