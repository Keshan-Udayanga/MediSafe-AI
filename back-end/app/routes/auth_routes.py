# app/routes/auth_routes.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.auth import verify_google_token, create_jwt_token
from app.database import get_db
from app.models import User

router = APIRouter()

class GoogleLoginRequest(BaseModel):
    token: str

@router.post("/auth/google-login")
def google_login(request: GoogleLoginRequest, db=Depends(get_db)):
    # Step 1: Google token එක verify කරනවා
    google_user = verify_google_token(request.token)
    
    if not google_user:
        raise HTTPException(status_code=401, detail="Invalid Google token")
    
    # Step 2: User දැනටමත් database එකේ ඉන්නවද බලනවා
    existing_user = db.query(User).filter(User.email == google_user["email"]).first()
    
    if not existing_user:
        # අලුත් user කෙනෙක් - database එකට add කරනවා
        existing_user = User(
            username=google_user["username"],
            email=google_user["email"],
            password_hash=None  # Google login users ට password ඕන නෑ
        )
        
        db.add(existing_user)
        db.commit()
        db.refresh(existing_user)
    
    # Step 3: JWT token එක generate කරලා frontend එකට return කරනවා
    access_token = create_jwt_token({
        "email": existing_user.email,
        "username": existing_user.username
    })
    
    return {
        "access_token": access_token,
        "user": {
            "username": existing_user.username,
            "email": existing_user.email
        }
    }