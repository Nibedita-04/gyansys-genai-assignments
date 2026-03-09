from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, END
import os
import chromadb

from config import *
from utils import *
from schemas import ResumeSchema

# State
class ResumeState(TypedDict):
        file_path: str
        file_hash: str
        is_new: bool
        parsed_text: str
        structured: Dict[str, Any]

# Nodes
def hash_node(state): 
    return {"file_hash": generate_hash(state["file_path"])}

def check_cache_node(state):
      existing = load_json(RESUME_JSON)
      hashes = {r["file_hash"] for r in existing}
      return {"is_new": state["file_hash"] not in hashes}

def parse_node(state):
      return {"parsed_text": parse_document(state["file_path"])}

def structure_node(state):
      llm = get_llm()
      structured = llm.with_structured_output(ResumeSchema).invoke(
            state["parsed_text"]
      )
      return {"structured": structured.model_dump()}

def store_node(state):
      append_json(RESUME_JSON, {
            "file_hash": state["file_hash"],
            "data": state["structured"]
      })
      return {}

def embed_node(state):
      embeddings = get_embeddings()
      client = chromadb.PersistentClient(path="vector_db")
      collection = client.get_or_create_collection(CHROMA_COLLECTION)

      summary = state["structured"]["summary"]
      vector = embeddings.embed_query(summary)

      collection.add(
            ids=[state["file_hash"]],
            documents=[
                  state["structured"]["summary"] +
                  "\nSkills: " + ",".join(state["structured"]["skills"])
            ],
            embeddings = [vector],
            metadatas = [{
                  "experience": state["structured"]["total_years_experience"],
                  "skills": ",".join(state["structured"]["skills"]),
            }]
      )
      return {}

# Conditional
def route(state):
      return "process" if state["is_new"] else "skip"

# Build Graph
def build_resume_graph():
      workflow = StateGraph(ResumeState)

      workflow.add_node("hash", hash_node)
      workflow.add_node("check", check_cache_node)
      workflow.add_node("parse", parse_node)
      workflow.add_node("structure", structure_node)
      workflow.add_node("store", store_node)
      workflow.add_node("embed", embed_node)

      workflow.set_entry_point("hash")
      workflow.add_edge("hash", "check")

      workflow.add_conditional_edges(
            "check",
            route,
            {"process": "parse", "skip": END}
      )

      workflow.add_edge("parse", "structure")
      workflow.add_edge("structure", "store")
      workflow.add_edge("store", "embed")
      workflow.add_edge("embed", END)

      return workflow.compile()