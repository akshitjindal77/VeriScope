import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.connection import get_db
from app.database.models import User, ResearchSession, ResearchQuery
from app.auth.dependencies import get_current_user
from app.sessions.schemas import (
    CreateSessionRequest,
    SessionResponse,
    SessionDetailResponse,
    QueryInSessionResponse,
)

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("", response_model=list[SessionResponse])
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ResearchSession)
        .where(ResearchSession.user_id == current_user.id)
        .order_by(ResearchSession.updated_at.desc())
    )
    sessions = result.scalars().all()
    return [SessionResponse.model_validate(s) for s in sessions]


@router.post("", response_model=SessionResponse)
async def create_session(
    request: CreateSessionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = ResearchSession(user_id=current_user.id, title=request.title or "New Research")
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return SessionResponse.model_validate(session)


@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ResearchSession).where(
            ResearchSession.id == session_id,
            ResearchSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    queries_result = await db.execute(
        select(ResearchQuery)
        .where(ResearchQuery.session_id == session_id)
        .order_by(ResearchQuery.created_at)
    )
    queries = queries_result.scalars().all()

    query_responses = [
        QueryInSessionResponse(
            id=q.id,
            prompt=q.prompt,
            mode=q.mode,
            answer=q.answer,
            citations=json.loads(q.citations_json or "[]"),
            confidence=q.confidence,
            query_type=q.query_type,
            resolved_meaning=q.resolved_meaning,
            react_steps=q.react_steps,
            duration_seconds=q.duration_seconds,
            created_at=q.created_at,
        )
        for q in queries
    ]

    return SessionDetailResponse(
        id=session.id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
        queries=query_responses,
    )


@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ResearchSession).where(
            ResearchSession.id == session_id,
            ResearchSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    await db.delete(session)
    await db.commit()
    return {"status": "deleted"}
