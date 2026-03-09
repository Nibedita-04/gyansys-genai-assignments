import os
import json
import hashlib
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
)
import pickle

# File Hash
def generate_hash(file_path):
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()
    
# JSON Manager
def load_json(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

def append_json(path, data):
    existing = load_json(path)
    existing.append(data)
    with open(path, "w") as f:
        json.dump(existing, f, indent=4)

def load_cache(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def save_cache(path,cache):
    with open(path, "w") as f:
        json.dump(cache, f, indent=4)

# Resume/JD Parser
def parse_document(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext == ".docx":
        loader = Docx2txtLoader(file_path)
    elif ext == ".txt":
        loader = TextLoader(file_path)
    else:
        pass

    docs = loader.load()
    return "\n".join([d.page_content for d in docs])

# Print the result retrieved from thr ChromaDB
def pretty_print_results(results):
    if not results:
        print("\nNo matching resumes found.\n")
        return

    print("\n" + "=" * 80)
    print("TOP MATCHING CANDIDATES")
    print("=" * 80)

    for idx, candidate in enumerate(results, start=1):
        print(f"\nRank #{idx}")
        print("-" * 80)
        print(f"Candidate ID       : {candidate['id']}")
        print(f"Final Score        : {round(candidate['final_score'], 3)}")
        print(f"Semantic Score     : {candidate['semantic_score']}")
        print(f"Experience Score   : {candidate['experience_score']}")
        print(f"Skill Score        : {candidate['skill_score']}")
        print(f"Penalty            : {round(candidate['underqualification_penalty'], 3)}")
        print(f"Experience (yrs)   : {candidate['metadata'].get('experience', 'N/A')}")
        print(f"Skills             : {candidate['metadata'].get('skills', 'N/A')}")
        print("\nResume Preview:")
        print(candidate['document'][:400])  # limit preview
        print("\n" + "=" * 80)

def load_embedding_cache(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return pickle.load(f)
    return {}

def save_embedding_cache(file_path, cache):
    with open(file_path, "wb") as f:
        pickle.dump(cache, f)