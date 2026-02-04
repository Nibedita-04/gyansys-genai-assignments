from memory.embedding_model import get_embedding
from memory.user_manager import get_user_collection

def retrieve_memory(user_id, query, k=5):
    collection = get_user_collection(user_id)
    embedding = get_embedding(query)

    results = collection.query(
        query_embeddings = [embedding],
        n_results = k,
        include = ["documents", "distances", "metadata"]
    )

    if not results or not results["documents"]:
        return []

    return list(zip(
        results["documents"][0],
        results["distances"][0]
    ))