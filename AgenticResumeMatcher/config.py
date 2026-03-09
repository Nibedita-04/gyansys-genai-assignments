# config.py
import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

load_dotenv()

def get_llm():
    return AzureChatOpenAI(
        azure_deployment=os.getenv("DEPLOYMENT_NAME"),
        openai_api_version=os.getenv("OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("OPENAI_API_ENDPOINT"),
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0
    )

def get_embeddings():
    return AzureOpenAIEmbeddings(
        azure_deployment=os.getenv("deployment"),
        openai_api_version=os.getenv("api_version"),
        azure_endpoint=os.getenv("endpoint"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )

# Paths
RESUME_FOLDER = "data/resumes"
JD_FOLDER = "data/jds"
RESUME_JSON = "cache/summarized_resume.json"
LOG_FILE = "cache/processed_resumes.txt"
JD_JSON = "cache/summarized_jd.json"
CHROMA_COLLECTION = "resume_collection"
RERANK_WEIGHTS = {
    "semantic": 0.5,
    "experience": 0.25,
    "skills": 0.25,
    "underqualification_penalty": 0.4
}
EMBEDDING_JD_JSON = "cache/jd_embedding_cache.pkl"