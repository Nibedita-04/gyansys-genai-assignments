from pydantic import BaseModel, Field
from typing import List


class HSNPrediction(BaseModel):
    hsn: str = Field(description="HSN code")
    confidence: float = Field(description="Confidence score between 0 and 1")
    reasoning: str = Field(description="Short explanation")


class FinalHSNOutput(BaseModel):
    predictions: List[HSNPrediction]
