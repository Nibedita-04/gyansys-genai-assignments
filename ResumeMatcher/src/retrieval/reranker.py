import os
from typing import List, Dict
import numpy as np
from sentence_transformers import CrossEncoder
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field, model_validator
import json

load_dotenv()

# Load Models / Clients

# Cross-encoder for ranking
reranker_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L12-v2")

# Azure Chat LLM client for skill extraction
client = AzureChatOpenAI(
    azure_deployment=os.getenv("DEPLOYMENT_NAME"),
    azure_endpoint=os.getenv("OPENAI_API_ENDPOINT"),
    api_key=os.getenv("OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION"),
    temperature=0,
    max_retries=5,
)

# LLM-based Skill Extraction
def extract_skills_llm(text: str) -> List[str]:
    prompt = f"""
    <TEXT>
    {text}
    </TEXT>
    Extract professional skills, tools, technologies, and frameworks from the text.
    Return ONLY a comma-separated list of skills. No explanations.
    """
    response = client.invoke(prompt)
    return [skill.strip() for skill in response.content.split(",") if skill.strip()]

def compute_stability_score(resume_text: str) -> float:
    prompt = f"""
    <RESUME TEXT>
    \"\"\"{resume_text}\"\"\"
    </RESUME TEXT>

    You are a resume analyzer. Given the following resume text, extract the following information.
    Parse the entire resume and identify all job entries with their start and end years. Calculate:

    1. total_experience_years: total number of years of work experience.
    2. average_tenure_per_job: average duration per job in years.

    Return the result in JSON format:
    {{
      "total_experience_years": ...,
      "average_tenure_per_job": ...
    }}
    """
    
    # Call LLM
    llm_response = client.invoke(prompt)
    
    # Parse JSON response
    try:
        data = json.loads(llm_response.content)
        avg_tenure = data.get("average_tenure_per_job", 0)
    except:
        # Fallback in case parsing fails
        avg_tenure = 1.5  # neutral value
    
    # Map average tenure to stability score
    if avg_tenure < 1.5:
        return 0.6
    elif avg_tenure < 2.5:
        return 0.8
    return 1.0


# Experience Relevance Boost
def compute_experience_relevance(jd_text: str, resume_text: str) -> float:
    jd_keywords = extract_skills_llm(jd_text)
    resume_lower = resume_text.lower()
    boost = sum(0.1 for kw in jd_keywords if kw.lower() in resume_lower)
    return min(boost, 0.3)

# Normalize Scores
def normalize_score(score: float, min_val: float, max_val: float) -> float:
    return (score - min_val) / (max_val - min_val + 1e-9)

# Default Weights (fallback)
DEFAULT_WEIGHTS = {
    "cross_weight": 0.7,
    "skill_weight": 0.2,
    "stability_weight": 0.1,
}

# Pydantic model for structured LLM output
class GlobalWeights(BaseModel):
    cross_weight: float = Field(..., ge=0)
    skill_weight: float = Field(..., ge=0)
    stability_weight: float = Field(..., ge=0)

    @model_validator(mode="after")
    def check_not_all_zero(self):
        total = sum(self.model_dump().values())
        if total == 0:
            raise ValueError("All weights cannot be zero")
        return self

# LLM Global weight Score
WEIGHT_CACHE = {}

def get_dynamic_global_weights(jd_text: str) -> dict:
    if jd_text in WEIGHT_CACHE:
        return WEIGHT_CACHE[jd_text]

    prompt = f"""
    <JOB_DESCRIPTION>
    {jd_text}
    </JOB_DESCRIPTION>

    You are an AI recruitment scoring strategist.

    Analyze the following Job Description and assign importance weights 
    to the resume scoring components below.

    <COMPONENTS>
    - cross_weight
    - skill_weight
    - stability_weight
    </COMPONENTS>

    <RULES>
    - All weights must be non-negative numbers.
    - Return structured output only.
    </RULES>
    """
    try:
        structured_llm = client.with_structured_output(GlobalWeights)
        weights_obj = structured_llm.invoke(prompt)
        weights = weights_obj.model_dump()
        total = sum(weights.values())
        weights = {k: v / total for k, v in weights.items()}
        WEIGHT_CACHE[jd_text] = weights
        print("Dynamic Weights:", weights)
        return weights
    except Exception:
        return DEFAULT_WEIGHTS

# Main Rerank Function
def rerank_resumes(jd_text: str, retrieved_resumes: List[Dict], debug: bool = False) -> List[Dict]:
    if not retrieved_resumes:
        return []

    # Cross-encoder scores
    pairs = [(jd_text, r.get("full_text", "")) for r in retrieved_resumes]
    cross_scores = reranker_model.predict(pairs) if pairs else [0] * len(retrieved_resumes)

    reranked = []

    for i, resume in enumerate(retrieved_resumes):
        resume_text = resume.get("full_text", "")
        gap_data = resume.get("gap_analysis", {})

        # Component scores
        matched_skills = gap_data.get("matched_skills", [])
        missing_skills = gap_data.get("missing_skills", [])
        total_skills = len(matched_skills) + len(missing_skills)
        skill_score = len(matched_skills) / total_skills if total_skills > 0 else 0

        cross_score = cross_scores[i] if i < len(cross_scores) else 0
        cross_score = max(0.0, min(cross_score / 3.0, 1.0))

        stability_score = compute_stability_score(resume_text)

        # Get dynamic weights
        weights = get_dynamic_global_weights(jd_text)
        cross_w = weights["cross_weight"]
        skill_w = weights["skill_weight"]
        stab_w = weights["stability_weight"]

        # Weighted raw score
        weighted_components = {
            "cross": cross_w * cross_score,
            "skill": skill_w * skill_score,
            "stability": stab_w * stability_score,
        }
        raw_score = sum(weighted_components.values())

        reranked.append({
            "resume_id": resume.get("resume_id"),
            "raw_score": raw_score,
            "component_scores": {
                "cross_score": cross_score,
                "skill_score": skill_score,
                "stability_score": stability_score,
            },
            "weighted_contributions": weighted_components,
            "gap_analysis": gap_data,
            "full_text": resume_text
        })

    # Normalize final scores
    raw_scores = [r["raw_score"] for r in reranked]
    min_score, max_score = min(raw_scores), max(raw_scores)
    for r in reranked:
        r["final_score"] = round(normalize_score(r["raw_score"], min_score, max_score), 4)
        total_weighted = sum(r["weighted_contributions"].values())
        if total_weighted > 0:
            r["contribution_percent"] = {
                k: round((v / total_weighted) * 100, 2)
                for k, v in r["weighted_contributions"].items()
            }
        else:
            r["contribution_percent"] = {}

    reranked.sort(key=lambda x: x["final_score"], reverse=True)
    return reranked
