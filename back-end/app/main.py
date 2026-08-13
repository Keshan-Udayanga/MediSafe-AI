# FastAPI app entry point

from fastapi import FastAPI

app = FastAPI(title="MediSafe AI")

# check if the backend is running
@app.get("/")
def root():
    return {
        "message": "MediSafe AI Backend is running"
    }

