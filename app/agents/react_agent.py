import logging
import re
from typing import List, Dict, Optional, Set, Callable, Awaitable

StatusCallback = Optional[Callable[[str, str], Awaitable[None]]]

from app.providers.search_provider import SearchProvider
from app.providers.llm_provider import LLMProvider
from app.agents.tools import format_tools_for_prompt
from app.prompts.react_prompt import build_react_system, build_react_prompt
from app.utils.react_parser import parse_react_response, format_observation
from app.utils.source_scoring import get_domain_authority_score, compute_relevance_score
from app.models.research_models import Source, ScoredSource, Citation
from app.prompts.synthesis import SYNTHESIS_SYSTEM_PROMPT, build_synthesis_prompt
from app.prompts.disambiguation import DISAMBIGUATION_SYSTEM_PROMPT, DISAMBIGUATION_USER_TEMPLATE, format_candidate_meanings
from app.utils.json_parser import parse_llm_json

logger = logging.getLogger(__name__)


class ReactResearchAgent:
    def __init__(self, search_provider: SearchProvider, llm_provider: LLMProvider, settings=None):
        self.search_provider = search_provider
        self.llm_provider = llm_provider
        self.max_steps = settings.REACT_MAX_STEPS if settings else 7

    async def _emit(self, callback: StatusCallback, stage: str, message: str):
        if callback:
            await callback(stage, message)

    async def run(self, prompt: str, status_callback: StatusCallback = None) -> dict:
        tools_text = format_tools_for_prompt()
        system_prompt = build_react_system(tools_text)

        collected_sources: List[Source] = []
        seen_urls: Set[str] = set()
        conversation_history: List[str] = []
        final_answer: str = ""
        steps_taken: int = 0
        is_ambiguous: bool = False
        resolved_meaning: Optional[str] = None

        await self._emit(status_callback, "thinking", "Starting deep reasoning...")

        user_prompt = build_react_prompt(prompt, tools_text)
        conversation_history.append(f"User: {user_prompt}")

        while steps_taken < self.max_steps:
            full_conversation = "\n\n".join(conversation_history)

            response = await self.llm_provider.generate(
                prompt=full_conversation,
                system=system_prompt,
                temperature=0.2,
                max_tokens=512,
            )

            parsed = parse_react_response(response.text)
            logger.info("ReAct step %s — Thought: %s", steps_taken + 1, parsed["thought"][:100])
            logger.info("ReAct step %s — Action: %s", steps_taken + 1, parsed["action"])
            await self._emit(status_callback, "react_step", f"Step {steps_taken + 1}: {parsed['thought'][:150]}")

            conversation_history.append(response.text)

            action = parsed["action"]

            if action == "web_search":
                query_text = parsed["action_input"].get("query", str(parsed["action_input"]))
                await self._emit(status_callback, "searching", f"Searching: {query_text[:100]}")
                results = await self.search_provider.search(query_text)
                new_count = 0
                for source in results:
                    if source.url not in seen_urls:
                        seen_urls.add(source.url)
                        collected_sources.append(source)
                        new_count += 1
                observation = (
                    f"Found {new_count} new sources ({len(collected_sources)} total). "
                    "Top results: " + ", ".join([s.title[:50] for s in results[:3]])
                )
                conversation_history.append(format_observation("web_search", observation))

            elif action == "disambiguate":
                await self._emit(status_callback, "disambiguating", "Resolving ambiguous term...")
                term = parsed["action_input"].get("term", prompt)
                candidates = parsed["action_input"].get("candidates", [])
                if candidates:
                    formatted = format_candidate_meanings(candidates)
                    dis_prompt = DISAMBIGUATION_USER_TEMPLATE.format(
                        query=prompt, candidate_meanings=formatted, domain="general"
                    )
                    dis_response = await self.llm_provider.generate(
                        prompt=dis_prompt, system=DISAMBIGUATION_SYSTEM_PROMPT, temperature=0.1
                    )
                    dis_parsed = parse_llm_json(dis_response.text)
                    resolved_meaning = dis_parsed.get("resolved_meaning", None)
                    is_ambiguous = True
                    observation = (
                        f"Resolved '{term}' to: {resolved_meaning}"
                        if resolved_meaning
                        else f"Could not resolve '{term}'"
                    )
                else:
                    observation = f"No candidate meanings provided for '{term}'. Try searching first to understand the term."
                conversation_history.append(format_observation("disambiguate", observation))

            elif action == "analyze_sources":
                await self._emit(status_callback, "scoring", f"Analyzing {len(collected_sources)} sources...")
                scored = []
                for source in collected_sources:
                    authority = get_domain_authority_score(source.url)
                    relevance = compute_relevance_score(prompt, source.snippet)
                    quality = round((0.6 * authority) + (0.4 * relevance), 2)
                    scored.append((source, quality))
                scored.sort(key=lambda x: x[1], reverse=True)
                top_sources = [f"{s.title[:40]} (quality={q})" for s, q in scored[:5]]
                observation = f"Analyzed {len(collected_sources)} sources. Top 5 by quality:\n" + "\n".join(top_sources)

                collected_sources_scored = []
                for source, quality in scored:
                    collected_sources_scored.append(ScoredSource(
                        id=source.id,
                        title=source.title,
                        url=source.url,
                        snippet=source.snippet,
                        published_at=source.published_at,
                        domain_authority=get_domain_authority_score(source.url),
                        relevance_score=compute_relevance_score(prompt, source.snippet),
                        quality_score=quality,
                    ))
                collected_sources = collected_sources_scored
                conversation_history.append(format_observation("analyze_sources", observation))

            elif action == "synthesize":
                await self._emit(status_callback, "synthesizing", "Writing final answer...")
                sources_for_synthesis = collected_sources[:10]
                synth_prompt = build_synthesis_prompt(prompt, sources_for_synthesis)
                synth_response = await self.llm_provider.generate(
                    prompt=synth_prompt,
                    system=SYNTHESIS_SYSTEM_PROMPT,
                    temperature=0.3,
                )
                final_answer = synth_response.text.strip()
                observation = f"Synthesized answer ({len(final_answer)} chars) from {len(sources_for_synthesis)} sources."
                conversation_history.append(format_observation("synthesize", observation))

            elif action == "finish":
                if not final_answer:
                    final_answer = parsed["action_input"].get("answer", "")
                logger.info("ReAct finished after %s steps", steps_taken + 1)
                await self._emit(status_callback, "done", f"Research complete in {steps_taken + 1} steps")
                steps_taken += 1
                break

            else:
                observation = (
                    f"Unknown action '{parsed['action']}'. "
                    "Available actions: web_search, disambiguate, analyze_sources, synthesize, finish"
                )
                conversation_history.append(format_observation("error", observation))

            steps_taken += 1

        if not final_answer and collected_sources:
            await self._emit(status_callback, "synthesizing", "Reached max steps, finalizing answer...")
            sources_for_synthesis = collected_sources[:10]
            synth_prompt = build_synthesis_prompt(prompt, sources_for_synthesis)
            synth_response = await self.llm_provider.generate(
                prompt=synth_prompt, system=SYNTHESIS_SYSTEM_PROMPT
            )
            final_answer = synth_response.text.strip()

        if not final_answer:
            final_answer = f"I couldn't find enough information to answer: '{prompt}'. Try rephrasing your question."

        cited_numbers: Set[int] = set()
        for match in re.findall(r"\[(\d+)\]", final_answer):
            cited_numbers.add(int(match))

        citations = []
        for i, source in enumerate(collected_sources[:10]):
            if (i + 1) in cited_numbers:
                citations.append(Citation(
                    source_id=source.id,
                    url=source.url,
                    title=source.title,
                    quotes=source.snippet[:200],
                    evidence=source.snippet,
                    confidence=getattr(source, "quality_score", 0.5),
                ))

        quality_scores = [getattr(s, "quality_score", 0.4) for s in collected_sources[:10]]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        confidence = round(
            max(0.1, min(0.95,
                0.35 * avg_quality
                + 0.30 * min(len(collected_sources) / 8, 1.0)
                + 0.20 * 0.5
                + 0.15
            )), 2
        )

        return {
            "status": "success",
            "answer": final_answer,
            "prompt": prompt,
            "citations": citations,
            "confidence": confidence,
            "query_type": "react",
            "resolved_meaning": resolved_meaning,
            "react_steps": steps_taken,
        }
