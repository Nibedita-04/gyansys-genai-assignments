# document_parser.py
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredWordDocumentLoader
import os
import re
from nltk.corpus import stopwords
import nltk

EXTENSION_TO_LOADER = {
    ".pdf": PyPDFLoader,
    ".docx": UnstructuredWordDocumentLoader,
    ".txt": TextLoader
}

# Parses one file at a time -> this function is used inside the parse_folder()
from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from pathlib import Path
from typing import Dict, List

def parse_file(file_path: str):
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext == ".docx":
        loader = Docx2txtLoader(file_path)
    elif ext == ".txt":
        loader = TextLoader(file_path, encoding="utf-8")
    else:
        print(f"Unsupported file type: {file_path}")
        return None

    docs = loader.load()
    # Extract text from Document objects
    text = " ".join([doc.page_content for doc in docs])
    return text

def parse_folder(folder_path: str) -> Dict[str, str]:
    folder = Path(folder_path)
    parsed_docs = {}

    for file_path in folder.iterdir():
        if file_path.suffix.lower() in [".pdf", ".docx", ".txt"]:
            text = parse_file(str(file_path))
            if text:
                parsed_docs[file_path.name] = text

    return parsed_docs

# Download stopwords once
nltk.download('stopwords')
STOPWORDS = set(stopwords.words('english'))

def clean_text(text: str, remove_stopwords=True):
    """
    Clean text for chunking:
    - Normalize whitespace
    - Remove special characters
    - Optionally remove stopwords
    """
    # Lowercase
    text = text.lower()

    # Remove special characters except spaces
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # Normalize whitespace
    text = " ".join(text.split())

    if remove_stopwords:
        words = text.split()
        words = [w for w in words if w not in STOPWORDS]
        text = " ".join(words)

    return text