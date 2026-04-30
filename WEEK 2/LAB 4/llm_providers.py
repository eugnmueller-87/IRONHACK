"""
llm_providers.py — Unified interface to OpenAI and Anthropic with:
  • Per-provider rate limiting
  • Token counting & cost tracking
  • Automatic fallback when the primary provider fails
"""
import time
import tiktoken
from openai import OpenAI
from anthropic import Anthropic
from config import Config

# ---------------------------------------------------------------------------
# Pricing table (USD per million tokens, as of early 2026)
# Update these numbers if the providers change their pricing.
# ---------------------------------------------------------------------------
PRICING = {
    "gpt-4o-mini":               {"input": 0.15,  "output": 0.60},
    "gpt-4o":                    {"input": 2.50,  "output": 10.00},
    "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
}


# ---------------------------------------------------------------------------
# Cost tracker
# ---------------------------------------------------------------------------

class CostTracker:
    """Accumulate token usage and compute USD cost across all API calls."""

    def __init__(self):
        self.total_cost = 0.0
        self.requests = []  # list of per-request dicts for later inspection

    def track_request(self, provider: str, model: str, input_tokens: int, output_tokens: int) -> float:
        """
        Record one API call and return its cost in USD.

        Falls back to Claude Sonnet pricing when the model is not in the table.
        """
        pricing = PRICING.get(model, {"input": 3.0, "output": 15.0})
        cost = (
            (input_tokens  / 1_000_000) * pricing["input"] +
            (output_tokens / 1_000_000) * pricing["output"]
        )

        self.total_cost += cost
        self.requests.append({
            "provider":      provider,
            "model":         model,
            "input_tokens":  input_tokens,
            "output_tokens": output_tokens,
            "cost":          cost,
        })

        return cost

    def get_summary(self) -> dict:
        """Return aggregate stats suitable for reporting."""
        total_input  = sum(r["input_tokens"]  for r in self.requests)
        total_output = sum(r["output_tokens"] for r in self.requests)
        n = max(len(self.requests), 1)  # avoid division by zero

        return {
            "total_requests":      len(self.requests),
            "total_cost":          self.total_cost,
            "total_input_tokens":  total_input,
            "total_output_tokens": total_output,
            "average_cost":        self.total_cost / n,
        }

    def check_budget(self, daily_budget: float):
        """Raise if the running total exceeds the daily budget; warn at 90%."""
        if self.total_cost >= daily_budget:
            raise Exception(
                f"Daily budget of ${daily_budget:.2f} exceeded! "
                f"Current: ${self.total_cost:.2f}"
            )

        percent_used = (self.total_cost / daily_budget) * 100
        if percent_used >= 90:
            print(f"⚠️  Warning: {percent_used:.1f}% of daily budget used")


# ---------------------------------------------------------------------------
# Token counting helper
# ---------------------------------------------------------------------------

def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """
    Return the number of tokens in *text* for the given *model*.

    tiktoken only covers OpenAI models; for Anthropic we fall back to
    a simple character-based estimate (4 chars ≈ 1 token).
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception:
        return len(text) // 4


# ---------------------------------------------------------------------------
# Main provider class
# ---------------------------------------------------------------------------

class LLMProviders:
    """Wrap OpenAI and Anthropic clients with rate limiting and cost tracking."""

    def __init__(self):
        self.openai_client    = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.anthropic_client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.cost_tracker     = CostTracker()

        # Rate-limiting state per provider
        self.openai_last_call    = 0
        self.anthropic_last_call = 0
        self.openai_interval     = 60.0 / Config.OPENAI_RPM
        self.anthropic_interval  = 60.0 / Config.ANTHROPIC_RPM

    # ------------------------------------------------------------------
    # Rate-limiting helpers
    # ------------------------------------------------------------------

    def _wait_openai(self):
        """Sleep if we are sending OpenAI requests too fast."""
        elapsed = time.time() - self.openai_last_call
        if elapsed < self.openai_interval:
            time.sleep(self.openai_interval - elapsed)
        self.openai_last_call = time.time()

    def _wait_anthropic(self):
        """Sleep if we are sending Anthropic requests too fast."""
        elapsed = time.time() - self.anthropic_last_call
        if elapsed < self.anthropic_interval:
            time.sleep(self.anthropic_interval - elapsed)
        self.anthropic_last_call = time.time()

    # ------------------------------------------------------------------
    # Provider calls
    # ------------------------------------------------------------------

    def ask_openai(self, prompt: str, model: str = None) -> str:
        """Send *prompt* to OpenAI and return the text response."""
        if model is None:
            model = Config.OPENAI_MODEL

        self._wait_openai()

        input_tokens = count_tokens(prompt, model)

        response = self.openai_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )

        output_text   = response.choices[0].message.content
        output_tokens = count_tokens(output_text, model)

        # Record cost and abort if over budget
        self.cost_tracker.track_request("openai", model, input_tokens, output_tokens)
        self.cost_tracker.check_budget(Config.DAILY_BUDGET)

        return output_text

    def ask_anthropic(self, prompt: str, model: str = None) -> str:
        """Send *prompt* to Anthropic and return the text response."""
        if model is None:
            model = Config.ANTHROPIC_MODEL

        self._wait_anthropic()

        input_tokens = count_tokens(prompt, model)

        response = self.anthropic_client.messages.create(
            model=model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )

        output_text   = response.content[0].text
        output_tokens = count_tokens(output_text, model)

        self.cost_tracker.track_request("anthropic", model, input_tokens, output_tokens)
        self.cost_tracker.check_budget(Config.DAILY_BUDGET)

        return output_text

    def ask_with_fallback(self, prompt: str, primary: str = "openai") -> dict:
        """
        Try the primary provider; fall back to the other if it raises.

        Returns:
            {"provider": "<name>", "response": "<text>"}
        """
        providers = {
            "openai":    self.ask_openai,
            "anthropic": self.ask_anthropic,
        }
        secondary = "anthropic" if primary == "openai" else "openai"

        # --- Primary attempt ---
        try:
            print(f"Trying {primary} (primary)...")
            return {"provider": primary, "response": providers[primary](prompt)}

        except Exception as e:
            print(f"✗ Primary provider ({primary}) failed: {e}")

        # --- Fallback attempt ---
        try:
            print(f"Falling back to {secondary}...")
            return {"provider": secondary, "response": providers[secondary](prompt)}

        except Exception as e2:
            raise Exception(f"All providers failed. Last error: {e2}") from e2


# ---------------------------------------------------------------------------
# Quick smoke-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    providers = LLMProviders()

    print("Testing OpenAI:")
    print(providers.ask_openai("What is Python? One sentence."), "\n")

    print("Testing Anthropic:")
    print(providers.ask_anthropic("What is Python? One sentence."), "\n")

    print("Testing fallback:")
    result = providers.ask_with_fallback("What is machine learning? One sentence.")
    print(f"Provider used: {result['provider']}")
    print(f"Response:      {result['response']}\n")

    summary = providers.cost_tracker.get_summary()
    print(f"Total cost:     ${summary['total_cost']:.4f}")
    print(f"Total requests: {summary['total_requests']}")
