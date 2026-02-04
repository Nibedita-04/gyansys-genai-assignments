from memory.embedding_model import get_embedding
from memory.user_manager import get_user_collection
import uuid
from datetime import datetime

def store_memory(user_id, text):
    collection = get_user_collection(user_id)
    embedding = get_embedding(text)

    memory_id = str(uuid.uuid4())

    collection.add(
        ids = [memory_id],
        documents = [text],
        embeddings = [embedding],
        metadata = [{
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }]
    )
    
    return memory_id