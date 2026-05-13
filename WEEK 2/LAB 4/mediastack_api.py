"""
mediastack_api.py — Fetcher for the Mediastack live news API.
Docs: https://mediastack.com/documentation

Free-tier note: Mediastack's free plan uses plain HTTP (not HTTPS).
Upgrade to a paid plan to enable HTTPS.

Sign up and get your key at: https://mediastack.com/signup/free
"""
import requests
import time
from config import Config


class MediastackAPI:
    """Fetch news articles from mediastack.com."""

    # Free tier is HTTP only; paid tiers support HTTPS
    BASE_URL = "http://api.mediastack.com/v1"

    # Mediastack free plan: 500 requests/month — be conservative with RPM
    RPM = 10

    def __init__(self):
        self.access_key = Config.MEDIASTACK_API_KEY
        self.last_call_time = 0
        self.min_interval = 60.0 / self.RPM

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _wait_if_needed(self):
        """Throttle calls to stay within the free-plan rate limit."""
        elapsed = time.time() - self.last_call_time
        if elapsed < self.min_interval:
            wait_time = self.min_interval - elapsed
            print(f"Rate limiting Mediastack: waiting {wait_time:.2f}s...")
            time.sleep(wait_time)
        self.last_call_time = time.time()

    def _normalise(self, article: dict) -> dict:
        """Convert a raw Mediastack article dict into the app's flat schema."""
        return {
            "title":        article.get("title", ""),
            "description":  article.get("description", ""),
            # Mediastack doesn't have a separate 'content' field — reuse description
            "content":      article.get("description", ""),
            "url":          article.get("url", ""),
            "source":       article.get("source", "Unknown"),
            "published_at": article.get("published_at", ""),
        }

    def _fetch(self, params: dict) -> list:
        """
        Hit the /news endpoint with the given params and return normalised articles.
        Returns an empty list on any error so callers never have to handle exceptions.
        """
        self._wait_if_needed()

        params["access_key"] = self.access_key

        try:
            response = requests.get(
                f"{self.BASE_URL}/news",
                params=params,
                timeout=Config.REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()

            # Mediastack signals errors via an "error" key
            if "error" in data:
                code = data["error"].get("code", "unknown")
                msg  = data["error"].get("message", "")
                raise Exception(f"Mediastack error {code}: {msg}")

            articles = [self._normalise(a) for a in data.get("data", [])]
            print(f"[OK] Fetched {len(articles)} articles from Mediastack")
            return articles

        except requests.exceptions.RequestException as e:
            print(f"[ERR] Mediastack request failed: {e}")
            return []

    # ------------------------------------------------------------------
    # Public interface — mirrors the NewsAPI surface so they're swappable
    # ------------------------------------------------------------------

    def fetch_top_headlines(self, category="technology", country="us", max_articles=5) -> list:
        """
        Fetch latest articles filtered by category and country.

        Supported categories: general | business | entertainment |
                              health | science | sports | technology
        Country: ISO 3166-1 alpha-2 code, e.g. "us", "gb", "de".
        """
        return self._fetch({
            "categories": category,
            "countries":  country,
            "languages":  "en",
            "limit":      max_articles,
            "sort":       "published_desc",
        })

    def fetch_ai_news(self, max_articles=5) -> list:
        """
        Search for AI-focused articles using keyword filtering.

        Mediastack supports comma-separated keywords in the 'keywords' param.
        """
        keywords = (
            "artificial intelligence,machine learning,LLM,"
            "ChatGPT,OpenAI,Anthropic,deep learning"
        )
        return self._fetch({
            "keywords": keywords,
            "languages": "en",
            "limit":     max_articles,
            "sort":      "published_desc",
        })

    def fetch_by_keywords(self, keywords: str, max_articles=5) -> list:
        """
        Flexible keyword search — pass any comma-separated terms.

        Example:
            api.fetch_by_keywords("climate change,renewable energy")
        """
        return self._fetch({
            "keywords":  keywords,
            "languages": "en",
            "limit":     max_articles,
            "sort":      "published_desc",
        })


# ---------------------------------------------------------------------------
# Smoke-test — run directly to verify your Mediastack key works
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    api = MediastackAPI()

    print("--- Technology headlines ---")
    for i, a in enumerate(api.fetch_top_headlines(category="technology", max_articles=3), 1):
        print(f"{i}. {a['title']}")
        print(f"   Source: {a['source']} | {a['published_at']}")
        print(f"   URL:    {a['url']}\n")

    print("--- AI keyword search ---")
    for i, a in enumerate(api.fetch_ai_news(max_articles=3), 1):
        print(f"{i}. {a['title']}")
        print(f"   Source: {a['source']} | {a['published_at']}")
        print(f"   URL:    {a['url']}\n")
