"""
test_summarizer.py — Unit tests for the news summariser pipeline.

All external HTTP calls and LLM API calls are mocked so the test suite
runs offline and never costs any API credits.

Run with:  pytest test_summarizer.py -v
"""
import pytest
from unittest.mock import Mock, patch
from news_api import NewsAPI
from llm_providers import LLMProviders, CostTracker, count_tokens
from summarizer import NewsSummarizer


# ===========================================================================
# CostTracker
# ===========================================================================

class TestCostTracker:
    """Verify cost calculation and budget enforcement."""

    def test_track_request(self):
        """A single request should produce a positive cost and one record."""
        tracker = CostTracker()
        cost = tracker.track_request("openai", "gpt-4o-mini", 100, 500)

        assert cost > 0
        assert tracker.total_cost == cost
        assert len(tracker.requests) == 1

    def test_get_summary(self):
        """Summary should aggregate tokens and costs from all requests."""
        tracker = CostTracker()
        tracker.track_request("openai",    "gpt-4o-mini",               100, 200)
        tracker.track_request("anthropic", "claude-3-5-sonnet-20241022", 150, 300)

        summary = tracker.get_summary()

        assert summary["total_requests"]      == 2
        assert summary["total_cost"]          > 0
        assert summary["total_input_tokens"]  == 250
        assert summary["total_output_tokens"] == 500

    def test_budget_check_passes(self):
        """Small spend should not raise."""
        tracker = CostTracker()
        tracker.track_request("openai", "gpt-4o-mini", 100, 100)
        tracker.check_budget(10.00)  # should be fine

    def test_budget_check_raises(self):
        """Spending above the daily budget must raise an exception."""
        tracker = CostTracker()
        tracker.total_cost = 15.00
        with pytest.raises(Exception, match="budget.*exceeded"):
            tracker.check_budget(10.00)


# ===========================================================================
# Token counting
# ===========================================================================

class TestTokenCounting:

    def test_count_tokens_returns_positive(self):
        """Token count for any non-empty string must be > 0."""
        assert count_tokens("Hello, how are you?") > 0

    def test_count_tokens_less_than_chars(self):
        """Tokens should be fewer than characters (BPE compression)."""
        text = "Hello, how are you today?"
        assert count_tokens(text) < len(text)


# ===========================================================================
# NewsAPI
# ===========================================================================

class TestNewsAPI:

    @patch("news_api.requests.get")
    def test_fetch_top_headlines(self, mock_get):
        """Successful API response should be normalised to our flat schema."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ok",
            "articles": [
                {
                    "title":       "Test Article",
                    "description": "Test description",
                    "content":     "Test content",
                    "url":         "https://example.com",
                    "source":      {"name": "Test Source"},
                    "publishedAt": "2026-01-19",
                }
            ],
        }
        mock_get.return_value = mock_response

        api      = NewsAPI()
        articles = api.fetch_top_headlines(max_articles=1)

        assert len(articles) == 1
        assert articles[0]["title"]  == "Test Article"
        assert articles[0]["source"] == "Test Source"

    @patch("news_api.requests.get")
    def test_fetch_returns_empty_list_on_error(self, mock_get):
        """Network errors should return an empty list, not raise."""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("no network")

        api      = NewsAPI()
        articles = api.fetch_top_headlines()

        assert articles == []


# ===========================================================================
# LLMProviders
# ===========================================================================

class TestLLMProviders:

    @patch("llm_providers.OpenAI")
    def test_ask_openai(self, mock_openai_class):
        """ask_openai() should forward the prompt and return the response text."""
        mock_client   = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        providers = LLMProviders()
        providers.openai_client = mock_client  # swap in the mock directly

        response = providers.ask_openai("Test prompt")

        assert response == "Test response"
        assert mock_client.chat.completions.create.called


# ===========================================================================
# NewsSummarizer (integration-level, all LLM calls mocked)
# ===========================================================================

class TestNewsSummarizer:

    def test_initialization(self):
        """Summariser should set up both sub-components on construction."""
        summarizer = NewsSummarizer()
        assert summarizer.news_api      is not None
        assert summarizer.llm_providers is not None

    @patch.object(LLMProviders, "ask_openai")
    @patch.object(LLMProviders, "ask_anthropic")
    def test_summarize_article(self, mock_anthropic, mock_openai):
        """summarize_article() should call both providers and return merged result."""
        mock_openai.return_value    = "Test summary"
        mock_anthropic.return_value = "Positive sentiment"

        summarizer = NewsSummarizer()
        article = {
            "title":        "Test Article",
            "description":  "Test description",
            "content":      "Test content",
            "url":          "https://example.com",
            "source":       "Test Source",
            "published_at": "2026-01-19",
        }

        result = summarizer.summarize_article(article)

        assert result["title"]     == "Test Article"
        assert result["summary"]   == "Test summary"
        assert result["sentiment"] == "Positive sentiment"
        assert mock_openai.called
        assert mock_anthropic.called

    @patch.object(LLMProviders, "ask_openai")
    @patch.object(LLMProviders, "ask_anthropic")
    def test_process_articles_skips_failures(self, mock_anthropic, mock_openai):
        """process_articles() should continue past articles that raise exceptions."""
        mock_openai.side_effect    = Exception("quota exceeded")
        mock_anthropic.side_effect = Exception("server error")

        summarizer = NewsSummarizer()
        articles   = [{"title": "A", "description": "", "content": "",
                        "url": "", "source": "", "published_at": ""}]

        results = summarizer.process_articles(articles)
        # Both providers failed → article is skipped, not raised
        assert results == []


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
