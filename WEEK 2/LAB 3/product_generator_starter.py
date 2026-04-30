"""
Product Description Generator - STARTER CODE (Needs Refactoring)
This code works but has many issues that need to be fixed.

Issues to identify:
1. Silent failures (except: pass)
2. Monolithic function doing too much
3. No error messages showing WHERE errors occur
4. Hardcoded API key
5. No modular separation of concerns
"""

import json
import os
from openai import OpenAI
from pydantic import BaseModel, field_validator
from typing import List, Optional


class Product(BaseModel):
    id: str
    name: str
    category: str
    price: float
    features: List[str] = []

    @field_validator('price')
    @classmethod
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v


def generate_product_descriptions(json_file):
    # Load JSON file
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Validate products
    products = []
    for item in data.get('products', []):
        try:
            product = Product(**item)
            products.append(product)
        except:
            pass  # Silent failure!

    # Generate descriptions
    client = OpenAI(api_key="your-api-key-here")
    results = []

    for product in products:
        # Create prompt
        prompt = f"""Create a product description for:
Name: {product.name}
Category: {product.category}
Price: ${product.price}
Features: {', '.join(product.features)}

Generate a compelling product description."""

        # Call API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        # Process response
        description = response.choices[0].message.content
        results.append({
            "product_id": product.id,
            "name": product.name,
            "description": description
        })

    # Save results
    with open('results.json', 'w') as f:
        json.dump(results, f, indent=2)

    return results


# Usage
if __name__ == "__main__":
    generate_product_descriptions("products.json")
