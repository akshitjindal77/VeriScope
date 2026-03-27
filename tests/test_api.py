import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database.connection import engine, Base, async_session
from app.database.models import User
from app.auth.security import hash_password, create_access_token


@pytest_asyncio.fixture
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(setup_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_headers(setup_db):
    """Create a test user and return auth headers."""
    session = async_session()
    try:
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash=hash_password("password123"),
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        token = create_access_token({"sub": user.id})
        return {"Authorization": f"Bearer {token}"}
    finally:
        await session.close()


class TestHealthEndpoint:
    @pytest.mark.asyncio
    async def test_health_returns_ok(self, client):
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


class TestAuthEndpoints:
    @pytest.mark.asyncio
    async def test_signup_success(self, client):
        response = await client.post("/auth/signup", json={
            "email": "new@example.com",
            "username": "newuser",
            "password": "securepass123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    @pytest.mark.asyncio
    async def test_signup_duplicate_email(self, client):
        # First signup
        await client.post("/auth/signup", json={
            "email": "dup@example.com",
            "username": "user1",
            "password": "pass123"
        })
        # Duplicate
        response = await client.post("/auth/signup", json={
            "email": "dup@example.com",
            "username": "user2",
            "password": "pass456"
        })
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_login_success(self, client, auth_headers):
        response = await client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        assert response.status_code == 200
        assert "access_token" in response.json()

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client, auth_headers):
        response = await client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_me_authenticated(self, client, auth_headers):
        response = await client.get("/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_me_unauthenticated(self, client):
        response = await client.get("/auth/me")
        assert response.status_code in [401, 403]


class TestResearchEndpoint:
    @pytest.mark.asyncio
    async def test_research_requires_auth(self, client):
        response = await client.post("/research", json={"prompt": "test"})
        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_research_empty_prompt(self, client, auth_headers):
        response = await client.post("/research", json={"prompt": ""}, headers=auth_headers)
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_research_prompt_too_long(self, client, auth_headers):
        long_prompt = "a" * 2001
        response = await client.post("/research", json={"prompt": long_prompt}, headers=auth_headers)
        assert response.status_code == 413

    @pytest.mark.asyncio
    async def test_invalid_mode(self, client, auth_headers):
        response = await client.post("/research", json={
            "prompt": "test",
            "mode": "turbo"
        }, headers=auth_headers)
        assert response.status_code == 400


class TestSessionEndpoints:
    @pytest.mark.asyncio
    async def test_list_sessions_empty(self, client, auth_headers):
        response = await client.get("/sessions", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == [] or isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_create_session(self, client, auth_headers):
        response = await client.post("/sessions", json={"title": "Test Session"}, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Session"

    @pytest.mark.asyncio
    async def test_sessions_require_auth(self, client):
        response = await client.get("/sessions")
        assert response.status_code in [401, 403]
