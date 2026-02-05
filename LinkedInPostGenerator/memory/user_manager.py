from memory.db_client import get_client
import re
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")

def sanitize_name(name: str):
    name = name.strip().replace(" ", "_")
    name = re.sub(r"[^a-zA-Z0-9._-]", "", name)
    return name

def get_user_collection(user_id):
    safe_user_id = sanitize_name(user_id)
    collection_name = f"user_{safe_user_id}_memory"

    return client.get_or_create_collection(
        name=collection_name
    )


def get_global_collection():
    return client.get_or_create_collection(
        name="global_memory"
    )
