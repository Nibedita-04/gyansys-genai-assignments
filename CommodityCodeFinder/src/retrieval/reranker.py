from sentence_transformers import CrossEncoder

reranker_model = CrossEncoder("BAAI/bge-reranker-base")


def build_doc_text(doc):

    meta = doc.metadata

    text = f"""
    Chapter: {meta.get('chapter_code', '')}
    Heading: {meta.get('heading_code', '')}
    Subheading: {meta.get('subheading_code', '')}
    HSN: {meta.get('hsn_6_digit', '')}
    Description: {meta.get('description', '')}
    """

    return text.strip()


def rerank(query, docs, top_k=30):

    if not docs:
        return []

    pairs = []
    valid_docs = []

    for doc in docs:

        text = doc.page_content.strip()

        # If empty → build from metadata
        if not text:
            text = build_doc_text(doc)

        if not text:
            continue

        pairs.append([query, text])
        valid_docs.append(doc)

    if not pairs:
        print("No valid pairs for reranking.")
        return []

    try:
        scores = reranker_model.predict(pairs)

    except Exception as e:
        print("Reranker error:", e)
        return []

    doc_scores = list(zip(valid_docs, scores))
    doc_scores.sort(key=lambda x: x[1], reverse=True)

    reranked_docs = [doc for doc, score in doc_scores[:top_k]]

    return reranked_docs


