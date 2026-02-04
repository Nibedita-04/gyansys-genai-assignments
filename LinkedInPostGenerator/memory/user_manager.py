from memory.db_client import get_client

def get_user_collection(user_id):
    client = get_client()
    return client.get_or_create_collection(name = f"user_{user_id}")

def user_exists(user_id):
    client = get_client()
    try:
        client.get_collection(name=f"user_{user_id}")
        return True
    except:
        return False