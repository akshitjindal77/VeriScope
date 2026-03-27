import pytest
import pytest_asyncio
from app.agents.research_agent import ResearchAgent
from app.providers.mock_search_provider import MockSearchProvider
from app.providers.mock_llm_provider import MockLLMProvider
from app.models.research_models import ResearchPlan

@pytest.fixture
def agent():
    return ResearchAgent(
        search_provider=MockSearchProvider(),
        llm_provider=MockLLMProvider(),
    )

class TestPlanStep:
    """Test the query planning step."""

    @pytest.mark.asyncio
    async def test_returns_research_plan(self, agent):
        """plan_step should return a ResearchPlan with queries."""
        plan = await agent.plan_step("What is RAG?")
        # With mock LLM, should fall back to static templates
        assert isinstance(plan, tuple) or isinstance(plan, ResearchPlan)

    @pytest.mark.asyncio
    async def test_generates_search_queries(self, agent):
        """plan_step should produce at least one search query."""
        result = await agent.plan_step("What is Python?")
        # Handle both tuple return (plan, analysis) and plain ResearchPlan
        plan = result[0] if isinstance(result, tuple) else result
        assert len(plan.search_queries) > 0


class TestSearchStep:
    """Test the web search step."""

    @pytest.mark.asyncio
    async def test_returns_sources(self, agent):
        """search_step should return a list of sources."""
        plan = ResearchPlan(
            sub_questions=["What is test?"],
            search_queries=["test query"]
        )
        sources = await agent.search_step(plan)
        assert len(sources) > 0

    @pytest.mark.asyncio
    async def test_deduplicates_by_url(self, agent):
        """search_step should not return duplicate URLs."""
        plan = ResearchPlan(
            sub_questions=["q1", "q2"],
            search_queries=["same query", "same query"]
        )
        sources = await agent.search_step(plan)
        urls = [s.url for s in sources]
        assert len(urls) == len(set(urls))


class TestAnalyzeStep:
    """Test the source analysis step."""

    def test_extracts_notes(self, agent):
        """analyze_step should extract non-empty snippets."""
        from app.models.research_models import Source
        sources = [
            Source(id="1", title="Test", url="http://test.com", snippet="This is content"),
            Source(id="2", title="Test 2", url="http://test2.com", snippet="More content"),
        ]
        notes = agent.analyze_step(sources)
        assert len(notes) == 2

    def test_removes_empty_snippets(self, agent):
        """analyze_step should skip sources with empty snippets."""
        from app.models.research_models import Source
        sources = [
            Source(id="1", title="Test", url="http://test.com", snippet="Has content"),
            Source(id="2", title="Empty", url="http://empty.com", snippet=""),
            Source(id="3", title="Spaces", url="http://spaces.com", snippet="   "),
        ]
        notes = agent.analyze_step(sources)
        assert len(notes) == 1

    def test_deduplicates_notes(self, agent):
        """analyze_step should remove duplicate snippets."""
        from app.models.research_models import Source
        sources = [
            Source(id="1", title="T1", url="http://a.com", snippet="Same content"),
            Source(id="2", title="T2", url="http://b.com", snippet="Same content"),
        ]
        notes = agent.analyze_step(sources)
        assert len(notes) == 1


class TestFullPipeline:
    """Test the complete research pipeline."""

    @pytest.mark.asyncio
    async def test_run_returns_result(self, agent):
        """run() should return a complete result dict."""
        result = await agent.run("What is testing?")
        assert result["status"] == "success"
        assert "answer" in result
        assert "citations" in result
        assert "confidence" in result

    @pytest.mark.asyncio
    async def test_confidence_between_0_and_1(self, agent):
        """Confidence should be between 0.1 and 0.95."""
        result = await agent.run("What is testing?")
        assert 0.1 <= result["confidence"] <= 0.95

    @pytest.mark.asyncio
    async def test_empty_prompt_still_works(self, agent):
        """Pipeline should handle edge cases gracefully."""
        result = await agent.run("x")
        assert result["status"] == "success"
