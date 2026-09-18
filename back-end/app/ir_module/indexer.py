import logging
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from app.database import SessionLocal
from app.ir_module.document_store import get_all_documents
from app.ir_module.pdf_loader import extract_pdf_pages
from app.ir_module.preprocessing import chunk_text, normalize_text, preprocess_text


logger = logging.getLogger(__name__)
INDEX_DIR = Path(__file__).resolve().parent / "index"
INDEX_FILE = INDEX_DIR / "documents.json"


def _document_chunks(document):
    records = []
    pages = extract_pdf_pages(document["pdf_file"])
    logger.info("[PDF] Document: %s; PDF bytes: %d; pages: %d", document["title"], len(document["pdf_file"]), len(pages))
    for page in pages:
        text = normalize_text(page["text"])
        if not text:
            continue
        chunks = chunk_text(text, chunk_size=500, overlap=100)
        processed_text = preprocess_text(text)
        logger.info("[INDEXER] Document: %s; original characters: %d; processed characters: %d; tokens: %d; chunks: %d", document["title"], len(text), len(processed_text), len(processed_text.split()), len(chunks))
        for chunk_id, chunk in enumerate(chunks):
            processed = preprocess_text(chunk)
            if processed:
                records.append({"document_id": document["id"], "title": document["title"], "document_type": document["document_type"], "chunk_id": chunk_id, "page_number": page["page_number"], "text": chunk, "processed_text": processed})
    return records


def _write_records(records):
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    if not records:
        INDEX_FILE.unlink(missing_ok=True)
        return
    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform([record["processed_text"] for record in records])
    payload = {
        "version": 1,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "records": records,
        "vocabulary": vectorizer.vocabulary_,
        "idf": vectorizer.idf_.tolist(),
        "matrix": matrix.toarray().tolist(),
    }
    temporary_file = INDEX_FILE.with_suffix(".tmp")
    with temporary_file.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False)
    os.replace(temporary_file, INDEX_FILE)
    logger.info("[INDEXER] Saved %d chunks to %s", len(records), INDEX_FILE)


def load_index():
    if not INDEX_FILE.exists():
        logger.warning("[INDEXER] Index does not exist: %s", INDEX_FILE)
        return None
    try:
        with INDEX_FILE.open("r", encoding="utf-8") as file:
            payload = json.load(file)
        vectorizer = TfidfVectorizer(vocabulary=payload["vocabulary"])
        vectorizer.fit([" ".join(payload["vocabulary"].keys())])
        vectorizer._tfidf.idf_ = np.asarray(payload["idf"], dtype=float)
        vectorizer.fixed_vocabulary_ = True
        payload["vectorizer"] = vectorizer
        payload["matrix"] = np.asarray(payload["matrix"], dtype=float)
        return payload
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        logger.exception("[INDEXER] Unable to load local index: %s", INDEX_FILE)
        return None


def rebuild_index(db=None):
    owns_session = db is None
    db = db or SessionLocal()
    records = []
    try:
        for document in get_all_documents(db, include_pdf=True):
            try:
                records.extend(_document_chunks(document))
            except Exception:
                logger.exception("[INDEXER] Skipping invalid PDF: %s", document["title"])
        _write_records(records)
    finally:
        if owns_session:
            db.close()


def index_document(document_id, title, document_type, pdf_bytes):
    document = {"id": document_id, "title": title, "document_type": document_type, "pdf_file": pdf_bytes}
    new_records = _document_chunks(document)
    current = load_index()
    records = [] if not current else [record for record in current["records"] if not (record["document_id"] == document_id and record["document_type"] == document_type)]
    _write_records(records + new_records)


def remove_document(document_id, document_type):
    current = load_index()
    if current:
        _write_records([record for record in current["records"] if not (record["document_id"] == document_id and record["document_type"] == document_type)])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    rebuild_index()