import logging
import os
import sys
from typing import List, Dict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.ir_module.indexer import load_index
from app.ir_module.preprocessing import preprocess_text


logger = logging.getLogger(__name__)
RAG_THRESHOLD = float(os.getenv("RAG_THRESHOLD", "0.10"))
TOP_K = 5


def retrieve_relevant_chunks(
    query: str,
    top_k: int = TOP_K,
    min_similarity: float = RAG_THRESHOLD,
) -> List[Dict]:
    index = load_index()
    if not index or not index.get("records"):
        logger.warning("[RETRIEVAL] No local index records available")
        return []

    query_processed = preprocess_text(query)
    if not query_processed:
        return []

    query_vector = index["vectorizer"].transform([query_processed])
    similarities = cosine_similarity(query_vector, index["matrix"])[0]
    ranked = sorted(enumerate(similarities), key=lambda item: item[1], reverse=True)
    logger.info("[RETRIEVAL] Query: %s; indexed chunks: %d", query, len(index["records"]))
    for item_index, score in ranked[:top_k]:
        record = index["records"][item_index]
        logger.info("[RETRIEVAL] score: %.4f, document: %s, title: %s", score, record["document_id"], record["title"])

    results = []

    for item_index, score in ranked:
        if score < min_similarity:
            continue
        result = dict(index["records"][item_index])
        result.pop("processed_text", None)
        result["score"] = float(score)
        results.append(result)
        if len(results) >= top_k:
            break

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results[:top_k]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    query = " ".join(sys.argv[1:]) or "Aspirin"
    results = retrieve_relevant_chunks(query)
    print(f"Query: {query}")
    print(f"Has context: {bool(results)}")
    print("Top documents:")
    for result in results:
        print(f"- {result['title']} | document={result['document_id']} | similarity={result['score']:.4f}")