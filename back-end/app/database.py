import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Explicitly load .env from the directory of this file
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

# Create the database engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class - models.py එකේ tables (User, Drug, etc.) define කරන්න use කරනවා
Base = declarative_base()

# FastAPI routes වලින් database session එකක් ගන්න use කරන dependency function එක
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


