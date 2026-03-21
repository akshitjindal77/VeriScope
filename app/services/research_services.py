from app.agents.research_agent import ResearchAgent
from app.agents.react_agent import ReactResearchAgent
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
react_agent = ReactResearchAgent(search_provider=provider, llm_provider=llm_provider, settings=settings)


async def run_research(prompt: str, mode: str = "linear") -> dict:
    logger.info("run_research started")
    logger.info("Prompt Length: %s", len(prompt))

    if mode == "react":
        logger.info("Using ReAct agent mode")
        result = await react_agent.run(prompt)
    else:
        logger.info("Using linear agent mode")
        result = await agent.run(prompt)

    logger.info("Agent returned %s citations", len(result.get("citations", [])))

    return result
