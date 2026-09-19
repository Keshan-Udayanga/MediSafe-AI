import logging

from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer

from app.database import SessionLocal
from app.models import DocumentChunk, TfidfIndex
from app.ir_module.pdf_loader import extract_pdf_pages
from app.ir_module.preprocessing import chunk_text, normalize_text, preprocess_text


logger = logging.getLogger(__name__)


def _document_chunks(document):
    records = []
    pages = extract_pdf_pages(document["pdf_file"])
    logger.info("[PDF] Document: %s; PDF bytes: %d; pages: %d", document["title"], len(document["pdf_file"]), len(pages))
    next_chunk_id = 0
    for page in pages:
        text = normalize_text(page["text"])
        if not text:
            continue
        chunks = chunk_text(text, chunk_size=500, overlap=100)
        logger.info("[INDEXER] Document: %s; original characters: %d; chunks: %d", document["title"], len(text), len(chunks))
        for chunk in chunks:
            processed = preprocess_text(chunk)
            if processed:
                records.append({
                    "document_id": document["id"],
                    "document_type": document["document_type"],
                    "chunk_id": next_chunk_id,
                    "page_number": page["page_number"],
                    "original_text": chunk,
                    "processed_text": processed,
                })
            next_chunk_id += 1
    return records


def rebuild_index(db: Session):
    chunks = db.query(DocumentChunk).order_by(DocumentChunk.id).all()
    index_record = db.query(TfidfIndex).filter(TfidfIndex.id == 1).first()

    if not chunks:
        if index_record:
            db.delete(index_record)
        return

    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform([chunk.processed_text for chunk in chunks])
    if index_record is None:
        index_record = TfidfIndex(id=1)
        db.add(index_record)

    index_record.version = (index_record.version or 0) + 1
    index_record.vocabulary = vectorizer.vocabulary_
    index_record.idf = vectorizer.idf_.tolist()
    index_record.matrix = matrix.toarray().tolist()
    logger.info("[INDEXER] Saved %d chunks to the database", len(chunks))


def index_document(document_id, title, document_type, pdf_bytes, db: Session):
    document = {"id": document_id, "title": title, "document_type": document_type, "pdf_file": pdf_bytes}
    new_records = _document_chunks(document)
    db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document_id,
        DocumentChunk.document_type == document_type,
    ).delete(synchronize_session=False)
    db.add_all([DocumentChunk(**record) for record in new_records])
    db.flush()
    rebuild_index(db)


def remove_document(document_id, document_type, db: Session):
    db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document_id,
        DocumentChunk.document_type == document_type,
    ).delete(synchronize_session=False)
    rebuild_index(db)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    with SessionLocal() as db:
        rebuild_index(db)
        db.commit()