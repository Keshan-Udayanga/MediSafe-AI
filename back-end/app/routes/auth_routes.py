import logging

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from app.auth import SECRET_KEY, create_jwt_token, verify_google_token

from app.database import get_db
from app.models import User


router = APIRouter()
logger = logging.getLogger(__name__)
bearer_scheme = HTTPBearer(auto_error=False)


class GoogleLoginRequest(BaseModel):

    token: str


def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db=Depends(get_db),
):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    user = db.query(User).filter(User.email == payload.get("sub")).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.get("/api/v1/auth/me")
def current_user(user: User = Depends(get_authenticated_user)):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
    }


@router.post("/auth/google-login")
def google_login(
    request: GoogleLoginRequest,
    db=Depends(get_db)
):

    logger.info("Google login request received")

    # ---------------------------------------
    # 1. Verify Google token
    # ---------------------------------------

    google_user = verify_google_token(
        request.token
    )

    if not google_user:

        logger.error("Google login rejected: token verification returned no user")

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