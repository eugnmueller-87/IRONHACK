"""
main.py — Interactive entry point for the News Summariser.

Usage:
    python main.py

The user is prompted for a category, article count, and whether to use
async (concurrent) processing. Results are printed to stdout.
"""
import sys
import asyncio
from summarizer import NewsSummarizer, AsyncNewsSummarizer


def get_user_inputs():
    """Collect and validate inputs from stdin; return (category, n_articles, use_async)."""
    category = (
        input("\nEnter news category (technology/business/health/general): ").strip()
        or "technology"
    )

    raw_n = input("How many articles to process? (1-10): ").strip()
    try:
        n_articles = max(1, min(10, int(raw_n)))  # clamp to [1, 10]
    except ValueError:
        n_articles = 3

    use_async = input("Use async (concurrent) processing? (y/n): ").strip().lower() == "y"

    return category, n_articles, use_async


def run_sync(category: str, n_articles: int):
    """Fetch and process articles synchronously, one at a time."""
    summarizer = NewsSummarizer()
    articles   = summarizer.news_api.fetch_top_headlines(
        category=category, max_articles=n_articles
    )
    if not articles:
        print("No articles fetched. Check your News API key.")
        return

    print(f"\nProcessing {len(articles)} articles sequentially...")
    results = summarizer.process_articles(articles)
    summarizer.generate_report(results)


async def run_async(category: str, n_articles: int):
    """Fetch and process articles concurrently using asyncio."""
    summarizer = AsyncNewsSummarizer()
    articles   = summarizer.news_api.fetch_top_headlines(
        category=category, max_articles=n_articles
    )
    if not articles:
        print("No articles fetched. Check your News API key.")
        return

    print(f"\nProcessing {len(articles)} articles concurrently (max 3 at once)...")
    results = await summarizer.process_articles_async(articles, max_concurrent=3)
    summarizer.generate_report(results)


def main():
    print("=" * 80)
    print("NEWS SUMMARISER — Multi-Provider Edition")
    print("=" * 80)

    try:
        category, n_articles, use_async = get_user_inputs()
        print(f"\nFetching {n_articles} articles from category: {category}")

        if use_async:
            asyncio.run(run_async(category, n_articles))
        else:
            run_sync(category, n_articles)

        print("\n[OK] Processing complete!")

    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(0)

    except Exception as e:
        print(f"\n[ERR] Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
