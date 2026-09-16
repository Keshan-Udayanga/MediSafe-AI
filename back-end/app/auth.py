# app/auth.py
import os
from datetime import datetime, timedelta
from jose import jwt
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "temporary-secret-change-this")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")  # front-end එකේ use කරපු ID එකම

def create_jwt_token(user_data: dict):
    payload = {
        "sub": user_data["email"],
        "username": user_data["username"],
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_google_token(token: str):
    # Google එකෙන් ආපු token එක validate කරනව
    try:
        idinfo = id_token.verify_oauth2_token(
            token, google_requests.Request(), GOOGLE_CLIENT_ID
        )
        return {
            "email": idinfo["email"],
            "username": idinfo.get("name", idinfo["email"].split("@")[0]),
            "picture": idinfo.get("picture", "")
        }
    except ValueError:
        return None   # token invalid