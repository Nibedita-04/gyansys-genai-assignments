# src/ingestion/vectordb.py

from langchain_openai import AzureOpenAIEmbeddings
from langchain_chroma import Chroma
from src.config import settings


def get_embedding_model():
    return AzureOpenAIEmbeddings(
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_OPENAI_KEY,
        azure_deployment=settings.AZURE_EMBEDDING_DEPLOYMENT,
        openai_api_version=settings.AZURE_API_VERSION,
    )


def get_vectorstore(persist_directory="chroma_db"):
    embedding = get_embedding_model()

    return Chroma(
        collection_name="hsn_subheadings",
        embedding_function=embedding,
        persist_directory=persist_directory,
    )
