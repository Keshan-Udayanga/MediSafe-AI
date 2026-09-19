# app/auth.py
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from jose import jwt
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "temporary-secret-change-this")
# Change the hardcoded fallback value to match your actual frontend client ID
GOOGLE_CLIENT_ID = os.getenv(
    "969316442650-abi1s5o13khi3iommpvdchc3s5j25lmg.apps.googleusercontent.com", 
    "433792870261-71c2798lbarhr6bhjpqv4bcep8e0em7n.apps.googleusercontent.com"
)


def create_jwt_token(user_data: dict):
    payload = {
        "sub": user_data["email"],
        "username": user_data["username"],
        "role": user_data.get("role", "user"),
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_google_token(token: str):
    if not GOOGLE_CLIENT_ID:
        logger.error("Google authentication failed: GOOGLE_CLIENT_ID is not configured")
        return None

    try:
        idinfo = id_token.verify_oauth2_token(
            token, google_requests.Request(), [
                '433792870261-71c2798lbarhr6bhjpqv4bcep8e0em7n.apps.googleusercontent.com',
                '969316442650-abi1s5o13khi3iommpvdchc3s5j25lmg.apps.googleusercontent.com'
            ]
        )
        return {
            "email": idinfo["email"],
            "username": idinfo.get("name", idinfo["email"].split("@")[0]),
            "picture": idinfo.get("picture", "")
        }
    except Exception:
        logger.exception("Google token verification failed")
        return None