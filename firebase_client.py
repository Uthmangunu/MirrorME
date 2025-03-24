from google.cloud import firestore
import os
from dotenv import load_dotenv

load_dotenv()

def init_firestore():
    return firestore.Client()

def save_doc(collection, doc_id, data):
    db = init_firestore()
    db.collection(collection).document(doc_id).set(data)

def get_doc(collection, doc_id):
    db = init_firestore()
    doc = db.collection(collection).document(doc_id).get()
    return doc.to_dict() if doc.exists else {}

def get_all_docs(collection):
    db = init_firestore()
    return [doc.to_dict() for doc in db.collection(collection).stream()]

def update_doc(collection, doc_id, updates):
    db = init_firestore()
    db.collection(collection).document(doc_id).update(updates)

def delete_doc(collection, doc_id):
    db = init_firestore()
    db.collection(collection).document(doc_id).delete()
