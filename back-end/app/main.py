# FastAPI app entry point
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth_routes
from app.database import engine, Base
from app import models 

app = FastAPI(title="MediSafe AI")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the authentication routes
app.include_router(auth_routes.router)


# ← මේ line එකෙන් models.py එකේ define කරපු tables ඔක්කොම, database එකේ physically create වෙනවා
Base.metadata.create_all(bind=engine)

# check if the backend is running
@app.get("/")
def root():
    return {
        "message": "MediSafe AI Backend is running"
    }

