import chromadb

client = chromadb.PersistentClient(path = "./storage/chroma_db")

def get_client():
    return client