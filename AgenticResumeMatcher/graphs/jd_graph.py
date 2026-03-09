from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, END
import chromadb
from config import *
from utils import *
from schemas import JDSchema
import re


# JD's State Object that flows through the LangGraph workflow
# Stores all intermediate and final JD processing data
class JDState(TypedDict, total = False):
    jd_path: str
    jd_hash: str
    parsed_text: str
    structured: Dict[str, Any]
    embedding: Any
    cached: bool
    results: Any
    reranked_results: Any


# Check whether the JD has already been processed
# If hash exists in cache, loads structured data and embedding
# Otherwise marks JD as new
def cache_check_node(state):
    jd_path = state["jd_path"]

    with open(jd_path, "rb") as f:
        jd_hash = hashlib.sha256(f.read()).hexdigest()

    structured_cache = load_cache(JD_JSON)
    embedding_cache = load_embedding_cache(EMBEDDING_JD_JSON)

    if jd_hash in structured_cache and jd_hash in embedding_cache:
        print("Using cached JD")

        cached_data = structured_cache[jd_hash]

        return {
            "jd_hash": jd_hash,
            "parsed_text": cached_data["parsed_text"],
            "structured": cached_data["structured"],
            "embedding": embedding_cache[jd_hash],
            "cached": True
        }

    print("New JD detected")

    return {
        "jd_hash": jd_hash,
        "cached": False
    }


# Parses the JD document into raw text.
# Skips execution if JD was loaded from cache.
def parse_node(state):
    if state.get("cached"):
        return {}
    return {"parsed_text": parse_document(state["jd_path"])}


# Uses LLM to convert parsed JD text into structured schema format.
# Skips execution if JD was loaded from cache.
def structure_node(state):
    if state.get("cached"):
        return {}

    llm = get_llm()
    structured = llm.with_structured_output(JDSchema).invoke(
        state["parsed_text"]
    )
    return {"structured": structured.model_dump()}


# Generates embedding vector fro the JD summary.
# Skips execution if JD was loaded from cache.
def embed_node(state):
    if state.get("cached"):
        return {}

    embeddings = get_embeddings()
    vector = embeddings.embed_query(state["structured"]["summary"])

    return {"embedding": vector}


# Saves structured JD data and embedidng into separate caches.
# Skips execution if JD was loaded from cache.
def save_cache_node(state):
    if state.get("cached"):
        return {}

    structured_cache = load_cache(JD_JSON)
    embedding_cache = load_embedding_cache(EMBEDDING_JD_JSON)

    structured_cache[state["jd_hash"]] = {
        "parsed_text": state["parsed_text"],
        "structured": state["structured"],
    }
    embedding_cache[state["jd_hash"]] = state["embedding"]

    save_cache(JD_JSON,structured_cache)
    save_embedding_cache(EMBEDDING_JD_JSON, embedding_cache)

    return {}

# Queries ChromaDB to retrieve top resume matches using JD embedding and optional experience filtering.
def search_node(state):
    client = chromadb.PersistentClient(path="vector_db")
    collection = client.get_or_create_collection(CHROMA_COLLECTION)
    print("Total resumes in DB:", collection.count())
    structured = state["structured"]
    jd_summary = structured["summary"]
    jd_exp = structured.get("required_experience")
    jd_vector = state["embedding"]

    where_clause = None

    if jd_exp is not None:
        # Soft tolerance
        tolerance = max(1, jd_exp * 0.2)
        min_exp = jd_exp - tolerance
        max_exp = jd_exp + tolerance

        where_clause = {
            "$and": [
                {"experience": {"$gte": min_exp}},
                {"experience": {"$lte": max_exp}}
            ]
        }

    results = collection.query(
        query_embeddings=[jd_vector],
        n_results=5,
        where=where_clause
    )

    return {"results": results}


# Normalizes text bt removing special characters and converting to lowercase.
def normalize(text):
    return re.sub(r'[^a-z0-9 ]', '', text.lower())


# Converts text into a set of tokens for comaprision.
def token_set(text):
    return set(normalize(text).split())


