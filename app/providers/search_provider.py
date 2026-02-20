from typing import List
from app.models.research_models import Source
from abc import ABC, abstractmethod

class SearchProvider(ABC):
    @abstractmethod
    async def search(self, query: str) -> List[Source]:
        raise NotImplementedError