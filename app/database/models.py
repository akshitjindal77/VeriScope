from uuid import uuid4

from sqlalchemy import Column, String, Float, Boolean, Text, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.connection import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)

    sessions = relationship("ResearchSession", back_populates="user", cascade="all, delete-orphan")


class ResearchSession(Base):
    __tablename__ = "research_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, default="New Research")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="sessions")
    queries = relationship("ResearchQuery", back_populates="session", cascade="all, delete-orphan", order_by="ResearchQuery.created_at")


class ResearchQuery(Base):
    __tablename__ = "research_queries"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    session_id = Column(String, ForeignKey("research_sessions.id"), nullable=False, index=True)
    prompt = Column(String, nullable=False)
    mode = Column(String, default="linear")
    answer = Column(Text, default="")
    citations_json = Column(Text, default="[]")
    confidence = Column(Float, default=0.0)
    query_type = Column(String, nullable=True)
    resolved_meaning = Column(String, nullable=True)
    react_steps = Column(Integer, nullable=True)
    duration_seconds = Column(Float, default=0.0)
    created_at = Column(DateTime, server_default=func.now())

    session = relationship("ResearchSession", back_populates="queries")


class ResearchCache(Base):
    __tablename__ = "research_cache"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    prompt_hash = Column(String, nullable=False, index=True)
    mode = Column(String, nullable=False)
    response_json = Column(Text, nullable=False)
    prompt_embedding = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=False)
