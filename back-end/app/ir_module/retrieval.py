import logging
import os
import sys
from typing import List, Dict

import numpy as np
from app.database import SessionLocal
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.models import DocumentChunk, TfidfIndex
from app.ir_module.preprocessing import preprocess_text


logger = logging.getLogger(__name__)
RAG_THRESHOLD = float(os.getenv("RAG_THRESHOLD", "0.10"))
TOP_K = 5


def retrieve_relevant_chunks(
    query: str,
    top_k: int = TOP_K,
    min_similarity: float = RAG_THRESHOLD,
) -> List[Dict]:
    with SessionLocal() as db:
        index = db.query(TfidfIndex).filter(TfidfIndex.id == 1).first()
        if not index:
            logger.warning("[RETRIEVAL] No database TF-IDF index available")
            return []

        query_processed = preprocess_text(query)
        if not query_processed:
            return []

        vectorizer = TfidfVectorizer(vocabulary=index.vocabulary)
        vectorizer.fit([" ".join(index.vocabulary.keys())])
        vectorizer._tfidf.idf_ = np.asarray(index.idf, dtype=float)
        vectorizer.fixed_vocabulary_ = True
        query_vector = vectorizer.transform([query_processed])
        matrix = np.asarray(index.matrix, dtype=float)
        similarities = cosine_similarity(query_vector, matrix)[0]
        chunks = db.query(DocumentChunk).order_by(DocumentChunk.id).all()
        ranked = sorted(enumerate(similarities), key=lambda item: item[1], reverse=True)
        logger.info("[RETRIEVAL] Query: %s; indexed chunks: %d", query, len(chunks))

        results = []
        for item_index, score in ranked:
            if score < min_similarity:
                continue
            chunk = chunks[item_index]
            results.append({
                "document_id": chunk.document_id,
                "title": _document_title(db, chunk.document_id, chunk.document_type),
                "document_type": chunk.document_type,
                "chunk_id": chunk.chunk_id,
                "page_number": chunk.page_number,
                "text": chunk.original_text,
                "score": float(score),
            })
            if len(results) >= top_k:
                break

        return results


def _document_title(db, document_id: int, document_type: str) -> str:
    from app.models import DrugInformationDocument, SafetyDocument

    model = SafetyDocument if document_type == "safety" else DrugInformationDocument
    document = db.query(model.title).filter(model.id == document_id).first()
    return document[0] if document else "Unknown document"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    query = " ".join(sys.argv[1:])
    results = retrieve_relevant_chunks(query)
    print(f"Query: {query}")
    print(f"Has context: {bool(results)}")
    print("Top documents:")
    for result in results:
        print(f"- {result['title']} | document={result['document_id']} | similarity={result['score']:.4f}")