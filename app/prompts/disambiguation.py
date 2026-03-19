from typing import List

DISAMBIGUATION_SYSTEM_PROMPT = (
    "You are a query disambiguation assistant for a research engine. When a query contains ambiguous terms, "
    "you determine the most likely intended meaning based on context.\n\n"
    "You must respond with ONLY valid JSON, no markdown, no explanation, no backticks. Just the raw JSON object.\n\n"
    "The JSON must have exactly these fields:\n"
    '- resolved_meaning: a short description of the chosen meaning (e.g. "Retrieval-Augmented Generation, an AI technique")\n'
    "- reasoning: one sentence explaining why you chose this meaning\n"
    "- search_queries: a list of 3-5 specific search queries targeting ONLY the resolved meaning. "
    "Make them specific enough that they won't return results for other meanings."
)

DISAMBIGUATION_USER_TEMPLATE = (
    "The following research query contains an ambiguous term:\n\n"
    "Query: {query}\n"
    "Detected domain: {domain}\n"
    "Possible meanings:\n"
    "{candidate_meanings}\n\n"
    "This is a research engine primarily used for technical and knowledge queries. "
    "Choose the most likely intended meaning and generate search queries that specifically target that meaning. "
    "Avoid queries that would return results for the other meanings.\n\n"
    "Respond with ONLY the JSON object. No other text."
)


def format_candidate_meanings(candidates: List[str]) -> str:
    if not candidates:
        return "No candidate meanings available."
    return "\n".join(f"{i + 1}. {meaning}" for i, meaning in enumerate(candidates))