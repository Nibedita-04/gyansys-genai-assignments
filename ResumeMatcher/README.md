# Resume Matcher

Resume Matcher takes a Job Description, generates embeddings, retrieves relevant resumes using vector similarity search, applies multi-signal scoring with dynamic LLM-based weighting, and produces an explainable ranked shortlist of candidates.

---

# Project Overview

This system performs intelligent resume ranking using:

* Vector similarity search (ChromaDB)
* Cross-encoder semantic scoring
* Skill alignment scoring
* Experience and stability scoring
* Dynamic global weight generation using an LLM
* Explainable reranking with contribution breakdown

The pipeline ensures that:

* Scores are normalized
* Weights adapt to the job description
* Each ranking decision is explainable
* Output is structured and recruiter-friendly

---

# System Workflow

Batch Mode (main.py – LangGraph Orchestrated)

* Accepts Job Description input
* Embeds the JD using a sentence transformer model
* Queries ChromaDB to retrieve top_k relevant resumes
* Computes multi-signal component scores:

  * Cross-encoder semantic score
  * Embedding similarity score
  * Skill match score
  * Experience alignment score
  * Stability score
  * Section alignment score
* Generates dynamic global scoring weights using an LLM (Pydantic validated output)
* Applies weighted reranking
* Normalizes final scores
* Calculates contribution percentage per signal
* Displays top N ranked resumes with explainability

Graph Execution Flow:

JD Input
→ Embed JD
→ Retrieve Resumes (ChromaDB)
→ Generate Dynamic Weights (LLM)
→ Score & Rerank
→ Output Ranked Results

---

# Key Features

* Vector-based resume retrieval using ChromaDB
* Cross-encoder semantic ranking
* Dynamic LLM-based weight generation (Pydantic enforced schema)
* Multi-signal scoring engine
* Score normalization and calibration
* Explainable ranking (component + contribution %)
* LangGraph-based orchestration
* Modular and extensible architecture
* Structured output ready for API integration

---

# Tech Stack

Python
LangChain
ChromaDB
Sentence Transformers (all-MiniLM-L6-v2)
Cross Encoder (ms-marco-MiniLM-L12-v2)
Pydantic
Large Language Model API (AzureOpenAI)

---

# Usage

Run Resume Matcher

```
python main.py
```

Steps:

1. Take Job Description.
2. Enter number of top resumes to display.
3. View ranked and explainable results in terminal.

Ensure:

* Resumes are already indexed in ChromaDB.
* Embedding and cross-encoder models are downloaded.

---

# Output Format

Results are returned as structured JSON-like objects containing:

* resume_id
* final_score
* raw_score
* component_scores
* weighted_contributions
* contribution_percent

Example:

```
{
  "resume_id": "candidate_12.docx",
  "final_score": 0.91,
  "component_scores": {
    "cross": 0.88,
    "embedding": 0.76,
    "skill": 0.65,
    "experience": 0.70,
    "stability": 0.60,
    "section": 0.72
  },
  "contribution_percent": {
    "cross": 42.3,
    "skill": 24.1,
    "experience": 18.2,
    "embedding": 9.4,
    "stability": 3.0,
    "section": 3.0
  }
}
```

This ensures full transparency in ranking decisions.

---

# Architecture

The system is built using a modular LangChain-based pipeline architecture, where each stage of processing is clearly separated:

* Job Description embedding
* Resume vector retrieval (ChromaDB)
* Cross-encoder semantic scoring
* Multi-signal component scoring
* Dynamic weight generation using LLM
* Weighted reranking and normalization

The architecture is designed to be:

* Modular and extensible
* Easy to refactor into agent or graph-based workflows
* Scalable for API integration
* Suitable for production deployment

# Future Roadmap

* Conditional routing (technical vs functional JD strategies)
* Mandatory skill penalty engine
* Recruiter-facing explanation summary generation
* REST API service with FastAPI
* Multi-agent evaluation (Technical Agent + HR Agent)
* Web-based dashboard for recruiters
* Resume analytics & candidate profiling
* Real-time streaming evaluation
* Distributed processing for large resume batches

---

# Purpose

This project serves as a foundation for building:

* Intelligent hiring platforms
* AI-powered resume ranking systems
* Talent screening automation tools
* Skill-gap analysis engines
* Enterprise-grade recruitment intelligence systems

It demonstrates how vector search, cross-encoder ranking, LLM-driven strategy generation, and explainable scoring can be combined into a robust AI hiring pipeline.

---

