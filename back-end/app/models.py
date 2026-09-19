from sqlalchemy import Column, Integer, String, DateTime, LargeBinary, JSON, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True
    )

    username = Column(
        String(50),
        nullable=False
    )

    email = Column(
        String(100),
        unique=True,
        nullable=False
    )

    password_hash = Column(
        String(255),
        nullable=True
    )

    role = Column(
        String(20),
        nullable=False,
        default="user"
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )


class DrugInformationDocument(Base):

    __tablename__ = "drug_information_documents"

    id = Column(
        Integer,
        primary_key=True
    )

    title = Column(
        String(255),
        nullable=False
    )

    pdf_file = Column(
        LargeBinary,
        nullable=False
    )


class SafetyDocument(Base):

    __tablename__ = "safety_documents"

    id = Column(
        Integer,
        primary_key=True
    )

    title = Column(
        String(255),
        nullable=False
    )

    pdf_file = Column(
        LargeBinary,
        nullable=False
    )


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    __table_args__ = (UniqueConstraint("document_id", "document_type", "chunk_id", name="uq_document_chunk_source"),)

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, nullable=False, index=True)
    document_type = Column(String(30), nullable=False, index=True)
    chunk_id = Column(Integer, nullable=False)
    page_number = Column(Integer, nullable=False)
    original_text = Column(String, nullable=False)
    processed_text = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class TfidfIndex(Base):
    __tablename__ = "tfidf_index"

    id = Column(Integer, primary_key=True)
    version = Column(Integer, nullable=False, default=1)
    vocabulary = Column(JSON, nullable=False)
    idf = Column(JSON, nullable=False)
    matrix = Column(JSON, nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)