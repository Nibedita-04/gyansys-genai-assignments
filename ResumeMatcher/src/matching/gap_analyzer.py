import re
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Dict, Optional, Union

def extract_skills_dynamic(text: str, top_k: int = 25) -> List[str]:
    """
    Extract top skills/tools/technologies using TF-IDF.
    """
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 3),
        max_features=top_k
    )
    tfidf = vectorizer.fit_transform([text])
    return vectorizer.get_feature_names_out().tolist()


def extract_years_experience(text: str) -> Optional[int]:
    """
    Extract total years of experience mentioned in text.
    Example patterns: "5 years", "3+ years"
    """
    match = re.search(r"(\d+)\+?\s*years", text.lower())
    return int(match.group(1)) if match else None


def gap_analysis(resume_text: str, jd_text: str) -> Dict[str, Union[List[str], Optional[int]]]:
    """
    Compare resume vs JD for skill gaps and experience gaps.
    Returns:
        - matched_skills: Skills present in both resume & JD
        - missing_skills: Skills in JD missing from resume
        - resume_years: Extracted years from resume
        - jd_years: Extracted years from JD
        - experience_gap: jd_years - resume_years (if both exist)
    """
    resume_skills = set(extract_skills_dynamic(resume_text))
    jd_skills = set(extract_skills_dynamic(jd_text))

    matched = resume_skills.intersection(jd_skills)
    missing = jd_skills - resume_skills

    resume_years = extract_years_experience(resume_text)
    jd_years = extract_years_experience(jd_text)

    experience_gap = jd_years - resume_years if jd_years and resume_years else None

    return {
        "matched_skills": list(matched),
        "missing_skills": list(missing),
        "resume_years": resume_years,
        "jd_years": jd_years,
        "experience_gap": experience_gap
    }
