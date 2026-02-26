from __future__ import annotations
from app.providers.search_provider import SearchProvider
from app.models.research_models import Source

from typing import List
import logging, hashlib, httpx
from cachetools import TTLCache

logger = logging.getLogger(__name__)

def make_source_id(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:10]

class BraveSearchProvider(SearchProvider):
    def __init__(self, settings):
        self.settings = settings
        self._cache = TTLCache(maxsize=512, ttl=int(settings.WEB_SEARCH_CACHE_TTL_S))

    async def search(self, query: str) -> List[Source]:
        q = (query or "").strip()
        if not q:
            return []
        if q in self._cache:
            return self._cache[q]
        if not self.settings.BRAVE_API_KEY:
            logger.error("BRAVE_API_KEY is missing")
            self._cache[q] = []
            return []
        
        timeout = httpx.Timeout(self.settings.WEB_SEARCH_TIMEOUT_S)

        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.settings.BRAVE_API_KEY,
        }

        params = {
            "q": q,
            "count": int(self.settings.WEB_SEARCH_MAX_RESULTS),
        }

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                r = await client.get(self.settings.BRAVE_ENDPOINT, headers=headers, params=params)
                r.raise_for_status()
                data = r.json()
        except httpx.HTTPError as e:
            logger.exception("Brave search HTTP error: %s", e)
            self._cache[q] = []
            return []
        except Exception as e:
            logger.exception("Brave search unexpected error: %s", e)
            self._cache[q] = []
            return []
        
        results: List[Source] = []
        web = (data or {}).get("web") or {}
        items = web.get("results") or []

        for item in items:
            url = (item.get("url") or "").strip()
            title = (item.get("title") or "").strip()
            snippet = (item.get("description") or "").strip()

            if not url:
                continue
            if not title:
                title = url
            
            results.append(
                Source(
                    id= make_source_id(url),
                    title=title,
                    url=url,
                    snippet=snippet,
                    published_at=None,
                )
            )

            if len(results) >= int(self.settings.WEB_SEARCH_MAX_RESULTS):
                break

        logger.info("Brave returned %s results for query=%s", len(results), q)
        self._cache[q] = results
        return results
        