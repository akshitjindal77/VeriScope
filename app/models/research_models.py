from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class Source(BaseModel):
    id: str
    title: str
    url: str
    snippet: str
    published_at: Optional[datetime] = None

class ScoredSource(Source):
    domain_authority: float = 0.0
    relevance_score: float = 0.0
    quality_score: float = 0.0

class Citation(BaseModel):
    source_id: str
    url: str
    title: str
    quotes: str = ""
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
    query_type: Optional[str] = None
    resolved_meaning: Optional[str] = None
    react_steps: Optional[int] = None
    session_id: Optional[str] = None

class ResearchResult(BaseModel):
    answer: str
    citations: List[Citation] = []
    confidence: Optional[float] = None

# ── LLM Provider Models ──────────────────────────────────────────────

class LLMResponse(BaseModel):
    """Standardized response shape returned by every LLM provider."""

    text: str
    model: str
    tokens_used: Optional[int] = None


class QueryAnalysis(BaseModel):
    """Structured output from LLM query analysis. Captures intent, domain, ambiguity detection, and resolved search strategy."""

    query_type: str = "general"
    domain: str = "general"
    is_ambiguous: bool = False
    candidate_meanings: List[str] = Field(default_factory=list)
    resolved_meaning: Optional[str] = None
    search_queries: List[str] = Field(default_factory=list)
    sub_questions: List[str] = Field(default_factory=list)