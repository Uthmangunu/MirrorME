# utils/feedback_logger.py

from firebase_client import save_doc
from datetime import datetime

def log_feedback(content, page="unknown", feedback_type="general", user_id="anonymous"):
    feedback_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "page": page,
        "type": feedback_type,
        "content": content
    }

    # Use the timestamp as a unique doc ID for easier browsing
    doc_id = f"{user_id}_{datetime.utcnow().isoformat()}"
    save_doc("feedback_logs", doc_id, feedback_entry)
