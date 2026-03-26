import hashlib
import json
import logging
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.research_agent import ResearchAgent
from app.agents.react_agent import ReactResearchAgent
from app.providers.web_search_provider import WebSearchProvider
from app.providers.brave_search_provider import BraveSearchProvider
from app.providers.ollama_provider import OllamaProvider
from app.providers.mock_llm_provider import MockLLMProvider
from app.config.settings import settings
from app.database.models import ResearchCache

logger = logging.getLogger(__name__)


def _build_provider():
    if settings.WEB_SEARCH_PROVIDER.lower() == "brave":
        return BraveSearchProvider(settings)
    return WebSearchProvider(settings)


def _build_llm_provider():
    if settings.LLM_PROVIDER.lower() == "ollama":
        return OllamaProvider(settings)
    return MockLLMProvider()


provider = _build_provider()
llm_provider = _build_llm_provider()
agent = ResearchAgent(search_provider=provider, llm_provider=llm_provider)
react_agent = ReactResearchAgent(search_provider=provider, llm_provider=llm_provider, settings=settings)


def make_cache_key(prompt: str, mode: str) -> str:
    import re
    normalized = prompt.strip().lower()
    normalized = re.sub(r'[?.!,;:\s]+$', '', normalized)
    normalized = re.sub(r'\s+', ' ', normalized)
    return hashlib.sha256(f"{normalized}:{mode}".encode()).hexdigest()


async def get_cached_result(prompt: str, mode: str, db: AsyncSession) -> dict | None:
    cache_key = make_cache_key(prompt, mode)
    result = await db.execute(
        select(ResearchCache).where(
            ResearchCache.prompt_hash == cache_key,
            ResearchCache.mode == mode,
            ResearchCache.expires_at > datetime.utcnow(),
        )
    )
    cached = result.scalar_one_or_none()
    if cached:
        logger.info("Cache HIT for prompt='%s' mode=%s", prompt[:50], mode)
        return json.loads(cached.response_json)
    logger.info("Cache MISS for prompt='%s' mode=%s", prompt[:50], mode)
    return None


def _make_serializable(obj):
    """Convert a response dict with possible Pydantic objects to plain dicts."""
    if isinstance(obj, dict):
        return {k: _make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_make_serializable(item) for item in obj]
    elif hasattr(obj, "model_dump"):
        return obj.model_dump()
    elif hasattr(obj, "dict"):
        return obj.dict()
    else:
        return obj


async def save_to_cache(prompt: str, mode: str, response: dict, db: AsyncSession, ttl_minutes: int = 60):
    cache_key = make_cache_key(prompt, mode)
    cache_entry = ResearchCache(
        prompt_hash=cache_key,
        mode=mode,
        response_json=json.dumps(_make_serializable(response), default=str),
        expires_at=datetime.utcnow() + timedelta(minutes=ttl_minutes),
    )
    db.add(cache_entry)
    await db.commit()
    logger.info("Cached result for prompt='%s' mode=%s (TTL=%s min)", prompt[:50], mode, ttl_minutes)


async def run_research(prompt: str, mode: str = "linear", db: AsyncSession = None, status_callback=None) -> dict:
    logger.info("run_research started")
    logger.info("Prompt Length: %s", len(prompt))

    if db:
        cached = await get_cached_result(prompt, mode, db)
        if cached:
            if status_callback:
                await status_callback("done", "Loaded from cache")
            return cached

    if mode == "react":
        logger.info("Using ReAct agent mode")
        result = await react_agent.run(prompt, status_callback=status_callback)
    else:
        logger.info("Using linear agent mode")
        result = await agent.run(prompt, status_callback=status_callback)

    logger.info("Agent returned %s citations", len(result.get("citations", [])))

    if db:
        ttl = 120 if mode == "react" else 60
        await save_to_cache(prompt, mode, result, db, ttl_minutes=ttl)

    return result
