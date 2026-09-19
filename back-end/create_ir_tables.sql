-- Run once against the existing PostgreSQL/Supabase database.
-- The existing users, drug_information_documents, and safety_documents tables are unchanged.

CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL,
    document_type VARCHAR(30) NOT NULL,
    chunk_id INTEGER NOT NULL,
    page_number INTEGER NOT NULL,
    original_text TEXT NOT NULL,
    processed_text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_document_chunk_source UNIQUE (document_id, document_type, chunk_id)
);

CREATE INDEX IF NOT EXISTS ix_document_chunks_document_id
    ON document_chunks (document_id);

CREATE INDEX IF NOT EXISTS ix_document_chunks_document_type
    ON document_chunks (document_type);

CREATE TABLE IF NOT EXISTS tfidf_index (
    id INTEGER PRIMARY KEY,
    version INTEGER NOT NULL DEFAULT 1,
    vocabulary JSONB NOT NULL,
    idf JSONB NOT NULL,
    matrix JSONB NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
