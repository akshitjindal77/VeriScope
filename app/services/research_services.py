import hashlib
import json as json_module
import logging
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.research_agent import ResearchAgent
from app.agents.react_agent import ReactResearchAgent
from app.providers.web_search_provider import WebSearchProvider
from app.providers.brave_search_provider import BraveSearchProvider
from app.providers.ollama_provider import OllamaProvider
from app.providers.groq_provider import GroqProvider
from app.providers.mock_llm_provider import MockLLMProvider
from app.config.settings import settings
from app.database.models import ResearchCache
from app.utils.embeddings import get_embedding, cosine_similarity

logger = logging.getLogger(__name__)


def _build_provider():
    if settings.WEB_SEARCH_PROVIDER.lower() == "brave":
        return BraveSearchProvider(settings)
    return WebSearchProvider(settings)


def _build_llm_provider():
    if settings.LLM_PROVIDER.lower() == "groq":
        return GroqProvider(settings)
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
    # First: try exact match
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
        logger.info("Cache exact HIT for prompt='%s' mode=%s", prompt[:50], mode)
        return json_module.loads(cached.response_json)

    # Second: try semantic match
    try:
        query_embedding = get_embedding(prompt.strip().lower())

        result = await db.execute(
            select(ResearchCache).where(
                ResearchCache.mode == mode,
                ResearchCache.expires_at > datetime.utcnow(),
                ResearchCache.prompt_embedding.isnot(None),
            )
        )
        candidates = result.scalars().all()

        best_match = None
        best_score = 0.0
        SIMILARITY_THRESHOLD = 0.85

        for candidate in candidates:
            try:
                cached_embedding = json_module.loads(candidate.prompt_embedding)
                similarity = cosine_similarity(query_embedding, cached_embedding)
                if similarity > best_score and similarity >= SIMILARITY_THRESHOLD:
                    best_score = similarity
                    best_match = candidate
            except Exception:
                continue

        if best_match:
            logger.info(
                "Cache semantic HIT for prompt='%s' (similarity=%.3f with cached prompt)",
                prompt[:50], best_score
            )
            return json_module.loads(best_match.response_json)
    except Exception as e:
        logger.warning("Semantic cache lookup failed: %s", e)

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

    try:
        embedding = get_embedding(prompt.strip().lower())
        embedding_json = json_module.dumps(embedding)
    except Exception:
        embedding_json = None

    cache_entry = ResearchCache(
        prompt_hash=cache_key,
        mode=mode,
        response_json=json_module.dumps(_make_serializable(response), default=str),
        prompt_embedding=embedding_json,
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
