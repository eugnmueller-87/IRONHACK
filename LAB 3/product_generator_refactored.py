"""
Product Description Generator - Refactored Version (Path 2)
Demonstrates: helper functions, modular design, comprehensive error handling,
API wrapper with retry logic, and logging.
"""

import json
import os
import logging
import time
from datetime import datetime
from typing import List, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, field_validator, ValidationError
from openai import OpenAI, APIError

load_dotenv()


# ==============================================================================
# LOGGING SETUP
# ==============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            f'product_generator_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


# ==============================================================================
# PYDANTIC MODEL
# ==============================================================================

class Product(BaseModel):
    id: str
    name: str
    category: str
    price: float
    features: List[str] = []

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Price must be positive")
        return v


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def load_json_file(file_path: str) -> dict:
    """Load and parse a JSON file. Shows WHERE the error occurs on failure."""
    logger.info(f"Loading JSON from '{file_path}'")
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        logger.info(f"Successfully loaded '{file_path}'")
        return data
    except FileNotFoundError:
        error_msg = (
            f"ERROR in load_json_file(): FileNotFoundError\n"
            f"  Location: File '{file_path}' not found\n"
            f"  Current directory: {os.getcwd()}\n"
            f"  Suggestion: Check that the file path is correct and the file exists"
        )
        logger.error(error_msg)
        print(error_msg)
        raise
    except json.JSONDecodeError as e:
        error_msg = (
            f"ERROR in load_json_file(): JSONDecodeError\n"
            f"  Location: File '{file_path}', line {e.lineno}, column {e.colno}\n"
            f"  Message: {e.msg}\n"
            f"  Suggestion: Check JSON syntax at line {e.lineno}"
        )
        logger.error(error_msg)
        print(error_msg)
        raise


def validate_product_data(product_dict: dict) -> Optional[Product]:
    """Validate a product dict with Pydantic. Returns None if invalid (never silent)."""
    try:
        product = Product(**product_dict)
        logger.debug(f"Validated product ID '{product.id}'")
        return product
    except ValidationError as e:
        error_msg = (
            f"ERROR in validate_product_data(): ValidationError\n"
            f"  Product ID: {product_dict.get('id', 'unknown')}\n"
            f"  Invalid fields:\n"
        )
        for error in e.errors():
            error_msg += f"    - {error['loc']}: {error['msg']}\n"
        error_msg += "  Suggestion: Fix the invalid fields listed above"
        logger.warning(error_msg)
        print(error_msg)
        return None


def create_product_prompt(product: Product) -> str:
    """Build the OpenAI prompt string for a product."""
    return (
        f"Create a compelling e-commerce product description for:\n"
        f"Name: {product.name}\n"
        f"Category: {product.category}\n"
        f"Price: ${product.price:.2f}\n"
        f"Features: {', '.join(product.features)}\n\n"
        f"Write 2-3 sentences that highlight the key benefits and appeal to customers."
    )


def parse_api_response(response) -> str:
    """Extract the text content from an OpenAI chat completion response."""
    try:
        return response.choices[0].message.content
    except (AttributeError, IndexError) as e:
        error_msg = (
            f"ERROR in parse_api_response(): {type(e).__name__}\n"
            f"  Message: {str(e)}\n"
            f"  Suggestion: The API response format may have changed — check OpenAI docs"
        )
        logger.error(error_msg)
        print(error_msg)
        raise


def format_output(product: Product, description: str) -> dict:
    """Format a product and its description into a result dict."""
    return {
        "product_id": product.id,
        "name": product.name,
        "category": product.category,
        "price": product.price,
        "description": description,
    }


# ==============================================================================
# MODULAR FUNCTIONS (each has a single responsibility)
# ==============================================================================

def load_and_validate_products(json_path: str) -> List[Product]:
    """Load JSON file and return only the valid products."""
    data = load_json_file(json_path)

    raw_products = data.get("products", [])
    if not raw_products:
        logger.warning(f"No 'products' key found in '{json_path}'")

    valid_products = []
    for item in raw_products:
        product = validate_product_data(item)
        if product is not None:
            valid_products.append(product)

    logger.info(
        f"Loaded {len(valid_products)}/{len(raw_products)} valid products from '{json_path}'"
    )
    return valid_products


