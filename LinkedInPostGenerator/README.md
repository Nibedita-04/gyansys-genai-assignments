Here’s an **updated README.md** that reflects your **current system**: ChromaDB memory, step-back prompting, session modes (linked/standalone), typo handling, and multi-user personalization.

I’ve kept it **GitHub-polished, professional, structured, and emoji-free**.

---

# LinkedIn Post Generator (AI-Powered)

## Overview

The LinkedIn Post Generator is an AI-powered application that helps users create high-quality, personalized LinkedIn posts based on their role, intent, and post idea. The system uses Large Language Models (LLMs), LangChain, and vector-based memory (ChromaDB) to generate structured, engaging, and context-aware posts through a multi-step reasoning pipeline.

The project supports **multi-user personalization**, **memory-based post continuity**, **typo-aware idea refinement**, and **session-based post generation** (linked or standalone).

It is designed for students, job seekers, professionals, and content creators to enhance LinkedIn presence and personal branding.

---

## Problem Statement

Many professionals struggle to write effective LinkedIn posts due to time constraints, lack of writing confidence, or uncertainty about platform tone and engagement strategies. Additionally, most AI post generators lack personalization, memory, and narrative continuity across posts.

This project solves these challenges by:

* Automating LinkedIn post creation
* Maintaining user-specific writing style
* Linking posts across sessions when desired
* Correcting typos and refining ideas intelligently
* Supporting scalable memory using vector databases

---

## Key Features

* Role-based LinkedIn post generation
* Intent detection (educational, storytelling, hiring, personal branding)
* Step-back prompting for typo correction and idea refinement
* Chain-of-Thought (CoT) reasoning for structured generation
* Multi-step LangChain pipeline (role → intent → planning → generation)
* User-specific memory stored in ChromaDB
* Hybrid memory support (personal + global)
* Session modes:

  * Linked (uses past memory)
  * Standalone (ignores memory)
* Emoji and hashtag count control
* Writing style adaptation based on historical posts
* Modular, scalable, and maintainable architecture

---

## How It Works

The system follows a structured AI workflow:

1. User authentication and memory initialization
2. Step-back chain refines and corrects the post idea
3. Role chain interprets user background
4. Intent chain determines post purpose
5. Planner chain structures the post outline
6. Memory retriever fetches relevant past posts (if linked mode)
7. Generator chain produces the final LinkedIn post
8. Memory store saves post embeddings into ChromaDB

This multi-stage approach improves coherence, personalization, and post quality compared to single-prompt AI systems.

---

## Session Modes

| Mode       | Behavior                                        |
| ---------- | ----------------------------------------------- |
| Linked     | Uses past memory to maintain continuity         |
| Standalone | Generates a fresh post without memory influence |

---

## Memory System Architecture

### Memory Types

* User-specific memory (ChromaDB collections per user)
* Global shared memory (optional)
* Style memory for tone personalization

### Stored Data

* User role
* Post idea (original + refined)
* Generated post
* Timestamp
* Vector embeddings for semantic retrieval

### Benefits

* Context-aware post linking
* Career narrative continuity
* Semantic recall instead of keyword matching
* Scalable multi-user memory storage

---

## Project Workflow

![alt text](<Screenshot 2026-02-05 132015.png>)

---

## Project Structure

```
LINKEDINPOSTGENERATOR/

chains/
  generator_chain.py       Final post generation
  intent_chain.py          Post intent detection
  planner_chain.py         Post structure planning
  role_chain.py            Role understanding
  stepback_chain.py        Typo correction and idea refinement

config/
  llm.py                   LLM configuration

memory/
  db_client.py             ChromaDB client initialization
  embedding_model.py       SentenceTransformer embeddings
  memory_store.py          Store memory vectors
  memory_retriever.py      Retrieve relevant memory
  user_manager.py          User collection manager
  conversational_memory.py Legacy JSON memory (optional)

prompts/
  generator_prompt.py      Final writing instructions
  intent_prompt.py         Intent classification prompt
  planner_prompt.py        Post planning prompt
  role_prompt.py           Role understanding prompt
  stepback_prompt.py       Step-back refinement prompt

storage/
  chroma_db/               Persistent vector memory storage

main.py                    Core pipeline runner
app.py                     Optional UI interface
.env                       API keys and environment config
requirements.txt           Dependencies
README.md                  Project documentation
```

---

## Technology Stack

* Python
* LangChain
* Large Language Models (Groq / OpenAI / Local LLMs)
* ChromaDB (Vector Database)
* Sentence Transformers (Embeddings)
* Prompt Engineering
* Streamlit (Optional UI)
* JSON (Legacy memory storage)

---

## Installation

Clone the repository:

```bash
git clone https://github.com/your-username/linkedin-post-generator.git
cd linkedin-post-generator
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file and add your API keys:

```
OPENAI_API_KEY=your_key_here
```

---

## Running the Project

Run via terminal:

```bash
python main.py
```

If using Streamlit:

```bash
streamlit run app.py
```

---

## Example Capabilities

* Typo-aware idea correction (e.g., "langgeaph" → "LangGraph")
* Multi-post narrative continuity
* Memory-based personalization
* Skill progression storytelling
* Emoji and hashtag constraint control
* Research-ready modular AI pipeline

---

## Future Enhancements

* Skill graph and career trajectory tracking
* Memory weighting and temporal decay
* Explainable memory retrieval debugging
* Multi-platform post generation (LinkedIn, X, Medium)
* Research-grade analytics dashboard
* RAG-based career storytelling engine
