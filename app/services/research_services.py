from app.agents.research_agent import ResearchAgent

async def run_research(prompt: str) -> str:
    agent = ResearchAgent()
    result = await agent.run(prompt)
    return result