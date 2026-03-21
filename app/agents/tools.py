from dataclasses import dataclass
from typing import List


@dataclass
class Tool:
    name: str
    description: str
    parameters: str


AVAILABLE_TOOLS: List[Tool] = [
    Tool(
        name="web_search",
        description="Search the web for information on a specific topic. Use this when you need to find sources about a particular query. You can call this multiple times with different queries to get diverse results.",
        parameters="query (str): The search query to execute",
    ),
    Tool(
        name="disambiguate",
        description="Resolve an ambiguous term to its most likely meaning in context. Use this when a query contains a term that could mean different things (e.g., 'Python' could be a language or a snake, 'RAG' could be an AI technique or a piece of cloth).",
        parameters="term (str): The ambiguous term, candidates (list): Possible meanings",
    ),
    Tool(
        name="analyze_sources",
        description="Score and rank the sources collected so far by quality and relevance. Use this after collecting sources to see which ones are most valuable. Returns the top sources sorted by quality.",
        parameters="No parameters — operates on all sources collected so far",
    ),
    Tool(
        name="synthesize",
        description="Write a final answer from the collected sources. Only use this when you have enough high-quality sources to write a comprehensive answer. This is typically the last action before finishing.",
        parameters="No parameters — uses the query and all collected sources",
    ),
    Tool(
        name="finish",
        description="End the research process and return the final answer. Use this after synthesize has produced a good answer.",
        parameters="answer (str): The final answer text",
    ),
]


def format_tools_for_prompt() -> str:
    lines = ["Available tools:"]
    for i, tool in enumerate(AVAILABLE_TOOLS, start=1):
        lines.append(f"{i}. {tool.name}: {tool.description}")
        lines.append(f"   Parameters: {tool.parameters}")
        lines.append("")
    return "\n".join(lines).rstrip()
