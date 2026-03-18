from app.agents.research_agent import ResearchAgent
from app.providers.web_search_provider import WebSearchProvider
from app.providers.brave_search_provider import BraveSearchProvider
from app.providers.ollama_provider import OllamaProvider
from app.providers.mock_llm_provider import MockLLMProvider
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)

def _build_provider():
    if settings.WEB_SEARCH_PROVIDER.lower() == "brave":
        return BraveSearchProvider(settings)
    return WebSearchProvider(settings)

def _build_llm_provider():
    if settings.LLM_PROVIDER.lower() == "ollama":
        return OllamaProvider(settings)
    return MockLLMProvider()

provider = _build_provider()
llm_provider = _build_llm_provider()
agent = ResearchAgent(search_provider=provider, llm_provider=llm_provider)


async def run_research(prompt: str) -> dict:
    logger.info("run_research started")
    logger.info("Prompt Length: %s", len(prompt))

    result = await agent.run(prompt)
    
    logger.info("Agent returned %s citations", len(result.get("citations", [])))
    
    return result