# Computes similarity between one required skill and candidate skills using token overlap scoring.
def skill_similarity(req_skill, candidate_skills):
    req_tokens = token_set(req_skill)
    best_score = 0

    for cand in candidate_skills:
        cand_tokens = token_set(cand)

        if not req_tokens or not cand_tokens:
            continue

        intersection = req_tokens & cand_tokens
        union = req_tokens | cand_tokens

        score = len(intersection) / len(union)
        best_score = max(best_score, score)

    return best_score


# Re-ranks search results using semantic similarity, experience alignment, skill match score, and penalties.
def rerank_node(state):
    from config import RERANK_WEIGHTS

    results = state["results"]
    structured = state["structured"]

    jd_required_exp = structured.get("required_experience", 0)
    jd_skills = set(skill.lower() for skill in structured.get("skills", []))

    ids = results.get("ids", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    if not ids:
        return {"reranked_results": results}

    scored_candidates = []

    for i in range(len(ids)):

        # 1. Semantic Similarity Score
        semantic_score = max(0, 1 - distances[i])

        # 2. Experience Alignment Score
        candidate_exp = metadatas[i].get("experience", 0)

        if jd_required_exp > 0:
            exp_ratio = candidate_exp / jd_required_exp

            # Ideal range: 0.8 – 1.3
            if 0.8 <= exp_ratio <= 1.3:
                experience_score = 1
            elif exp_ratio < 0.8:
                experience_score = exp_ratio
            else:
                # Slight dampening for overqualification
                experience_score = 1 - ((exp_ratio - 1.3) * 0.2)
                experience_score = max(0.7, experience_score)
        else:
            experience_score = 1

        # 3. Skill Match Score
        candidate_skills = metadatas[i].get("skills", [])

        if jd_skills:
            scores = []
            for jd_skill in jd_skills:
                score = skill_similarity(jd_skill, candidate_skills)
                scores.append(score)

            skill_score = sum(scores) / len(scores)
        else:
            skill_score = 1

        # 4. Underqualification Penalty
        if jd_required_exp > 0 and candidate_exp < jd_required_exp:
            gap_ratio = (jd_required_exp - candidate_exp) / jd_required_exp
            underqualification_penalty = gap_ratio
        else:
            underqualification_penalty = 0

        # 5. Final weighted Score
        final_score = (
            RERANK_WEIGHTS["semantic"] * semantic_score +
            RERANK_WEIGHTS["experience"] * experience_score +
            RERANK_WEIGHTS["skills"] * skill_score -
            RERANK_WEIGHTS["underqualification_penalty"] * underqualification_penalty
        )

        scored_candidates.append({
            "id": ids[i],
            "document": documents[i],
            "metadata": metadatas[i],
            "semantic_score": semantic_score,
            "experience_score": experience_score,
            "skill_score": skill_score,
            "underqualification_penalty": underqualification_penalty,
            "final_score": final_score
        })

    scored_candidates.sort(
        key=lambda x: x["final_score"],
        reverse=True
    )

    return {"reranked_results": scored_candidates}


# Builds and connects all nodes into a LangGraph workflow.
# Defines execution order and conditional routing.
def build_jd_graph():
    workflow = StateGraph(JDState)

    workflow.add_node("cache_check", cache_check_node)
    workflow.add_node("parse", parse_node)
    workflow.add_node("structure", structure_node)
    workflow.add_node("embed", embed_node)
    workflow.add_node("save_cache", save_cache_node)
    workflow.add_node("search", search_node)
    workflow.add_node("rerank", rerank_node)

    workflow.set_entry_point("cache_check")

    workflow.add_edge("parse", "structure")
    workflow.add_edge("structure", "embed")
    workflow.add_edge("embed", "save_cache")
    workflow.add_edge("save_cache", "search")

    def route_after_cache(state):
        if state.get("cached"):
            return "search"
        return "parse"
    
    workflow.add_conditional_edges(
        "cache_check",
        route_after_cache,
        {
            "parse": "parse",
            "search": "search"
        }
    )

    workflow.add_edge("search", "rerank")
    workflow.add_edge("rerank", END)

    return workflow.compile()
    