from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class Source(BaseModel):
    id: str
    title: str
    url: str
    snippet: str
    published_at: Optional[datetime] = None

class Citation(BaseModel):
    source_id: str
    evidence: str
    confidence: Optional[float] = None

class ResearchPlan(BaseModel):
    sub_questions: List[str]
    search_queries: List[str]

class ResearchState(BaseModel):
    prompt: str
    plan: ResearchPlan
    sources: List[Source] = Field(default_factory=list)
    notes: List[str]
    answer: str
    citations: List[Citation]
    confidence: float
    stage: Literal["plan","search","analyze","answer","done"]

class ResearchResponse(BaseModel):
    status: str
    answer: str
    prompt: str
    citations: List[Citation]
    confidence: float