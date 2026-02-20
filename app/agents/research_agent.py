from app.providers.search_provider import SearchProvider
from app.providers.mock_search_provider import MockSearchProvider
from app.models.research_models import ResearchPlan, ResearchState, Source, Citation
from typing import List

class ResearchAgent:
    def __init__(self, search_provider: SearchProvider = None):
        if search_provider is None:
            search_provider = MockSearchProvider()
        self.search_provider = search_provider


    
    async def plan_step(self, prompt:str) -> ResearchPlan:
        sub_questions = [
            f"What is {prompt}?",
            f"Why is {prompt} important?",
            f"What are examples or real-world applications of {prompt}?"
        ]

        search_queries = [
            f"{prompt} definition",
            f"{prompt} importance",
            f"{prompt} examples"
        ]

        return ResearchPlan(
            sub_questions=sub_questions,
            search_queries=search_queries
        )
    
    async def search_step(self, plan: ResearchPlan) -> List[Source]:
        all_sources: List[Source] = []
        seen_urls = set()

        for query in plan.search_queries:
            results = await self.search_provider.search(query)

            for source in results:
                if source.url not in seen_urls:
                    seen_urls.add(source.url)
                    all_sources.append(source)

        return all_sources        

    async def run(self, prompt:str) -> dict:
        plan = await self.plan_step(prompt)
        sources = await self.search_step(plan)

        citations = []
        for source in sources:
            citations.append(
                Citation(
                    source_id = source.id,
                    evidence= source.snippet,
                    confidence= None
                )
            )

        answer = f"Research results collected for '{prompt}'."

        return {
            "answer": answer,
            "citations": [source.url for source in sources],
            "citations": citations,
            "confidence": 0.7
        }