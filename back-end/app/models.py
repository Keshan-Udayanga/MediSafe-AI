# app/models.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base   # Base class එකක් define කරලා තියෙන්න ඕන

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=True)  # nullable - Google login ට password ඕන නෑ
    created_at = Column(DateTime, server_default=func.now())