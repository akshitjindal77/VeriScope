from app.agents.research_agent import ResearchAgent
import logging

logger = logging.getLogger(__name__)

async def run_research(prompt: str) -> str:
    logger.info("run_research started")
    logger.info("Prompt Length: %s", len(prompt))

    agent = ResearchAgent()
    result = await agent.run(prompt)
    
    logger.info("Agent returned %s citations", len(result.get("citations", [])))
    
    return result
