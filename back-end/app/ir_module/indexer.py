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

    # Extract pages from the PDF and generate chunks for indexing
    pages = extract_pdf_pages(document["pdf_file"])
    logger.info("[PDF] Document: %s; PDF bytes: %d; pages: %d", document["title"], len(document["pdf_file"]), len(pages))
    next_chunk_id = 0

    # Process each page, normalize the text, and create chunks for indexing
    for page in pages:
        text = normalize_text(page["text"])
        if not text:
            continue
        chunks = chunk_text(text, chunk_size=500, overlap=100)
        logger.info("[INDEXER] Document: %s; original characters: %d; chunks: %d", document["title"], len(text), len(chunks))

        # Process each chunk, preprocess the text, and create a record for indexing
        for chunk in chunks:
            processed = preprocess_text(chunk)
            if processed:

                # Create a record for each chunk with relevant metadata and add it to the records list
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

    # Retrieve all document chunks from the database and rebuild the TF-IDF index
    chunks = db.query(DocumentChunk).order_by(DocumentChunk.id).all()

    # Retrieve the existing TF-IDF index record from the database
    index_record = db.query(TfidfIndex).filter(TfidfIndex.id == 1).first()

    # If there are no chunks, delete the existing index record if it exists and return
    if not chunks:
        if index_record:
            db.delete(index_record)
        return

    # Create a new TF-IDF vectorizer and fit it to the processed text of the chunks
    vectorizer = TfidfVectorizer()
    # Fit the vectorizer to the processed text of the chunks and transform it into a TF-IDF matrix
    matrix = vectorizer.fit_transform([chunk.processed_text for chunk in chunks])

    # If there is no existing index record, create a new one and add it to the database
    if index_record is None:
        index_record = TfidfIndex(id=1)
        db.add(index_record)

    index_record.version = (index_record.version or 0) + 1
    index_record.vocabulary = vectorizer.vocabulary_
    index_record.idf = vectorizer.idf_.tolist()
    index_record.matrix = matrix.toarray().tolist()
    logger.info("[INDEXER] Saved %d chunks to the database", len(chunks))


def index_document(document_id, title, document_type, pdf_bytes, db: Session):

    # Create a document dictionary and generate chunks for indexing
    document = {"id": document_id, "title": title, "document_type": document_type, "pdf_file": pdf_bytes}

    # Generate new chunks for the document and update the database
    new_records = _document_chunks(document)

    # Remove existing chunks for the document and add the new ones
    db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document_id,
        DocumentChunk.document_type == document_type,
    ).delete(synchronize_session=False)

    # Add the new chunks to the database
    db.add_all([DocumentChunk(**record) for record in new_records])

    # Flush the session to ensure that the new chunks are persisted before rebuilding the index
    db.flush()

    # Rebuild the TF-IDF index after adding the new chunks
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