def generate_description(product: Product, api_client: OpenAI) -> str:
    """Call the OpenAI API to generate a description for one product."""
    logger.info(f"Generating description for '{product.name}' (ID: {product.id})")
    prompt = create_product_prompt(product)
    try:
        response = api_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        description = parse_api_response(response)
        logger.info(f"Description generated for '{product.name}'")
        return description
    except APIError as e:
        error_msg = (
            f"ERROR in generate_description(): APIError\n"
            f"  Product: {product.name} (ID: {product.id})\n"
            f"  Error type: {type(e).__name__}\n"
            f"  Status code: {getattr(e, 'status_code', 'N/A')}\n"
            f"  Message: {str(e)}\n"
            f"  Suggestion: Check your API key, rate limits, or try again later"
        )
        logger.error(error_msg)
        print(error_msg)
        raise
    except Exception as e:
        error_msg = (
            f"ERROR in generate_description(): {type(e).__name__}\n"
            f"  Product: {product.name} (ID: {product.id})\n"
            f"  Message: {str(e)}\n"
            f"  Suggestion: Check your network connection"
        )
        logger.error(error_msg)
        print(error_msg)
        raise


def process_products(products: List[Product], api_client: OpenAI) -> List[dict]:
    """Orchestrate description generation for all products."""
    results = []
    for i, product in enumerate(products, 1):
        logger.info(f"Processing product {i}/{len(products)}: {product.name}")
        try:
            description = generate_description(product, api_client)
            result = format_output(product, description)
            results.append(result)
        except Exception as e:
            logger.error(
                f"Skipping '{product.name}' due to error: {type(e).__name__}: {e}"
            )
            print(f"  Skipped '{product.name}' — see error above.\n")
    return results


def save_results(results: List[dict], output_path: str) -> None:
    """Save results list to a JSON file."""
    logger.info(f"Saving {len(results)} results to '{output_path}'")
    try:
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results saved to '{output_path}'")
        print(f"\nResults saved to '{output_path}'")
    except OSError as e:
        error_msg = (
            f"ERROR in save_results(): OSError\n"
            f"  Location: Could not write to '{output_path}'\n"
            f"  Message: {str(e)}\n"
            f"  Suggestion: Check write permissions and that the directory exists"
        )
        logger.error(error_msg)
        print(error_msg)
        raise


# ==============================================================================
# OPTIONAL ADVANCED: API WRAPPER WITH RETRY LOGIC
# ==============================================================================

class OpenAIWrapper:
    """OpenAI API wrapper with retry logic and exponential backoff."""

    def __init__(self, api_key: str, max_retries: int = 3, timeout: int = 30):
        self.client = OpenAI(api_key=api_key, timeout=timeout)
        self.max_retries = max_retries

    def generate_description(self, prompt: str, model: str = "gpt-4o-mini") -> str:
        """Generate text with automatic retry on transient errors."""
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                )
                return parse_api_response(response)
            except APIError as e:
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt  # exponential backoff: 2s, 4s, 8s
                    logger.warning(
                        f"API error on attempt {attempt}/{self.max_retries}, "
                        f"retrying in {wait_time}s: {e}"
                    )
                    print(f"  API error, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All {self.max_retries} attempts failed.")
                    raise


# ==============================================================================
# MAIN
# ==============================================================================

def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print(
            "ERROR in main(): Missing API key\n"
            "  Suggestion: Set the OPENAI_API_KEY environment variable\n"
            "  Example:  export OPENAI_API_KEY='sk-...'"
        )
        return

    json_path = "products.json"
    output_path = "results.json"

    api_client = OpenAI(api_key=api_key)

    products = load_and_validate_products(json_path)
    if not products:
        print("No valid products to process. Exiting.")
        return

    results = process_products(products, api_client)

    if results:
        save_results(results, output_path)
        print(f"\nDone! Generated descriptions for {len(results)} product(s).")
    else:
        print("No descriptions were generated.")


if __name__ == "__main__":
    main()
