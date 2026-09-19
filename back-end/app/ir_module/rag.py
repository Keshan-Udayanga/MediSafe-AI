from app.ir_module.retrieval import retrieve_relevant_chunks


NO_RELEVANT_DOCUMENT_MESSAGE = (
    "I’m sorry, but I could not find relevant information "
    "in the available medical documents to answer this question."
)


def retrieve_context(
    query: str,
):

    results = retrieve_relevant_chunks(
        query=query,
    )

    if not results:
        return {
            "has_context": False,
            "message": NO_RELEVANT_DOCUMENT_MESSAGE,
            "documents": [],
            "context": "",
        }

    context_parts = []

    for result in results:

        context_parts.append(
            f"""
            Document: {result['title']}
            Type: {result['document_type']}
            Relevance Score: {result['score']:.4f}

            Content:
            {result['text']}
                """
        )

    return {
        "has_context": True,
        "message": "",
        "documents": results,
        "context": "\n\n".join(context_parts),
    }