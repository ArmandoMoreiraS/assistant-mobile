import json
import os
import base64
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore

from .models import Turn, UserProfile

# Initialize Firebase
_db = None

def get_db():
    global _db
    if _db is not None:
        return _db
    
    if not firebase_admin._apps:
        b64_key = os.environ.get("FIREBASE_SERVICE_ACCOUNT_BASE64")
        if b64_key:
            import tempfile
            # Decode and create a temp file for credentials
            key_json = base64.b64decode(b64_key).decode("utf-8")
            with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
                f.write(key_json)
                temp_path = f.name
            
            cred = credentials.Certificate(temp_path)
            firebase_admin.initialize_app(cred)
            os.remove(temp_path) # Clean up
        else:
            # Fallback to default auth if on GCP, though local requires the env var
            firebase_admin.initialize_app()
            
    _db = firestore.client()
    return _db


def load_profile(user_id: str) -> UserProfile:
    db = get_db()
    doc_ref = db.collection("profiles").document(user_id)
    doc = doc_ref.get()
    if doc.exists:
        return UserProfile(**doc.to_dict())
    return UserProfile()


def save_profile(user_id: str, profile: UserProfile) -> None:
    db = get_db()
    db.collection("profiles").document(user_id).set(profile.model_dump())


def load_history(user_id: str) -> list[Turn]:
    db = get_db()
    doc_ref = db.collection("histories").document(user_id)
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict().get("turns", [])
        return [Turn(**t) for t in data]
    return []


def save_history(user_id: str, history: list[Turn]) -> None:
    db = get_db()
    db.collection("histories").document(user_id).set({
        "turns": [t.model_dump() for t in history]
    })

