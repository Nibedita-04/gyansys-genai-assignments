import os
import json
from typing import Dict, List
from src.ingestion.document_parser import parse_folder, clean_text  # combined parser
from src.chunking.section_chunker import section_chunk_resume  # keep for resumes only
from src.embeddings.embedder import Embedder
from src.vector_store.chroma_store import ChromaStore
from src.matching.matcher import ResumeMatcher
from src.retrieval.reranker import rerank_resumes
from dotenv import load_dotenv

load_dotenv()



# CONFIG
RESUME_FOLDER = "data/resumes/"
JD_FOLDER = "data/job_descriptions/"
OUTPUT_FOLDER = "data/processed_chunks/"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

PARSED_RESUMES_PATH = os.path.join(OUTPUT_FOLDER, "parsed_resumes.json")
PARSED_JDS_PATH = os.path.join(OUTPUT_FOLDER, "parsed_jds.json")
CHUNKED_RESUMES_PATH = os.path.join(OUTPUT_FOLDER, "chunked_resumes.json")
CHUNKED_JDS_PATH = os.path.join(OUTPUT_FOLDER, "chunked_jds.json")
PROCESSED_TRACKER = os.path.join(OUTPUT_FOLDER, "processed_files.json")



# Load processed tracker
if os.path.exists(PROCESSED_TRACKER):
    with open(PROCESSED_TRACKER, "r") as f:
        processed_files = json.load(f)
else:
    processed_files = {"resumes": [], "jds": []}



# HELPER FUNCTIONS
def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def embed_and_store(chunked_data, doc_type="resume"):
    embedder = Embedder()
    chroma = ChromaStore()
    collection = chroma.resume_collection if doc_type == "resume" else chroma.jd_collection

    texts, metadatas, ids = [], [], []

    for doc_id, chunks in chunked_data.items():
        for i, chunk_obj in enumerate(chunks):
            text = chunk_obj.get("text", "") if isinstance(chunk_obj, dict) else chunk_obj
            metadata = chunk_obj.get("metadata", {"doc_id": doc_id, "type": doc_type}) if isinstance(chunk_obj, dict) else {"doc_id": doc_id, "type": doc_type}

            texts.append(text)
            metadatas.append(metadata)
            ids.append(f"{doc_id}_chunk_{i}")

    if not texts:
        print(f"No new {doc_type} chunks to store.")
        return

    print(f"\nEmbedding {len(texts)} new {doc_type} chunks...")
    embeddings = embedder.embed_texts(texts)
    chroma._store_chunks(collection, embeddings, texts, metadatas, ids)
    print(f"Stored {len(texts)} new {doc_type} chunks in ChromaDB.")



# Simple recursive overlapping chunking for JDs
def chunk_text_recursive(text: str, chunk_size=500, overlap=100) -> List[Dict]:
    """
    Split a long text into overlapping chunks of chunk_size words.
    """
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        chunk_words = words[start:start+chunk_size]
        if not chunk_words:
            break
        chunks.append({"text": " ".join(chunk_words), "metadata": {}})
        start += chunk_size - overlap
    return chunks



# PARSE & CHUNK RESUMES (Incremental)
all_resumes = [f for f in os.listdir(RESUME_FOLDER) if f.endswith(".docx")]
new_resumes = [f for f in all_resumes if f not in processed_files["resumes"]]

if new_resumes:
    # print(f"\nParsing new resumes: {new_resumes}")
    parsed_resumes = parse_folder(RESUME_FOLDER)
    parsed_resumes = {k: clean_text(v) for k, v in parsed_resumes.items()}

    # Save parsed resumes
    if os.path.exists(PARSED_RESUMES_PATH):
        with open(PARSED_RESUMES_PATH, "r", encoding="utf-8") as f:
            existing_resumes = json.load(f)
    else:
        existing_resumes = {}
    existing_resumes.update(parsed_resumes)
    save_json(PARSED_RESUMES_PATH, existing_resumes)

    # Chunk resumes using section_chunk_resume
    chunked_resumes = {}
    for doc_id, text in parsed_resumes.items():
        chunked_resumes[doc_id] = section_chunk_resume(text, resume_metadata={"doc_id": doc_id})

    # Save chunked resumes
    if os.path.exists(CHUNKED_RESUMES_PATH):
        with open(CHUNKED_RESUMES_PATH, "r", encoding="utf-8") as f:
            existing_chunks = json.load(f)
    else:
        existing_chunks = {}
    existing_chunks.update(chunked_resumes)
    save_json(CHUNKED_RESUMES_PATH, existing_chunks)
    embed_and_store(chunked_resumes, "resume")

    processed_files["resumes"].extend(new_resumes)
    save_json(PROCESSED_TRACKER, processed_files)
