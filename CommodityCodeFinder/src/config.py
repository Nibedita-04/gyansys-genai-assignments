# src/config.py

import os
from dotenv import load_dotenv

load_dotenv()


class settings:
    AZURE_OPENAI_ENDPOINT = os.getenv("OPENAI_API_ENDPOINT")
    AZURE_OPENAI_KEY = os.getenv("OPENAI_API_KEY")
    AZURE_API_VERSION = os.getenv("OPENAI_API_VERSION")
    AZURE_EMBEDDING_DEPLOYMENT = os.getenv("deployment")
    AZURE_CHAT_DEPLOYMENT = os.getenv("DEPLOYMENT_NAME")
