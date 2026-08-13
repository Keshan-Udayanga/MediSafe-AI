from database import engine, SessionLocal
from sqlalchemy import text

try:
    with engine.connect() as conn:
        print("Connected to the database")

except Exception as e:
    print(f"An error occurred: {e}")