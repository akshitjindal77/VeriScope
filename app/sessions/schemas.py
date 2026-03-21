from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class CreateSessionRequest(BaseModel):
    title: Optional[str] = None


class SessionResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QueryInSessionResponse(BaseModel):
    id: str
    prompt: str
    mode: str
    answer: str
    citations: List[dict] = []
    confidence: float
    query_type: Optional[str] = None
    resolved_meaning: Optional[str] = None
    react_steps: Optional[int] = None
    duration_seconds: float
    created_at: datetime


class SessionDetailResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    queries: List[QueryInSessionResponse] = []
