import chromadb
from chromadb.config import Settings
from typing import List, Dict, Union

CHROMA_PATH = "data/chroma_db"

class ChromaStore:
    def __init__(self, path: str = CHROMA_PATH):
        # Persistent client
        self.client = chromadb.PersistentClient(
            path=CHROMA_PATH
        )

        # Create / load Collections
        self.resume_collection = self.client.get_or_create_collection("resume_chunks")
        self.jd_collection = self.client.get_or_create_collection("jd_chunks")

    # Generic store function
    def _store_chunks(
        self,
        collection,
        embeddings: List[List[float]],
        texts: List[Union[str, Dict]],
        metadatas: List[Dict],
        ids: List[str]
    ):
        if not texts:
            print("No chunks to store.")
            return

        safe_texts, safe_metadatas = [], []

        for i, t in enumerate(texts):
            if isinstance(t, dict):
                text = t.get("text", "")
                metadata = t.get("metadata", {})
            else:
                text = t
                metadata = metadatas[i] if i < len(metadatas) else {}
            safe_texts.append(text)
            safe_metadatas.append(metadata)

        # Remove duplicates
        existing = set(collection.get(ids=ids).get("ids", []))
        filtered = [
            (emb, txt, meta, _id)
            for emb, txt, meta, _id in zip(embeddings, safe_texts, safe_metadatas, ids)
            if _id not in existing
        ]

        if not filtered:
            print("No new chunks to store (all duplicates).")
            return

        embeddings, safe_texts, safe_metadatas, ids = zip(*filtered)
        collection.add(
            embeddings=list(embeddings),
            documents=list(safe_texts),
            metadatas=list(safe_metadatas),
            ids=list(ids)
        )

        print(f"Stored {len(ids)} chunks in {collection.name}")

    # Resume-specific methods
    def store_resume_chunks(
        self, embeddings: List[List[float]], texts: List[Union[str, Dict]], metadatas: List[Dict], ids: List[str]
    ):
        self._store_chunks(self.resume_collection, embeddings, texts, metadatas, ids)

    def query_resume(
        self, query_embeddings: List[List[float]], n_results: int = 10, where: Dict = None
    ):
        return self._query_collection(self.resume_collection, query_embeddings, n_results, where)
    
    # JD-specific methods
    def store_jd_chunks(
        self, embeddings: List[List[float]], texts: List[Union[str, Dict]], metadatas: List[Dict], ids: List[str]
    ):
        self._store_chunks(self.jd_collection, embeddings, texts, metadatas, ids)

    def query_jd(
        self, query_embeddings: List[List[float]], n_results: int = 10, where: Dict = None
    ):
        return self._query_collection(self.jd_collection, query_embeddings, n_results, where)

    # Generic query function
    def _query_collection(self, collection, query_embeddings: List[List[float]], n_results: int = 10, where: Dict = None):
        if collection is None:
            return {}
        return collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"]
        )

    # Reset a collection
    def reset_resume_collection(self):
        self._reset_collection(self.resume_collection)

    def reset_jd_collection(self):
        self._reset_collection(self.jd_collection)

    def _reset_collection(self, collection):
        if collection is None:
            print("Collection does not exist.")
            return
        self.client.delete_collection(collection.name)
        print(f"Reset collection: {collection.name}")
