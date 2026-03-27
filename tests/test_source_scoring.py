import pytest
from app.utils.source_scoring import get_domain_authority_score, compute_relevance_score, compute_source_quality


class TestDomainAuthority:
    """Test the domain authority scoring system."""

    def test_tier1_government(self):
        """Government domains should score 1.0."""
        assert get_domain_authority_score("https://www.cdc.gov/health") == 1.0
        assert get_domain_authority_score("https://data.gov/datasets") == 1.0

    def test_tier1_education(self):
        """Education domains should score 1.0."""
        assert get_domain_authority_score("https://cs.stanford.edu/research") == 1.0
        assert get_domain_authority_score("https://mit.edu/courses") == 1.0

    def test_tier1_major_tech(self):
        """Major tech company docs should score 1.0."""
        assert get_domain_authority_score("https://aws.amazon.com/what-is/rag") == 1.0
        assert get_domain_authority_score("https://cloud.google.com/ai") == 1.0
        assert get_domain_authority_score("https://arxiv.org/abs/2005.11401") == 1.0

    def test_tier2_knowledge_bases(self):
        """Wikipedia and established publications should score 0.7."""
        assert get_domain_authority_score("https://en.wikipedia.org/wiki/RAG") == 0.7
        assert get_domain_authority_score("https://stackoverflow.com/questions/123") == 0.7

    def test_tier3_default(self):
        """Unknown domains should score 0.4."""
        assert get_domain_authority_score("https://random-blog.com/post") == 0.4
        assert get_domain_authority_score("https://some-site.xyz/article") == 0.4

    def test_www_stripping(self):
        """www prefix should be stripped before matching."""
        score_with = get_domain_authority_score("https://www.arxiv.org/paper")
        score_without = get_domain_authority_score("https://arxiv.org/paper")
        assert score_with == score_without

    def test_empty_url(self):
        """Empty or invalid URLs should return default score."""
        assert get_domain_authority_score("") == 0.4
        assert get_domain_authority_score("not-a-url") == 0.4


class TestRelevanceScore:
    """Test keyword relevance scoring."""

    def test_full_match(self):
        """All query words in snippet should score high."""
        score = compute_relevance_score("retrieval augmented generation", "retrieval augmented generation is a technique")
        assert score >= 0.8

    def test_partial_match(self):
        """Some query words in snippet should score medium."""
        score = compute_relevance_score("retrieval augmented generation", "generation of text content")
        assert 0.0 < score < 1.0

    def test_no_match(self):
        """No query words in snippet should score 0."""
        score = compute_relevance_score("quantum computing", "the weather today is sunny")
        assert score == 0.0

    def test_stop_words_ignored(self):
        """Stop words should not count toward matching."""
        score = compute_relevance_score("what is the meaning of life", "meaning of life is subjective")
        # "what", "is", "the", "of" are stop words — only "meaning" and "life" should match
        assert score > 0.0

    def test_case_insensitive(self):
        """Matching should be case insensitive."""
        score1 = compute_relevance_score("Python", "python programming language")
        score2 = compute_relevance_score("python", "Python Programming Language")
        assert score1 == score2

    def test_empty_inputs(self):
        """Empty inputs should return 0."""
        assert compute_relevance_score("", "some text") == 0.0
        assert compute_relevance_score("query", "") == 0.0


class TestSourceQuality:
    """Test combined quality scoring."""

    def test_high_quality_source(self):
        """Tier 1 domain with relevant snippet should score high."""
        score = compute_source_quality(
            "https://aws.amazon.com/what-is/rag",
            "retrieval augmented generation",
            "RAG is a technique for retrieval augmented generation"
        )
        assert score >= 0.7

    def test_low_quality_source(self):
        """Tier 3 domain with irrelevant snippet should score low."""
        score = compute_source_quality(
            "https://random-blog.xyz/post",
            "retrieval augmented generation",
            "today we discuss cooking recipes"
        )
        assert score < 0.5

    def test_quality_between_0_and_1(self):
        """Quality should always be between 0 and 1."""
        score = compute_source_quality("https://example.com", "test", "test content")
        assert 0.0 <= score <= 1.0
