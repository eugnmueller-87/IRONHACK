"""
news_api.py — Thin wrapper around the NewsAPI REST endpoint.

Handles rate limiting (token-bucket style) and normalises the raw JSON
response into a flat list of dicts that the rest of the app expects.
"""
import requests
import time
from config import Config


class NewsAPI:
    """Fetch news articles from newsapi.org."""

    def __init__(self):
        self.api_key = Config.NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2"

        # Rate-limiting state: track when we last made a call
        self.last_call_time = 0
        # Minimum gap between requests to stay under NEWS_API_RPM
        self.min_interval = 60.0 / Config.NEWS_API_RPM

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _wait_if_needed(self):
        """Sleep just long enough to respect the configured rate limit."""
        elapsed = time.time() - self.last_call_time
        if elapsed < self.min_interval:
            wait_time = self.min_interval - elapsed
            print(f"Rate limiting News API: waiting {wait_time:.2f}s...")
            time.sleep(wait_time)
        self.last_call_time = time.time()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def fetch_top_headlines(self, category="technology", country="us", max_articles=5):
        """
        Fetch top headlines and return them as a list of normalised dicts.

        Args:
            category:     One of business | entertainment | health |
                          science | sports | technology.
            country:      ISO 3166-1 alpha-2 country code (e.g. "us", "gb").
            max_articles: How many articles to return (max 100 per NewsAPI plan).

        Returns:
            List of dicts with keys: title, description, content,
            url, source, published_at.
        """
        self._wait_if_needed()

        params = {
            "apiKey": self.api_key,
            "category": category,
            "country": country,
            "pageSize": max_articles,
        }

        try:
            response = requests.get(
                f"{self.base_url}/top-headlines",
                params=params,
                timeout=Config.REQUEST_TIMEOUT,
            )
            response.raise_for_status()  # raises HTTPError for 4xx / 5xx
            data = response.json()

            if data.get("status") != "ok":
                raise Exception(f"News API error: {data.get('message')}")

            # Normalise: keep only the fields the summariser actually uses
            processed = []
            for article in data.get("articles", []):
                processed.append({
                    "title":        article.get("title", ""),
                    "description":  article.get("description", ""),
                    "content":      article.get("content", ""),
                    "url":          article.get("url", ""),
                    "source":       article.get("source", {}).get("name", "Unknown"),
                    "published_at": article.get("publishedAt", ""),
                })

            print(f"✓ Fetched {len(processed)} articles from News API")
            return processed

        except requests.exceptions.RequestException as e:
            print(f"✗ Error fetching news: {e}")
            return []


# ---------------------------------------------------------------------------
# Quick smoke-test — run this file directly to verify your News API key works
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    api = NewsAPI()
    articles = api.fetch_top_headlines(category="technology", max_articles=3)

    for i, article in enumerate(articles, 1):
        print(f"\n{i}. {article['title']}")
        print(f"   Source: {article['source']}")
        print(f"   URL:    {article['url']}")
