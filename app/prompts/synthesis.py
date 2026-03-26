from typing import List

from app.models.research_models import Source

SYNTHESIS_SYSTEM_PROMPT = """You are a research synthesis assistant. Your job is to take a user's question and a set of source snippets, then produce a clear, well-organized answer.

Rules:
- ONLY use information from the provided sources. Never add facts not present in the snippets.
- Reference sources by their number in square brackets like [1], [2], etc.
- If sources disagree with each other, acknowledge the disagreement.
- If the sources don't contain enough information to fully answer the question, say so honestly.
- Write a detailed and comprehensive answer. Aim for 5-6 paragraphs minimum. Each paragraph should be 4-6 sentences long. Cover the topic from multiple angles: definition, how it works, why it matters, real-world applications, and any important nuances or debates.
- Do not summarize too aggressively. The user wants depth, not brevity. Explain concepts thoroughly as if writing for someone encountering this topic for the first time.
- Do NOT include a summary paragraph at the end that repeats what you already said. Every paragraph should contain NEW information and new insights, not restate previous paragraphs.
- ALWAYS format source references with square brackets like [1], [2], [3]. Never list source numbers without brackets. Never write '124567' or '1,2,3' — always write [1][2][4][5][6][7]. Every citation must appear inline within the sentence it supports.
- Do not repeat the question back. Start directly with the answer.
- Write in a neutral, informative tone."""

SYNTHESIS_USER_TEMPLATE = """Question: {query}

Sources:
{sources_block}

Using only the sources above, write a comprehensive answer to the question. Cite sources using [1], [2], etc."""


def build_sources_block(sources: List[Source]) -> str:
    if not sources:
        return "No sources available."
    parts = []
    for i, source in enumerate(sources, start=1):
        parts.append(
            f"[{i}] Title: {source.title}\n"
            f"URL: {source.url}\n"
            f"Content: {source.snippet}"
        )
    return "\n\n".join(parts)


def build_synthesis_prompt(query: str, sources: List[Source]) -> str:
    sources_block = build_sources_block(sources)
    return SYNTHESIS_USER_TEMPLATE.format(query=query, sources_block=sources_block)
