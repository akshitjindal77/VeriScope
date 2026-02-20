from typing import List
from app.models.research_models import Source
from app.providers.search_provider import SearchProvider

class MockSearchProvider(SearchProvider):
    async def search(self, query: str) -> List[Source]:
        sources = []
        sources.append(
            Source(
                id="src_1",
                title="Article about " + query,
                url="https://example.com/article1",
                snippet="This article explains " + query
            )
        )
        sources.append(
            Source(
                id="src_2",
                title="Article about " + query,
                url="https://example.com/article2",
                snippet="This article explains " + query
            )
        )
        return sources