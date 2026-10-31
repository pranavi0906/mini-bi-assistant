import json
import os
import logging

from dotenv import load_dotenv
from google import genai


load_dotenv()

logger = logging.getLogger(__name__)

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY was not found in .env")

client = genai.Client(api_key=API_KEY)


SUPPORTED_INTENTS = {
    "total_revenue",
    "highest_revenue_product",
    "monthly_revenue",
    "highest_revenue_region",
    "monthly_comparison",
    "total_units_sold",
    "revenue_by_category",
    "revenue_by_sales_channel",
    "unknown",
    "list_products",
}


def interpret_with_gemini(question: str) -> dict:
    """
    Use Gemini to identify the analytics intent and required parameters.
    Gemini does not calculate analytics or generate SQL.
    """

    prompt = f"""
You are an intent classifier for a sales analytics assistant.

The dataset contains sales transactions from January through June 2026.

Supported analytics intents:

1. total_revenue
   Questions about total revenue or total sales value.

2. highest_revenue_product
   Questions about the product with the highest revenue.

3. monthly_revenue
   Questions about monthly revenue trends or revenue over time.

4. highest_revenue_region
   Questions about the region with the highest revenue.

5. monthly_comparison
   Questions comparing revenue between two months.
   Extract exactly two months.

6. total_units_sold
   Questions about total quantity or number of units sold.

7. revenue_by_category
   Questions about revenue grouped by product category.

8. revenue_by_sales_channel
   Questions about revenue grouped by sales channel,
   such as online or retail.

9. unknown
   Questions unrelated to the supported analytics.

10. list_products
    Questions asking which products are available, sold, or included
    in the sales dataset. Examples:
    - What products are you selling?
    - What products do we sell?
    - List all products.
    - Which products are available?

Available months:
January 2026, February 2026, March 2026,
April 2026, May 2026, June 2026.

Rules:
- Return only valid JSON.
- Do not calculate revenue.
- Do not generate SQL.
- Do not invent analytics.
- For monthly_comparison, return exactly two months.
- Represent months using YYYY-MM.
- For other intents, return an empty months list.

Required JSON structure:
{{
    "intent": "one_supported_intent",
    "months": []
}}

User question:
{question}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
        },
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    result = json.loads(response.text)

    intent = result.get("intent")
    months = result.get("months", [])

    if intent not in SUPPORTED_INTENTS:
        raise ValueError(f"Unsupported intent returned by Gemini: {intent}")

    if not isinstance(months, list):
        raise ValueError("Gemini returned invalid month parameters.")

    # Validate that all months belong to our dataset.
    valid_months = {
        "2026-01",
        "2026-02",
        "2026-03",
        "2026-04",
        "2026-05",
        "2026-06",
    }

    if any(month not in valid_months for month in months):
        raise ValueError("Gemini returned a month outside the dataset.")

    if intent == "monthly_comparison":
        if len(months) != 2 or months[0] == months[1]:
            raise ValueError(
                "Monthly comparison requires two different months."
            )

    else:
        months = []

    return {
        "intent": intent,
        **({"months": months} if intent == "monthly_comparison" else {}),
    }