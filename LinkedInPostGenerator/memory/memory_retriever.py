# from memory.embedding_model import get_embedding
# from memory.user_manager import get_user_collection

# def retrieve_memory(user_id, query, k=5):
#     collection = get_user_collection(user_id)
#     embedding = get_embedding(query)

#     results = collection.query(
#         query_embeddings = [embedding],
#         n_results = k,
#         include = ["documents", "distances", "metadata"]
#     )

#     if not results or not results["documents"]:
#         return []

#     return list(zip(
#         results["documents"][0],
#         results["distances"][0]
#     ))

from memory.embedding_model import get_embedding
from memory.user_manager import get_user_collection, get_global_collection

def retrieve_memory(user_id, query, k=5, mode="linked"):
    embedding = get_embedding(query)

    # Standalone mode = no memory
    if mode == "standalone":
        return []

    memories = []

    # Personal memory
    user_collection = get_user_collection(user_id)
    user_results = user_collection.query(
        query_embeddings=[embedding],
        n_results=k
    )

    if user_results["documents"]:
        memories += user_results["documents"][0]

    # Global memory
    global_collection = get_global_collection()
    global_results = global_collection.query(
        query_embeddings=[embedding],
        n_results=k
    )

    if global_results["documents"]:
        memories += global_results["documents"][0]

    return memories[:k]
