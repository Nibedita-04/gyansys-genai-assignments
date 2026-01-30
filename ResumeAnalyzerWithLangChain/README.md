# Resume Skill Extractor

An AI-powered resume parsing system that extracts structured skill data using Large Language Models (LLMs), Pydantic-based schema enforcement, and output parsing. The project supports both batch resume processing and an interactive Streamlit web interface.

# Project Overview

This tool automates the extraction of skills and relevant resume fields while ensuring clean, structured, and validated outputs. It is designed as a scalable foundation for advanced resume analytics, matching, and recruitment intelligence systems.

The extraction pipeline ensures that only meaningful and non-empty fields are returned, improving readability and downstream usability.

# System Workflow
Batch Mode (main.py)

- Loads resumes from a folder in batches (currently limited to 5 resumes per run)

- Sends resume text to an LLM using a structured prompt through a LangChain pipeline

- Uses a Pydantic schema to define and enforce expected extraction fields

- Parses and validates model outputs with an output parser

- Displays structured extraction results in the terminal

- Filters out empty fields to maintain clean outputs

![alt text](image.png)

# Streamlit Web Application

- Allows users to upload a resume via a browser interface

- Processes resumes using the same extraction pipeline

- Displays extracted skills and structured fields instantly

- Automatically removes empty or irrelevant fields from results

# Key Features

- LLM-driven resume skill extraction

- Pydantic-based schema validation for structured outputs

- LangChain-powered processing pipeline

- Batch resume ingestion and processing

- Interactive Streamlit front-end

- Clean output formatting with empty-field filtering

- Modular, extendable project architecture

# Tech Stack

Python

LangChain

Pydantic

Streamlit

Large Language Model API (OpenAI/Groq/Compatible APIs)

Usage
Run Batch Processing
python main.py


Ensure resumes are placed inside the configured input folder.

Run Streamlit App
streamlit run app.py


Upload a resume via the UI to extract skills interactively.

Output Format

Results are returned as structured JSON-like objects containing only non-empty extracted fields.

Example:

{
  "technical_skills": ["Python", "SQL", "Machine Learning"],
  "tools": ["Git", "Docker"],
  "soft_skills": ["Communication", "Problem Solving"]
}

# Future Roadmap

- Database integration for storing parsed resumes

- Resume-to-job matching and ranking algorithms

- Skill gap analysis and candidate profiling

- Scalable multi-user API service

- Analytics dashboard for recruiters and HR teams

# Purpose

This project serves as a base pipeline for building intelligent hiring, talent screening, and resume matching platforms.