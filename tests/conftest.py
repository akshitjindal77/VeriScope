import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database.connection import engine, Base, async_session
from app.providers.mock_search_provider import MockSearchProvider
from app.providers.mock_llm_provider import MockLLMProvider
from app.agents.research_agent import ResearchAgent
from app.database.models import User
from app.auth.security import hash_password, create_access_token
import asyncio

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture
async def db_session():
    """Create a fresh database for each test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session = async_session()
    try:
        yield session
    finally:
        await session.close()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def client(db_session):
    """Create a test HTTP client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture
async def auth_token(db_session):
    """Create a test user and return a valid JWT token."""
    user = User(
        email="test@test.com",
        username="testuser",
        password_hash=hash_password("testpass123"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    token = create_access_token({"sub": user.id})
    return token

@pytest.fixture
def mock_agent():
    """Create a research agent with mock providers."""
    return ResearchAgent(
        search_provider=MockSearchProvider(),
        llm_provider=MockLLMProvider(),
    )
