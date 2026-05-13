"""
summarizer.py — Orchestrates the two-step pipeline:
  1. OpenAI  → summarise the raw article text
  2. Anthropic → sentiment-analyse the summary

Also contains AsyncNewsSummarizer, an optional subclass that processes
articles concurrently using asyncio (see Part 5 of the lab spec).
"""
import asyncio
from news_api import NewsAPI
from mediastack_api import MediastackAPI
from llm_providers import LLMProviders
from config import Config


class NewsSummarizer:
    """Process news articles through a two-provider LLM pipeline."""

    def __init__(self):
        # Use Mediastack if its key is set, otherwise fall back to NewsAPI
        if Config.MEDIASTACK_API_KEY:
            self.news_api = MediastackAPI()
        else:
            self.news_api = NewsAPI()
        self.llm_providers = LLMProviders()

    # ------------------------------------------------------------------
    # Single-article pipeline
    # ------------------------------------------------------------------

    def summarize_article(self, article: dict) -> dict:
        """
        Run one article through summarisation → sentiment analysis.

        Args:
            article: Normalised article dict from NewsAPI.fetch_top_headlines().

        Returns:
            Dict with keys: title, source, url, summary, sentiment, published_at.
        """
        print(f"\nProcessing: {article['title'][:60]}...")

        # Build a compact text block to keep token usage low
        article_text = (
            f"Title: {article['title']}\n"
            f"Description: {article['description']}\n"
            f"Content: {article['content'][:500]}"  # truncate long content
        )

        # --- Step 1: Summarise with OpenAI (cheap, fast) ---
        summary_prompt = f"Summarize this news article in 2-3 sentences:\n\n{article_text}"
        try:
            print("  → Summarising with OpenAI...")
            summary = self.llm_providers.ask_openai(summary_prompt)
            print("  [OK] Summary generated")
        except Exception as e:
            # If OpenAI is down or over quota, fall back to Anthropic
            print(f"  [ERR] OpenAI summarisation failed: {e}")
            print("  → Falling back to Anthropic for summary...")
            summary = self.llm_providers.ask_anthropic(summary_prompt)

        # --- Step 2: Sentiment analysis with Anthropic (better at nuance) ---
        sentiment_prompt = (
            f'Analyse the sentiment of this text: "{summary}"\n\n'
            "Provide:\n"
            "- Overall sentiment (positive/negative/neutral)\n"
            "- Confidence (0-100%)\n"
            "- Key emotional tone\n\n"
            "Be concise (2-3 sentences)."
        )
        try:
            print("  → Analysing sentiment with Anthropic...")
            sentiment = self.llm_providers.ask_anthropic(sentiment_prompt)
            print("  [OK] Sentiment analysed")
        except Exception as e:
            print(f"  [ERR] Anthropic sentiment analysis failed: {e}")
            sentiment = "Unable to analyse sentiment"

        return {
            "title":        article["title"],
            "source":       article["source"],
            "url":          article["url"],
            "summary":      summary,
            "sentiment":    sentiment,
            "published_at": article["published_at"],
        }

    # ------------------------------------------------------------------
    # Batch processing
    # ------------------------------------------------------------------

    def process_articles(self, articles: list) -> list:
        """
        Run summarize_article() on every article; skip any that raise.

        Returns a list of result dicts (failed articles are omitted).
        """
        results = []
        for article in articles:
            try:
                results.append(self.summarize_article(article))
            except Exception as e:
                print(f"[ERR] Failed to process article: {e}")
        return results

    # ------------------------------------------------------------------
    # Report generation
    # ------------------------------------------------------------------

    def generate_report(self, results: list):
        """Print a formatted report to stdout, including cost summary."""
        print("\n" + "=" * 80)
        print("NEWS SUMMARY REPORT")
        print("=" * 80)

        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['title']}")
            print(f"   Source: {result['source']} | Published: {result['published_at']}")
            print(f"   URL: {result['url']}")
            print(f"\n   SUMMARY:\n   {result['summary']}")
            print(f"\n   SENTIMENT:\n   {result['sentiment']}")
            print(f"\n   {'-' * 76}")

        # Cost breakdown at the end so operators can gauge spend
        summary = self.llm_providers.cost_tracker.get_summary()
        print("\n" + "=" * 80)
        print("COST SUMMARY")
        print("=" * 80)
        print(f"Total requests:           {summary['total_requests']}")
        print(f"Total cost:               ${summary['total_cost']:.4f}")
        print(f"Total tokens:             {summary['total_input_tokens'] + summary['total_output_tokens']:,}")
        print(f"  Input:                  {summary['total_input_tokens']:,}")
        print(f"  Output:                 {summary['total_output_tokens']:,}")
        print(f"Average cost per request: ${summary['average_cost']:.6f}")
        print("=" * 80)


# ---------------------------------------------------------------------------
# Optional advanced: async concurrent processing
# ---------------------------------------------------------------------------

class AsyncNewsSummarizer(NewsSummarizer):
    """
    Subclass that processes multiple articles concurrently with asyncio.

    The LLM SDK calls themselves are synchronous, so we offload each article
    to a thread via asyncio.to_thread() and cap concurrency with a Semaphore.
    """

    async def summarize_article_async(self, article: dict) -> dict:
        """Async wrapper — runs the blocking summarize_article() in a thread."""
        return await asyncio.to_thread(self.summarize_article, article)

    async def process_articles_async(self, articles: list, max_concurrent: int = 3) -> list:
        """
        Process all articles concurrently, at most *max_concurrent* at a time.

        Returns a list of result dicts; exceptions from individual articles
        are filtered out rather than propagated.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_with_semaphore(article):
            async with semaphore:
                return await self.summarize_article_async(article)

        tasks   = [process_with_semaphore(a) for a in articles]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Drop articles that raised during processing
        return [r for r in results if not isinstance(r, Exception)]


# ---------------------------------------------------------------------------
# Smoke-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    summarizer = NewsSummarizer()

    print("Fetching news articles...")
    articles = summarizer.news_api.fetch_top_headlines(category="technology", max_articles=2)

    if not articles:
        print("No articles fetched. Check your News API key.")
    else:
        print(f"\nProcessing {len(articles)} articles...")
        results = summarizer.process_articles(articles)
        summarizer.generate_report(results)
