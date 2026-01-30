from pydantic import BaseModel, Field
from typing import List, Optional

class SkillExtraction(BaseModel):
    name: Optional[str] = Field(
        default=None,
        description="Full name of the candidate from the resume"
    )
     
    programming_languages: List[str] = Field(
        description = "Programming languages explicitly mentioned in the resume"
    )

    frameworks_libraries: List[str] = Field(
        description = "Frameworks and libraries such as FastAPI, LangChain, Raect, etc."
    )

    tools_technologies: List[str] = Field(
        description = "developer tools, platforms, IDEs, APIs, etc."
    )

    databases: List[str] = Field(
        description = "Databases such as MySQL, PostgreSQL, MongoDB, etc."
    )

    cloud_devops: List[str] = Field(
        description = "Cloud platforms and DevOPs tools like AWS, Docker, Kubernetes"
    )

    data_AI_ML: List[str] = Field(
        description = "Data science, AI, and ML-related skills"
    )

    soft_skills: List[str] = Field(
        description = "Soft skills such as communication, teamwork, leadership"
    )

    domain_skills: List[str] = Field(
        description = "Domain-specific skills like healthcare, finance, education, etc."
    )