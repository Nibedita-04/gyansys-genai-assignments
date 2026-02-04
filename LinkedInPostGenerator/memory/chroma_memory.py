from memory.db_client import get_client

def get_memory_collection():
    client = get_client()
    collection = client.get_or_create_collection(
        name = "user_memory"
    )
    return collection