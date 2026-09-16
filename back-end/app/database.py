import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load environment variables from .env file
load_dotenv()

# Get the database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Create the database engine
engine = create_engine(DATABASE_URL)

# Create a session factory
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