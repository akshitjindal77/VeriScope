import pytest
from app.services.research_services import make_cache_key


class TestCacheKey:
    """Test cache key normalization."""

    def test_case_insensitive(self):
        """Upper and lower case should produce same key."""
        key1 = make_cache_key("What is RAG?", "linear")
        key2 = make_cache_key("what is rag?", "linear")
        assert key1 == key2

    def test_punctuation_stripped(self):
        """Trailing punctuation should not affect key."""
        key1 = make_cache_key("What is RAG", "linear")
        key2 = make_cache_key("What is RAG?", "linear")
        key3 = make_cache_key("What is RAG!", "linear")
        assert key1 == key2 == key3

    def test_whitespace_normalized(self):
        """Multiple spaces should be collapsed."""
        key1 = make_cache_key("what is rag", "linear")
        key2 = make_cache_key("what  is   rag", "linear")
        assert key1 == key2

    def test_different_modes_different_keys(self):
        """Same prompt with different modes should have different keys."""
        key1 = make_cache_key("What is RAG?", "linear")
        key2 = make_cache_key("What is RAG?", "react")
        assert key1 != key2

    def test_different_prompts_different_keys(self):
        """Different prompts should have different keys."""
        key1 = make_cache_key("What is RAG?", "linear")
        key2 = make_cache_key("What is Python?", "linear")
        assert key1 != key2

    def test_leading_trailing_spaces(self):
        """Leading and trailing spaces should be stripped."""
        key1 = make_cache_key("what is rag", "linear")
        key2 = make_cache_key("  what is rag  ", "linear")
        assert key1 == key2
