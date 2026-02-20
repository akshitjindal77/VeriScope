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

    def analyze_step(self, sources):
        notes = []
        seen = set()

        for s in sources:
            text = (s.snippet or "").strip()
            if not text:
                continue

            note = text

            if note not in seen:
                seen.add(note)
                notes.append(note)
        
        return notes
    
    def write_step(self, prompt:str, notes):
        if not notes:
            return (
                f"I couldn’t find enough usable information to answer: '{prompt}'. "
                "Try rephrasing your question or being more specific."
            )
        
        intro = f"Based on the collected research, here is a structured explanation of '{prompt}': "
        body = " ".join(notes)
        conclusion = " The information above is synthesized from the referenced sources."

        return intro + body + conclusion
    

    def confidence_step(self, sources, notes):
        if not notes:
            return 0.2
        
        unique_sources = len(sources)

        conf = 0.3 + (0.15*unique_sources)

        if conf > 0.95:
            conf = 0.95
        if conf < 0.1:
            conf = 0.1
        
        return round(conf, 2)


    async def run(self, prompt:str) -> dict:
        plan = await self.plan_step(prompt)
        sources = await self.search_step(plan)
        notes = self.analyze_step(sources)
        answer = self.write_step(prompt, notes)
        confidence = self.confidence_step(sources, notes)

        citations = []
        for source in sources:
            citations.append(
                Citation(
                    source_id = source.id,
                    evidence= source.snippet,
                    confidence= None
                )
            )

        return {
            "status": "success",
            "answer": answer,
            "prompt": prompt,
            "citations": citations,
            "confidence": confidence
        }