"""
config.py — Central configuration for the news summarizer.

Reads all settings from environment variables (loaded from .env via python-dotenv).
Call Config.validate() at startup to catch missing keys early.
"""
import os
from dotenv import load_dotenv

# Pull variables from .env into os.environ before anything else reads them
load_dotenv()


class Config:
    """Single source of truth for every tuneable setting."""

    # --- API keys (never hard-code these) ---
    OPENAI_API_KEY      = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY   = os.getenv("ANTHROPIC_API_KEY")
    NEWS_API_KEY        = os.getenv("NEWS_API_KEY")
    MEDIASTACK_API_KEY  = os.getenv("MEDIASTACK_API_KEY")  # optional second news source
    GEMINI_API_KEY      = os.getenv("GEMINI_API_KEY")      # optional third LLM provider

    # --- Runtime environment ---
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

    # --- Retry / timeout behaviour ---
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))  # seconds

    # --- Model identifiers ---
    OPENAI_MODEL    = "gpt-4o-mini"                     # cheap & fast for summarisation
    ANTHROPIC_MODEL = "claude-3-5-sonnet-20241022"      # better nuance for sentiment
    GEMINI_MODEL    = "gemini-2.0-flash-lite"           # lighter quota bucket than 2.0-flash

    # --- Cost guard ---
    DAILY_BUDGET = float(os.getenv("DAILY_BUDGET", "5.00"))  # USD

    # --- Rate limits (requests per minute, per provider docs) ---
    OPENAI_RPM       = 500
    ANTHROPIC_RPM    = 50
    NEWS_API_RPM     = 100
    MEDIASTACK_RPM   = 10   # free plan is 500 req/month — be conservative
    GEMINI_RPM       = 15   # free tier: 15 RPM on gemini-2.0-flash

    @classmethod
    def validate(cls):
        """Raise ValueError if any required key is missing; prints confirmation otherwise."""
        required = [
            ("OPENAI_API_KEY", cls.OPENAI_API_KEY),
            ("ANTHROPIC_API_KEY", cls.ANTHROPIC_API_KEY),
            # NEWS_API_KEY is optional — Mediastack can be used instead
        ]

        missing = [name for name, value in required if not value]

        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")

        print(f"[OK] Configuration validated for {cls.ENVIRONMENT} environment")


# Validate immediately so any module that imports Config fails fast
Config.validate()
