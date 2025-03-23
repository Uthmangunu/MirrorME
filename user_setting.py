# user_settings.py

import os
import json

DEFAULT_SETTINGS = {
    "dark_mode": False,
    "voice_id": "3Tjd0DlL3tjpqnkvDu9j"
}

def get_settings_path(user_id):
    return f"user_data/{user_id}/settings.json"

def load_user_settings(user_id):
    path = get_settings_path(user_id)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return DEFAULT_SETTINGS.copy()

def save_user_settings(user_id, settings):
    path = get_settings_path(user_id)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(settings, f, indent=2)
