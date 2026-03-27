import json
import time
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.services.research_services import run_research, llm_provider
from app.models.research_models import ResearchResponse
from app.database.connection import get_db
from app.database.models import User, ResearchSession, ResearchQuery, ResearchCache
from app.auth.dependencies import get_current_user
from app.api.rate_limiter import limiter

router = APIRouter()
MAX_PROMPT_LENGTH = 2000


@router.get("/")
def hello():
    return ("hello bitch")


@router.get("/health")
async def health_check():
    import inspect
    if inspect.iscoroutinefunction(llm_provider.is_available):
        llm_ok = await llm_provider.is_available()
    else:
        llm_ok = llm_provider.is_available()
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "env": settings.env,
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model": settings.OLLAMA_MODEL,
        "llm_status": "connected" if llm_ok else "unavailable",
        "rate_limits": {
            "research": "10/hour",
            "signup": "5/hour",
            "login": "20/hour",
        },
    }


class ResearchRequest(BaseModel):
    prompt: str
    mode: str = "linear"
    session_id: Optional[str] = None


@router.post("/research", response_model=ResearchResponse)
@limiter.limit("10/hour")
async def research(
    request: Request,
    research_request: ResearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not research_request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty or just spaces")

    if len(research_request.prompt) > MAX_PROMPT_LENGTH:
        raise HTTPException(status_code=413, detail=f"Prompt cannot be too long, The maximum allowed is {MAX_PROMPT_LENGTH} characters")

    valid_modes = {"linear", "react"}
    if research_request.mode not in valid_modes:
        raise HTTPException(status_code=400, detail=f"Invalid mode '{research_request.mode}'. Must be one of: {', '.join(valid_modes)}")

    start_time = time.time()
    result = await run_research(research_request.prompt, mode=research_request.mode, db=db)
    duration = round(time.time() - start_time, 2)

    # Resolve or create session
    session_id = research_request.session_id
    if session_id:
        session_result = await db.execute(
            select(ResearchSession).where(
                ResearchSession.id == session_id,
                ResearchSession.user_id == current_user.id,
            )
        )
        session = session_result.scalar_one_or_none()
        if session is None:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        session = ResearchSession(
            user_id=current_user.id,
            title=research_request.prompt[:50],
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        session_id = session.id

    # Check if this is the first query in the session and update title
    queries_count_result = await db.execute(
        select(ResearchQuery).where(ResearchQuery.session_id == session.id)
    )
    existing_queries = queries_count_result.scalars().all()
    if len(existing_queries) == 0 and research_request.session_id:
        session.title = research_request.prompt[:50]
        await db.commit()

    # Save the query result
    citations = result.get("citations", [])
    citations_as_dicts = [c.model_dump() if hasattr(c, "model_dump") else (c.dict() if hasattr(c, "dict") else c) for c in citations]
    query_record = ResearchQuery(
        session_id=session.id,
        prompt=research_request.prompt,
        mode=research_request.mode,
        answer=result.get("answer", ""),
        citations_json=json.dumps(citations_as_dicts),
        confidence=result.get("confidence", 0.0),
        query_type=result.get("query_type"),
        resolved_meaning=result.get("resolved_meaning"),
        react_steps=result.get("react_steps"),
        duration_seconds=duration,
    )
    db.add(query_record)
    await db.commit()

    return {
        "status": "success",
        "prompt": research_request.prompt,
        "answer": result["answer"],
        "citations": result["citations"],
        "confidence": result["confidence"],
        "query_type": result.get("query_type"),
        "resolved_meaning": result.get("resolved_meaning"),
        "react_steps": result.get("react_steps"),
        "session_id": session_id,
    }


@router.delete("/cache")
async def clear_cache(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ResearchCache).where(ResearchCache.expires_at < datetime.utcnow())
    )
    expired = result.scalars().all()
    for entry in expired:
        await db.delete(entry)
    await db.commit()

    return {"status": "cleared", "removed": len(expired)}
