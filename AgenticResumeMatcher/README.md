# Agentic Resume Matcher

An **AI-powered resume matching system** that automatically ingests resumes, extracts structured candidate information, stores embeddings in a vector database, and ranks candidates against a Job Description (JD) using a hybrid scoring approach.

This project leverages **LLMs, vector search, and graph-based orchestration** to create an intelligent pipeline for resume parsing and candidate ranking.

---

# Overview

Recruiters often need to manually screen hundreds of resumes to identify suitable candidates for a job role. This project automates the process by:

1. Parsing resumes and extracting structured information using an LLM.
2. Generating vector embeddings for semantic search and storing metadata for metadata filtering before semantic search.
3. Storing candidate profiles in a vector database.
4. Matching candidates against a job description.
5. Ranking candidates using a hybrid scoring system.

The system is built using **LangGraph workflows**, allowing modular, scalable orchestration of resume ingestion and job description analysis.

---

# Features

* Automated Resume Ingestion
* LLM-based Resume Parsing
* Structured Data Extraction (skills, experience, summary)
* Vector Embedding Generation
* Metadata Filtering for Experience
* ChromaDB Vector Database Storage
* Job Description Semantic Matching
* Hybrid Candidate Ranking System
* Resume Deduplication using Hashing
* Modular LangGraph Pipeline Architecture
* Optional Streamlit UI for interactive usage

---

# System Architecture

The project is composed of two primary pipelines orchestrated using **LangGraph**.

### 1. Resume Ingestion Pipeline

Processes resumes and stores candidate profiles.

Steps:

1. Generate hash for resume file
2. Check if resume already processed
3. Parse document text
4. Extract structured candidate information using LLM
5. Store structured data in JSON
6. Generate embeddings
7. Store vectors in ChromaDB

```
Resume → Hash → Cache Check → Parse → Structure → Store → Embed → Vector DB
```

---

### 2. Job Description Matching Pipeline

Matches a job description with stored resumes.

Steps:

1. Parse job description
2. Extract structured JD information
3. Generate embedding
4. Query vector database
5. Retrieve candidate resumes
6. Apply reranking based on multiple scoring factors

```
JD → Parse → Structure → Embed → Vector Search → Rerank → Results
```

---

# Ranking Methodology

Candidates are ranked using a hybrid scoring model combining multiple factors.

### Semantic Score

Measures vector similarity between the job description and candidate resume.

### Skill Score

Measures overlap between required skills and candidate skills.

### Experience Score

Compares candidate years of experience with job requirements.

### Underqualification Penalty

Applied when a candidate has significantly less experience than required.

### Final Score

```
Final Score =
    (Semantic Weight × Semantic Score)
  + (Skill Weight × Skill Score)
  + (Experience Weight × Experience Score)
  - Penalty
```

This approach ensures both **semantic relevance and structured criteria** influence the final ranking.

---

# Project Structure

```
project/
│
├── app.py                 # Streamlit application
├── main.py                # CLI orchestration
│
├── graphs/
│    ├── resume_graph.py   # Resume ingestion LangGraph pipeline
|    ├── jd_graph.py       # Job description processing pipeline
|    └── master_graph.py   # Orchestrates resume & JD flows
|
├── schemas.py             # Pydantic schemas for structured extraction
├── utils.py               # Utility functions
├── config.py              # Configuration settings
│
├── vector_db/             # ChromaDB storage (generated)
│
├── data/
│   ├── resumes/           # Resume documents
│   └── jds/               # Job descriptions
│
└── README.md
```

---

# Installation

### Install dependencies

```
pip install -r requirements.txt
```

---

# Running the Project

### Run via CLI

```
python main.py
```

The system will:

1. Check for new resumes
2. Process and store embeddings
3. Ask for a Job Description
4. Display ranked candidates

---

### Run Streamlit UI

```
streamlit run app.py
```

Open the provided URL in your browser.

The UI allows:

* Resume ingestion
* Job description upload
* Candidate ranking visualization

---

# Example Output

```
TOP MATCHING CANDIDATES

Rank #1
Final Score: 0.547
Experience: 9 years
Skills: SAP SD, Pricing, Sales Configuration

Resume Preview:
Experienced SAP SD Consultant with expertise in implementation,
testing, rollout, and sales document configuration.
```

---

# Technologies Used

* Python
* LangGraph
* LangChain
* AzureOpenAI 
* ChromaDB
* Streamlit
* Pydantic
* Vector Embeddings
* Semantic Search

---

# Key Design Decisions

### Graph-Based Orchestration

LangGraph enables modular pipelines where each processing step is represented as a node.

### Resume Deduplication

Each resume is hashed to avoid duplicate ingestion.

### Structured Extraction with LLM

Resumes are converted into structured candidate profiles using schema-guided extraction.

### Hybrid Ranking

Combines semantic similarity with structured filters for better candidate ranking.

---

# Future Improvements

* Batch embedding optimization
* Candidate skill normalization
* Resume highlighting based on JD match
* Recruiter dashboard analytics
* Support for multiple vector databases
* Deployment with Docker
* API endpoints for ATS integration

---


