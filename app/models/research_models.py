from pydantic import BaseModel
from typing import List

class ResearchResponse(BaseModel):
    status: str
    answer: str
    prompt: str
    citations: List[str]
    confidence: float