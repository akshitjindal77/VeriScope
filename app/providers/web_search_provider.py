from __future__ import annotations
from typing import List, Optional
import hashlib, re
from urllib.parse import urlparse, parse_qs, urlunparse
import httpx
from bs4 import BeautifulSoup
from cachetools import TTLCache
import logging

from app.providers.search_provider import SearchProvider
from app.config.settings import Settings
from app.models.research_models import Source

logger = logging.getLogger(__name__)

def _host(url: str) -> str:
    try:
        return (urlparse(url).hostname).lower()
    except Exception:
        return ""

def _strip_www(host: str) -> str:
    return host[4:] if host.startswith("www.") else host

def _is_blocked(host: str, blocked: List[str]) -> bool:
    h = _strip_www(host)
    for d in blocked:
        d = d.lower().strip()
        if not d:
            continue
        if d == h or h.endswith("." + d):
            return True
    return False

def _is_allowed(host: str, allowed: Optional[List[str]]) -> bool:
    if not allowed:
        return True
    h = _strip_www(host)
    for d in allowed:
        d = d.lower().strip()
        if not d:
            continue
        if h == d or h.endswith("." + d):
            return True
    return False

def _canonicalize_url(url:str) -> str:
    try:
        u = urlparse(url)
        qs = parse_qs(u.query)

        tracking_keys = {
            "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "gclid", "fbclid", "mc_cid", "mc_eid"
        }
        kept = []
        for k, vals in qs.items():
            if k in tracking_keys:
                continue
            for v in vals:
                kept.append((k,v))
        
        query = "&".join([f"{k}={v}" for k, v in kept])
        u2 = u._replace(fragment="", query=query)
        return urlunparse(u2)
    except Exception:
        return url

def _make_source_id(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:10]




class WebSearchProvider(SearchProvider):
    def __init__(self, settings):
        self.settings = settings
        self._cache = TTLCache(maxsize=512, ttl= int(settings.WEB_SEARCH_CACHE_TTL_S))
    
    async def search(self, query: str) -> List[Source]:
        q = (query or "").strip()
        if not q:
            return []
        
        if q in self._cache:
            return self._cache(q)
        
        timeout = httpx.Timeout(self.settings.WEB_SEARCH_TIMEOUT_S)
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        }

        url = "https://duckduckgo.com/html/"
        params = {"q": q}

        async with httpx.AsyncClient(timeout=timeout, headers=headers, follow_redirects=True) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
        
        sources = self._parse_ddg_html(r.text)

        cleaned: List[Source] = []
        seen = set()

        for s in sources:
            canon = _canonicalize_url(s.url)
            host = _host(canon)
            if not host:
                continue
            if _is_blocked(host, self.settings.WEB_SEARCH_BLOCK_DOMAINS):
                continue
            if not _is_allowed(host, self.settings.WEB_SEARCH_ALLOW_DOMAINS):
                continue

            if canon in seen:
                continue
            seen.add(canon)

            cleaned.append(
                Source(
                    id=_make_source_id(canon),
                    title=s.title.strip() if s.title else host,
                    url=canon,
                    snippet=(s.snippet or "").strip(),
                    published_at=getattr(s, "published_at", None),
                )
            )
            if len(cleaned) >= int(self.settings.WEB_SEARCH_MAX_RESULTS):
                break

            self._cache[q] = cleaned
        return cleaned
        
    def _parse_ddg_html(self, html:str) -> List[Source]: #take raw html text and return as Source objects
        soup = BeautifulSoup(html, "html.parser")
        results = []

        for res in soup.select(".result"):
            a = res.select_one("a.result__a")
            snippet_el = res.select_one(".result__snippet")

            if not a or not a.get("href"):
                continue

            title = a.get_text(" ", strip=True)
            href = a["href"].strip()
            snippet = snippet_el.get_text(" ", strip=True) if snippet_el else ""

            snippet = re.sub(r"\s+", " ", snippet).strip()

            results.append(
                Source(
                    id="tmp",
                    title=title,
                    url=href,
                    snippet=snippet,
                    published_at=None,
                )
            )
        logger.info("Found %s raw result blocks", len(results))
        return results


