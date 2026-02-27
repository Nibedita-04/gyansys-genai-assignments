from collections import defaultdict
import numpy as np
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer, util
from src.embeddings.embedder import Embedder
from src.vector_store.chroma_store import ChromaStore
from src.matching.gap_analyzer import gap_analysis


class ResumeMatcher:
    def __init__(self):
        self.embedder = Embedder()
        self.chroma = ChromaStore()
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    # Group chunks by section
    def group_sections(self, chunks: List[Tuple[str, Dict]]) -> Dict[str, List[str]]:
        section_map = defaultdict(list)
        for text, meta in chunks:
            section = meta.get("section", "general")
            section_map[section].append(text)
        return section_map

    # Compute section-wise cosine similarity
    def compute_section_similarity(
        self, resume_sections: Dict[str, List[str]], jd_sections: Dict[str, List[str]]
    ) -> Dict[str, float]:
        section_scores = {}
        for section in jd_sections:
            if section in resume_sections:
                jd_text = " ".join(jd_sections[section])
                resume_text = " ".join(resume_sections[section])
                if jd_text.strip() and resume_text.strip():
                    jd_emb = self.model.encode(jd_text, convert_to_tensor=True)
                    res_emb = self.model.encode(resume_text, convert_to_tensor=True)
                    score = util.cos_sim(jd_emb, res_emb).item()
                    section_scores[section] = round(score, 4)
        return section_scores

    # Main matching function
    def match_resume(self, jd_text: str, top_k: int = 10) -> List[Dict]:
        print("\nEmbedding JD...")
        jd_embedding = self.embedder.embed_texts([jd_text])[0]

        print("Querying resume chunks from ChromaDB...")
        results = self.chroma.resume_collection.query(
            query_embeddings=[jd_embedding],   
            n_results=200                      
        )

        if not results or "documents" not in results or not results["documents"]:
            print("No results found in ChromaDB")
            return []

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]

        # Group resume chunks by resume_id
        resume_chunks = defaultdict(list)
        for doc, meta in zip(documents, metadatas):
            resume_id = meta.get("doc_id")
            if resume_id:
                resume_chunks[resume_id].append((doc, meta))

        if not resume_chunks:
            print("No resume chunks grouped.")
            return []

        # Compute scores for each resume
        ranked_resumes = []
        jd_sections = {"general": [jd_text]}

        for resume_id, chunks in resume_chunks.items():
            resume_sections = self.group_sections(chunks)
            section_scores = self.compute_section_similarity(resume_sections, jd_sections)

            avg_score = (
                float(np.mean(list(section_scores.values())))
                if section_scores else 0.0
            )

            # Combine full text for gap analysis
            resume_text = " ".join([c[0] for c in chunks])
            gaps = gap_analysis(resume_text, jd_text)

            ranked_resumes.append({
                "resume_id": resume_id,
                "score": round(avg_score, 4),
                "section_scores": section_scores,
                "gap_analysis": gaps,
                "full_text": resume_text
            })

        # Sort by score
        ranked_resumes.sort(key=lambda x: x["score"], reverse=True)

        return ranked_resumes[:top_k]



