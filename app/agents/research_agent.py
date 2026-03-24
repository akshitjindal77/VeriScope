import logging
import re

from app.providers.search_provider import SearchProvider
from app.providers.mock_search_provider import MockSearchProvider
from app.providers.llm_provider import LLMProvider
from app.providers.mock_llm_provider import MockLLMProvider
from app.models.research_models import ResearchPlan, ResearchState, Source, Citation, QueryAnalysis, ScoredSource
from app.utils.source_scoring import compute_source_quality, get_domain_authority_score, compute_relevance_score
from app.prompts.synthesis import SYNTHESIS_SYSTEM_PROMPT, build_synthesis_prompt
from app.prompts.query_analysis import QUERY_ANALYSIS_SYSTEM_PROMPT, QUERY_ANALYSIS_USER_TEMPLATE
from app.prompts.disambiguation import DISAMBIGUATION_SYSTEM_PROMPT, DISAMBIGUATION_USER_TEMPLATE, format_candidate_meanings
from app.utils.json_parser import parse_llm_json
from typing import List, Optional, Callable, Awaitable

StatusCallback = Optional[Callable[[str, str], Awaitable[None]]]

logger = logging.getLogger(__name__)

class ResearchAgent:
    def __init__(self, search_provider: SearchProvider = None, llm_provider: LLMProvider = None):
        if search_provider is None:
            search_provider = MockSearchProvider()
        if llm_provider is None:
            llm_provider = MockLLMProvider()
        self.search_provider = search_provider
        self.llm_provider = llm_provider

    async def disambiguate_step(self, prompt: str, analysis: QueryAnalysis) -> QueryAnalysis:
        if not analysis.is_ambiguous or not analysis.candidate_meanings:
            return analysis

        formatted = format_candidate_meanings(analysis.candidate_meanings)
        user_prompt = DISAMBIGUATION_USER_TEMPLATE.format(
            query=prompt,
            candidate_meanings=formatted,
            domain=analysis.domain,
        )
        response = await self.llm_provider.generate(
            prompt=user_prompt,
            system=DISAMBIGUATION_SYSTEM_PROMPT,
            temperature=0.1,
        )
        parsed = parse_llm_json(response.text)

        resolved = parsed.get("resolved_meaning", "")
        if resolved and isinstance(resolved, str) and resolved.strip():
            analysis.resolved_meaning = resolved
            logger.info(
                "Disambiguated '%s' to: %s (reason: %s)",
                prompt,
                resolved,
                parsed.get("reasoning", "none"),
            )
            new_queries = parsed.get("search_queries")
            if new_queries and isinstance(new_queries, list) and len(new_queries) > 0:
                analysis.search_queries = new_queries
        else:
            logger.warning("Disambiguation failed for '%s', using original queries", prompt)

        return analysis

    async def plan_step(self, prompt: str) -> ResearchPlan:
        user_prompt = QUERY_ANALYSIS_USER_TEMPLATE.format(query=prompt)
        response = await self.llm_provider.generate(
            prompt=user_prompt,
            system=QUERY_ANALYSIS_SYSTEM_PROMPT,
            temperature=0.2,
        )
        parsed = parse_llm_json(response.text)

        # Coerce is_ambiguous to a proper boolean
        # Mistral sometimes returns "true"/"false" as strings instead of JSON booleans
        raw_ambiguous = parsed.get("is_ambiguous", False)
        if isinstance(raw_ambiguous, str):
            is_ambiguous = raw_ambiguous.strip().lower() == "true"
        else:
            is_ambiguous = bool(raw_ambiguous)

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

        # Ensure candidate_meanings is a list of strings
        raw_candidates = parsed.get("candidate_meanings", [])
        if isinstance(raw_candidates, list):
            candidate_meanings = [str(c) for c in raw_candidates if c]
        else:
            candidate_meanings = []

        if is_ambiguous and not candidate_meanings:
            # LLM flagged ambiguity but didn't provide meanings — generate generic ones
            term = prompt.strip().rstrip("?").split()[-1]  # rough extraction of the key term
            candidate_meanings = [
                f"{term} (technical/scientific meaning)",
                f"{term} (common/everyday meaning)",
            ]
            logger.info("Generated fallback candidate meanings for '%s': %s", prompt, candidate_meanings)

        analysis = QueryAnalysis(
            query_type=parsed.get("query_type", "general"),
            domain=parsed.get("domain", "general"),
            is_ambiguous=is_ambiguous,
            candidate_meanings=candidate_meanings,
            search_queries=search_queries,
            sub_questions=sub_questions,
        )

        analysis = await self.disambiguate_step(prompt, analysis)

        logger.info(
            "Query analysis: type=%s, domain=%s, ambiguous=%s, resolved=%s",
            analysis.query_type,
            analysis.domain,
            analysis.is_ambiguous,
            analysis.resolved_meaning,
        )

        return (ResearchPlan(sub_questions=analysis.sub_questions, search_queries=analysis.search_queries), analysis)
    
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
    

    def confidence_step(self, sources, notes, is_ambiguous: bool = False, was_disambiguated: bool = False) -> float:
        """Calculate overall confidence based on source quality, diversity, and coverage."""
        if not notes:
            return 0.1

        quality_scores = [getattr(s, 'quality_score', 0.4) for s in sources]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0

        count = len(sources)
        if count >= 8:
            count_factor = 0.85
        elif count >= 5:
            count_factor = 0.5 + (count - 5) * 0.05 + 0.2
        elif count >= 3:
            count_factor = 0.3 + (count - 3) * 0.1
        elif count >= 1:
            count_factor = 0.2 + (count - 1) * 0.05
        else:
            count_factor = 0.0

        domains = set()
        for s in sources:
            try:
                from urllib.parse import urlparse
                host = urlparse(s.url).hostname or ""
                parts = host.split(".")
                if len(parts) >= 2:
                    domains.add(".".join(parts[-2:]))
            except Exception:
                pass
        diversity = min(len(domains) / 5.0, 1.0)

        ambiguity_penalty = 0.0
        if is_ambiguous and not was_disambiguated:
            ambiguity_penalty = 0.15
        elif is_ambiguous and was_disambiguated:
            ambiguity_penalty = 0.05

        raw_confidence = (
            (0.35 * avg_quality) +
            (0.30 * count_factor) +
            (0.20 * diversity) +
            (0.15 * 1.0)
        ) - ambiguity_penalty

        confidence = max(0.1, min(0.95, raw_confidence))

        logger.info(
            "Confidence: avg_quality=%.2f, count_factor=%.2f, diversity=%.2f, ambiguity_penalty=%.2f, final=%.2f",
            avg_quality, count_factor, diversity, ambiguity_penalty, confidence,
        )

        return round(confidence, 2)


    def score_sources_step(self, prompt: str, sources: List[Source]) -> List[ScoredSource]:
        """Score each source by domain authority and relevance, then sort by quality descending."""
        scored: List[ScoredSource] = []

        for source in sources:
            authority = get_domain_authority_score(source.url)
            relevance = compute_relevance_score(prompt, source.snippet)
            quality = round((0.6 * authority) + (0.4 * relevance), 2)

            scored.append(ScoredSource(
                id=source.id,
                title=source.title,
                url=source.url,
                snippet=source.snippet,
                published_at=source.published_at,
                domain_authority=authority,
                relevance_score=relevance,
                quality_score=quality,
            ))

        scored.sort(key=lambda s: s.quality_score, reverse=True)

        logger.info(
            "Source scoring: %s sources scored, top=%s (%.2f), bottom=%s (%.2f)",
            len(scored),
            scored[0].url if scored else "none",
            scored[0].quality_score if scored else 0,
            scored[-1].url if scored else "none",
            scored[-1].quality_score if scored else 0,
        )

        return scored

    async def _emit(self, callback: StatusCallback, stage: str, message: str):
        """Send a status update if a callback is provided."""
        if callback:
            await callback(stage, message)

    def _extract_cited_source_numbers(self, answer: str) -> set:
        return {int(n) for n in re.findall(r"\[(\d+)\]", answer)}

    async def run(self, prompt: str, status_callback: StatusCallback = None) -> dict:
        await self._emit(status_callback, "analyzing", "Analyzing your query...")
        plan, analysis = await self.plan_step(prompt)
        await self._emit(status_callback, "planning", f"Generated {len(plan.search_queries)} search queries")

        await self._emit(status_callback, "searching", f"Searching {len(plan.search_queries)} queries...")
        all_sources = await self.search_step(plan)
        await self._emit(status_callback, "searching", f"Found {len(all_sources)} sources")

        await self._emit(status_callback, "scoring", f"Scoring {len(all_sources)} sources by quality...")
        scored_sources = self.score_sources_step(prompt, all_sources)

        min_quality = 0.3
        filtered = [s for s in scored_sources if s.quality_score >= min_quality]
        if len(filtered) < 5 and len(scored_sources) >= 5:
            filtered = scored_sources[:5]
        logger.info("Source filtering: %s -> %s sources (min_quality=%.2f)", len(scored_sources), len(filtered), min_quality)

        notes = self.analyze_step(filtered)
        sources = filtered[:10]
        await self._emit(status_callback, "scoring", f"Selected top {len(sources)} sources for synthesis")
        logger.info("Total sources collected: %s, sending top %s to synthesis", len(all_sources), len(sources))

        for i, s in enumerate(sources[:5]):
            logger.info(
                "  Source #%s: quality=%.2f authority=%.2f relevance=%.2f | %s",
                i + 1,
                getattr(s, 'quality_score', 0),
                getattr(s, 'domain_authority', 0),
                getattr(s, 'relevance_score', 0),
                s.url[:80],
            )

        await self._emit(status_callback, "synthesizing", "Writing answer from sources...")
        answer = await self.write_step(prompt, notes, sources)
        await self._emit(status_callback, "synthesizing", "Answer complete, building citations...")
        confidence = self.confidence_step(
            sources,
            notes,
            is_ambiguous=analysis.is_ambiguous if analysis else False,
            was_disambiguated=analysis.resolved_meaning is not None if analysis else False,
        )

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
                        confidence=getattr(source, 'quality_score', 0.5)
                    )
                )
        await self._emit(status_callback, "done", "Research complete")

        return {
            "status": "success",
            "answer": answer,
            "prompt": prompt,
            "citations": citations,
            "confidence": confidence,
            "query_type": analysis.query_type,
            "resolved_meaning": analysis.resolved_meaning,
        }