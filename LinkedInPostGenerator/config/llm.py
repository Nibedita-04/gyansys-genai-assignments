import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_openai import AzureChatOpenAI

load_dotenv()

def get_llm():
    return ChatGroq(
        model = "llama-3.1-8b-instant",
        temperature = 0.7,
        groq_api_key = os.getenv("GROQ_API_KEY")
    )
    # return AzureChatOpenAI(
    #     azure_deployment=os.getenv("DEPLOYMENT_NAME"),
    #     azure_endpoint=os.getenv("OPENAI_API_ENDPOINT"),
    #     api_key=os.getenv("OPENAI_API_KEY"),
    #     api_version=os.getenv("OPENAI_API_VERSION"),
    #     temperature=0,
    #     max_retries=5,
    # )