# vector_store.py
import openai
import hashlib
from firebase_client import save_doc, get_doc, get_all_docs
from dotenv import load_dotenv
import os
import numpy as np

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# === Utility: Create a hash ID for text ===
def hash_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

# === Store vector ===
def store_vector(user_id, text, source="chat"):
    try:
        embedding = openai.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        ).data[0].embedding

        vector_id = hash_text(text)
        save_doc("vectors", f"{user_id}_{vector_id}", {
            "user_id": user_id,
            "vector": embedding,
            "text": text,
            "source": source
        })
    except Exception as e:
        print("Embedding store error:", e)

# === Retrieve similar vectors ===
def get_similar_memories(user_id, query_text, top_n=3):
    try:
        query_vec = openai.embeddings.create(
            model="text-embedding-ada-002",
            input=query_text
        ).data[0].embedding

        all_vectors = get_all_docs("vectors")
        user_vectors = [v for v in all_vectors if v.get("user_id") == user_id]

        def cosine_sim(a, b):
            a, b = np.array(a), np.array(b)
            return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

        scored = [
            (v["text"], cosine_sim(query_vec, v["vector"]))
            for v in user_vectors if "vector" in v
        ]

        scored.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in scored[:top_n]]

    except Exception as e:
        print("Similarity retrieval error:", e)
        return []
