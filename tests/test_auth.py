import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database.connection import engine, Base, async_session
from app.database.models import User
from app.auth.security import hash_password, create_access_token, verify_password


class TestPasswordHashing:
    """Test password hashing utilities."""

    def test_hash_is_not_plaintext(self):
        """Hashed password should not equal the original."""
        hashed = hash_password("mysecretpassword")
        assert hashed != "mysecretpassword"

    def test_verify_correct_password(self):
        """verify_password should return True for matching passwords."""
        hashed = hash_password("correcthorse")
        assert verify_password("correcthorse", hashed) is True

    def test_verify_wrong_password(self):
        """verify_password should return False for wrong passwords."""
        hashed = hash_password("correcthorse")
        assert verify_password("wrongpassword", hashed) is False

    def test_same_password_different_hashes(self):
        """Hashing the same password twice should produce different hashes (bcrypt salting)."""
        hash1 = hash_password("samepassword")
        hash2 = hash_password("samepassword")
        assert hash1 != hash2

    def test_both_hashes_verify(self):
        """Both salted hashes should still verify correctly."""
        hash1 = hash_password("samepassword")
        hash2 = hash_password("samepassword")
        assert verify_password("samepassword", hash1) is True
        assert verify_password("samepassword", hash2) is True


class TestAccessToken:
    """Test JWT token creation."""

    def test_token_is_string(self):
        """create_access_token should return a string."""
        token = create_access_token({"sub": "user-123"})
        assert isinstance(token, str)

    def test_token_is_not_empty(self):
        """Token should be a non-empty string."""
        token = create_access_token({"sub": "user-123"})
        assert len(token) > 0

    def test_different_users_different_tokens(self):
        """Different user IDs should produce different tokens."""
        token1 = create_access_token({"sub": "user-1"})
        token2 = create_access_token({"sub": "user-2"})
        assert token1 != token2
