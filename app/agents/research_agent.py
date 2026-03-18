import logging
import re

from app.providers.search_provider import SearchProvider
from app.providers.mock_search_provider import MockSearchProvider
from app.providers.llm_provider import LLMProvider
from app.providers.mock_llm_provider import MockLLMProvider
from app.models.research_models import ResearchPlan, ResearchState, Source, Citation
from app.prompts.synthesis import SYNTHESIS_SYSTEM_PROMPT, build_synthesis_prompt
from app.prompts.query_analysis import QUERY_ANALYSIS_SYSTEM_PROMPT, QUERY_ANALYSIS_USER_TEMPLATE
from app.utils.json_parser import parse_llm_json
from typing import List

logger = logging.getLogger(__name__)

class ResearchAgent:
    def __init__(self, search_provider: SearchProvider = None, llm_provider: LLMProvider = None):
        if search_provider is None:
            search_provider = MockSearchProvider()
        if llm_provider is None:
            llm_provider = MockLLMProvider()
        self.search_provider = search_provider
        self.llm_provider = llm_provider


    
    async def plan_step(self, prompt: str) -> ResearchPlan:
        user_prompt = QUERY_ANALYSIS_USER_TEMPLATE.format(query=prompt)
        response = await self.llm_provider.generate(
            prompt=user_prompt,
            system=QUERY_ANALYSIS_SYSTEM_PROMPT,
            temperature=0.2,
        )
        parsed = parse_llm_json(response.text)

        raw_queries = parsed.get("search_queries")
        if raw_queries and isinstance(raw_queries, list) and all(isinstance(q, str) for q in raw_queries):
            search_queries = raw_queries
        else:
            search_queries = [
                f"{prompt} definition",
                f"{prompt} importance",
                f"{prompt} examples",
            ]

        raw_questions = parsed.get("sub_questions")
        if raw_questions and isinstance(raw_questions, list) and all(isinstance(q, str) for q in raw_questions):
            sub_questions = raw_questions
        else:
            sub_questions = [
                f"What is {prompt}?",
                f"Why is {prompt} important?",
                f"What are examples of {prompt}?",
            ]

        logger.info(
            "Query analysis: type=%s, domain=%s, ambiguous=%s",
            parsed.get("query_type", "unknown"),
            parsed.get("domain", "unknown"),
            parsed.get("is_ambiguous", "unknown"),
        )

        return ResearchPlan(sub_questions=sub_questions, search_queries=search_queries)
    
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
        empty = sum(1 for s in sources if not (s.snippet or "").strip())
        logger.info("empty_snippets=%s out_of=%s", empty, len(sources))
        
        return notes
    
    async def write_step(self, prompt: str, notes, sources: List[Source]) -> str:
        if not notes:
            return (
                f"I couldn’t find enough usable information to answer: ‘{prompt}’. "
                "Try rephrasing your question or being more specific."
            )

        user_prompt = build_synthesis_prompt(prompt, sources[:8])
        response = await self.llm_provider.generate(prompt=user_prompt, system=SYNTHESIS_SYSTEM_PROMPT)

        if not response.text.strip():
            logger.warning("LLM returned empty synthesis, falling back to concatenation")
            intro = f"Based on the collected research, here is a structured explanation of ‘{prompt}’: "
            body = " ".join(notes)
            conclusion = " The information above is synthesized from the referenced sources."
            return intro + body + conclusion

        logger.info("Synthesis used %s tokens", response.tokens_used)
        return response.text
    

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


    def _extract_cited_source_numbers(self, answer: str) -> set:
        return {int(n) for n in re.findall(r"\[(\d+)\]", answer)}

    async def run(self, prompt:str) -> dict:
        plan = await self.plan_step(prompt)
        all_sources = await self.search_step(plan)
        notes = self.analyze_step(all_sources)
        sources = all_sources[:10]
        logger.info("Total sources collected: %s, sending top %s to synthesis", len(all_sources), min(len(all_sources), 10))
        answer = await self.write_step(prompt, notes, sources)
        confidence = self.confidence_step(all_sources, notes)

        cited_numbers = self._extract_cited_source_numbers(answer)
        citations = []
        for i, source in enumerate(sources, start=1):
            if i in cited_numbers:
                citations.append(
                    Citation(
                        source_id=source.id,
                        url=source.url,
                        title=source.title,
                        quotes=source.snippet[:200],
                        evidence=source.snippet,
                        confidence=0.5
                    )
                )

        return {
            "status": "success",
            "answer": answer,
            "prompt": prompt,
            "citations": citations,
            "confidence": confidence
        }