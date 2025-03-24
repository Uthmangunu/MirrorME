from firebase_client import get_doc, save_doc
from datetime import date

# === 📓 Save Journal Entry ===
def save_journal_entry(user_id, text, reflection, adjustments):
    today = date.today().isoformat()
    data = get_doc("journals", user_id)
    entries = data.get("entries", [])
    entries.append({
        "date": today,
        "text": text,
        "reflection": reflection,
        "adjustments": adjustments
    })
    save_doc("journals", user_id, {"entries": entries})

# === 📓 Load Past Entries ===
def get_journal_entries(user_id):
    data = get_doc("journals", user_id)
    return sorted(data.get("entries", []), key=lambda x: x["date"], reverse=True)
