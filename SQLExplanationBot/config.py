import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()
SQLITE_DB_PATH = "database/sales.db"

def get_llm():
    return ChatGroq(
        model="openai/gpt-oss-20b",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0
    )
