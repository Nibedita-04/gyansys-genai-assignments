from pydantic import BaseModel
from typing import List, Optional

class Education(BaseModel):
    degree: str
    field_of_study: Optional[str] = None
    institute: str
    start_year: Optional[str] = None
    end_year: Optional[str] = None
    grade: Optional[str] = None

class ResumeSchema(BaseModel):
    candidate_name: str
    total_years_experience: float
    avg_years_in_org: float
    skills: List[str]
    current_organization: Optional[str]
    projects: List[str]
    summary: str
    education: List[Education]

class JDSchema(BaseModel):
    job_titlle: str
    required_experience: float
    required_skills: List[str]
    summary: str