else:
    print("\nNo new resumes to process.")



# PARSE & CHUNK JDs (Incremental)
all_jds = [f for f in os.listdir(JD_FOLDER) if f.endswith(".docx")]
new_jds = [f for f in all_jds if f not in processed_files["jds"]]

if new_jds:
    print(f"\nParsing new JDs: {new_jds}")
    parsed_jds = parse_folder(JD_FOLDER)
    parsed_jds = {k: clean_text(v) for k, v in parsed_jds.items()}

    # Save parsed JDs
    if os.path.exists(PARSED_JDS_PATH):
        with open(PARSED_JDS_PATH, "r", encoding="utf-8") as f:
            existing_jds = json.load(f)
    else:
        existing_jds = {}
    existing_jds.update(parsed_jds)
    save_json(PARSED_JDS_PATH, existing_jds)

    # Chunk JDs using simple recursive chunking
    chunked_jds = {}
    for doc_id, text in parsed_jds.items():
        print("\nProcessing JD:", doc_id)
        print("JD TEXT LENGTH:", len(text))
        chunks = chunk_text_recursive(text)
        print("NUM CHUNKS:", len(chunks))

        # Add metadata for each chunk
        for idx, chunk in enumerate(chunks):
            chunk["metadata"] = {"doc_id": doc_id, "chunk_index": idx}

        chunked_jds[doc_id] = chunks

    # Save chunked JDs
    if os.path.exists(CHUNKED_JDS_PATH):
        with open(CHUNKED_JDS_PATH, "r", encoding="utf-8") as f:
            existing_chunks = json.load(f)
    else:
        existing_chunks = {}
    existing_chunks.update(chunked_jds)
    save_json(CHUNKED_JDS_PATH, existing_chunks)
    embed_and_store(chunked_jds, "jd")
    store = ChromaStore()
    print("JD collection count:", store.jd_collection.count())

    processed_files["jds"].extend(new_jds)
    save_json(PROCESSED_TRACKER, processed_files)
else:
    print("\nNo new JDs to process.")



# RESUME MATCHING & RERANKING
matcher = ResumeMatcher()

# Pick a sample JD
with open(PARSED_JDS_PATH, "r", encoding="utf-8") as f:
    all_jds = json.load(f)
sample_jd_id = list(all_jds.keys())[5]  # pick first JD
sample_jd_text = all_jds[sample_jd_id]

top_k = 20
retrieved_resumes = matcher.match_resume(sample_jd_text, top_k)

# Rerank resumes
reranked = rerank_resumes(sample_jd_text, retrieved_resumes)

# Display top N
top_n = int(input("Enter how many top resumes you want to see: "))
final_results = reranked[:top_n]

print("\n--- JD CONTENT ---")
print(sample_jd_text)

store = ChromaStore()
print("Resume collection count:", store.resume_collection.count())

print("\n--- TOP RESUMES ---")
for i, r in enumerate(final_results, 1):
    print(f"\nRank {i}")
    print("Resume ID:", r["resume_id"])
    print("Final Score:", round(r["final_score"], 4))
    print("Raw Score:", round(r["raw_score"], 4))

    print("\nComponent Scores:")
    for k, v in r["component_scores"].items():
        print(f"  {k}: {round(v, 4)}")

    print("\nContribution %:")
    for k, v in r["contribution_percent"].items():
        print(f"  {k}: {v}%")