import pytest
from app.utils.json_parser import parse_llm_json


class TestJsonParser:
    """Test safe JSON extraction from LLM responses."""

    def test_clean_json(self):
        """Should parse clean JSON directly."""
        result = parse_llm_json('{"key": "value", "count": 42}')
        assert result == {"key": "value", "count": 42}

    def test_json_with_markdown_fences(self):
        """Should strip ```json fences."""
        result = parse_llm_json('```json\n{"key": "value"}\n```')
        assert result == {"key": "value"}

    def test_json_with_preamble(self):
        """Should extract JSON even with leading text."""
        result = parse_llm_json('Here is the analysis:\n{"query_type": "factual"}')
        assert result == {"query_type": "factual"}

    def test_json_with_trailing_text(self):
        """Should extract JSON even with trailing text."""
        result = parse_llm_json('{"is_ambiguous": true}\nHope this helps!')
        assert result == {"is_ambiguous": True}

    def test_invalid_json(self):
        """Should return empty dict for unparseable content."""
        result = parse_llm_json("This is not JSON at all")
        assert result == {}

    def test_empty_input(self):
        """Should return empty dict for empty input."""
        result = parse_llm_json("")
        assert result == {}

    def test_nested_json(self):
        """Should handle nested JSON objects."""
        result = parse_llm_json('{"queries": ["q1", "q2"], "meta": {"count": 2}}')
        assert result["queries"] == ["q1", "q2"]
        assert result["meta"]["count"] == 2
