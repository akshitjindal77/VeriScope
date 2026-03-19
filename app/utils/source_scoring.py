from urllib.parse import urlparse

TIER_1_DOMAINS = [
    ".gov", ".edu", ".ac.uk",
    "aws.amazon.com", "cloud.google.com", "azure.microsoft.com",
    "developer.mozilla.org", "docs.python.org", "docs.oracle.com",
    "arxiv.org", "research.google", "ai.meta.com", "research.ibm.com",
    "blogs.nvidia.com", "openai.com", "anthropic.com", "huggingface.co",
    "nature.com", "science.org", "ieee.org", "acm.org",
]

TIER_2_DOMAINS = [
    "wikipedia.org", "britannica.com", "stanford.edu",
    "techcrunch.com", "arstechnica.com", "wired.com", "theverge.com",
    "stackoverflow.com", "github.com", "medium.com", "towardsdatascience.com",
    "mckinsey.com", "hbr.org", "reuters.com", "bbc.com",
    "ibm.com", "oracle.com", "elastic.co", "mongodb.com", "pinecone.io",
]

STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "what", "how", "why",
    "when", "where", "which", "who", "do", "does", "in", "of", "for",
    "to", "and", "or", "it", "this", "that", "with", "on", "at", "by",
    "from", "can", "will", "about",
}


def get_domain_authority_score(url: str) -> float:
    hostname = urlparse(url).hostname or ""
    if hostname.startswith("www."):
        hostname = hostname[4:]

    for domain in TIER_1_DOMAINS:
        if hostname == domain or hostname.endswith(domain):
            return 1.0

    if hostname.endswith(".gov") or hostname.endswith(".edu") or hostname.endswith(".ac.uk"):
        return 1.0

    for domain in TIER_2_DOMAINS:
        if hostname == domain or hostname.endswith("." + domain):
            return 0.7

    return 0.4


def compute_relevance_score(query: str, snippet: str) -> float:
    query_words = [w for w in query.lower().split() if w not in STOP_WORDS]
    if not query_words:
        return 0.0
    snippet_lower = snippet.lower()
    matches = sum(1 for w in query_words if w in snippet_lower)
    return max(0.0, min(1.0, matches / len(query_words)))


def compute_source_quality(url: str, query: str, snippet: str) -> float:
    authority = get_domain_authority_score(url)
    relevance = compute_relevance_score(query, snippet)
    return round((0.6 * authority) + (0.4 * relevance), 2)
