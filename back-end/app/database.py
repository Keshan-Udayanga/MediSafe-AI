import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env file
load_dotenv()

# Get the database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Create the database engine
engine = create_engine(DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)