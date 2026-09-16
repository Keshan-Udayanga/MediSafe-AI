from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.auth import (
    verify_google_token,
    create_jwt_token
)

from app.database import get_db
from app.models import User


router = APIRouter()


class GoogleLoginRequest(BaseModel):

    token: str


@router.post("/auth/google-login")
def google_login(
    request: GoogleLoginRequest,
    db=Depends(get_db)
):

    # ---------------------------------------
    # 1. Verify Google token
    # ---------------------------------------

    google_user = verify_google_token(
        request.token
    )

    if not google_user:

        raise HTTPException(
            status_code=401,
            detail="Invalid Google token"
        )

    # ---------------------------------------
    # 2. Check existing user
    # ---------------------------------------

    existing_user = (
        db.query(User)
        .filter(
            User.email == google_user["email"]
        )
        .first()
    )

    # ---------------------------------------
    # 3. Create new user
    # ---------------------------------------

    if not existing_user:

        existing_user = User(

            username=google_user["username"],

            email=google_user["email"],

            password_hash=None,

            # EVERY NEW USER = NORMAL USER
            role="user"
        )

        db.add(existing_user)

        db.commit()

        db.refresh(existing_user)

    # ---------------------------------------
    # 4. Create JWT
    # ---------------------------------------

    access_token = create_jwt_token({

        "email": existing_user.email,

        "username": existing_user.username,

        "role": existing_user.role
    })

    # ---------------------------------------
    # 5. Return user + role
    # ---------------------------------------

    return {

        "access_token": access_token,

        "user": {

            "id": existing_user.id,

            "username": existing_user.username,

            "email": existing_user.email,

            "role": existing_user.role
        }
    }