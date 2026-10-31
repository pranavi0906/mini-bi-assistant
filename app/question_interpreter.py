
"""Interpret user questions and route them to analytics functions."""

import logging
import re

from app import analytics
from app.gemini_interpreter import interpret_with_gemini


logger = logging.getLogger(__name__)


# --------------------------------------------------
# Month handling
# --------------------------------------------------

MONTHS = {
    "january": "01",
    "jan": "01",
    "february": "02",
    "feb": "02",
    "march": "03",
    "mar": "03",
    "april": "04",
    "apr": "04",
    "may": "05",
    "june": "06",
    "jun": "06",
    "july": "07",
    "jul": "07",
    "august": "08",
    "aug": "08",
    "september": "09",
    "sep": "09",
    "sept": "09",
    "october": "10",
    "oct": "10",
    "november": "11",
    "nov": "11",
    "december": "12",
    "dec": "12",
}


def extract_months(question):
    """Extract month names and convert them to YYYY-MM."""

    question = question.lower()

    found_months = []

    for month_name, month_number in MONTHS.items():
        pattern = rf"\b{month_name}\b"

        for match in re.finditer(pattern, question):
            found_months.append(
                (match.start(), f"2026-{month_number}")
            )

    # Preserve the order in which months appear in the question.
    found_months.sort(key=lambda item: item[0])

    result = []

    for _, month in found_months:
        if month not in result:
            result.append(month)

    return result


# --------------------------------------------------
# Intent detection
# --------------------------------------------------
def detect_intent_rules(question):
    """Identify the analytics operation requested."""

    question = question.lower().strip()

    if not question:
        return {
            "intent": "unknown",
            "message": "Please enter a question.",
        }

    months = extract_months(question)

    # --------------------------------------------------
    # 1. Unsupported forecasting questions
    # --------------------------------------------------

    forecast_words = [
        "forecast",
        "predict",
        "prediction",
        "next year",
        "future sales",
        "future revenue",
        "sales next year",
        "revenue next year",
    ]

    if any(word in question for word in forecast_words):
        return {
            "intent": "unknown",
            "message": (
                "Sales forecasting is not currently supported. "
                "I can analyze historical sales data from January "
                "to June 2026."
            ),
            "requires_clarification": True,
        }

    # --------------------------------------------------
    # 2. Monthly comparison
    # --------------------------------------------------

    comparison_words = [
        "compare",
        "comparison",
        "difference",
        "change",
        "increase",
        "decrease",
        "versus",
        "vs",
        "outperform",
        "better than",
        "higher than",
        "lower than",
    ]

    has_comparison_word = any(
        word in question for word in comparison_words
    )

    if has_comparison_word:
        if len(months) >= 2:
            return {
                "intent": "monthly_comparison",
                "months": months[:2],
            }

        if (
            "two months" in question
            or "between months" in question
            or "between two months" in question
        ):
            return {
                "intent": "unknown",
                "message": (
                    "Please specify the two months you want to compare, "
                    "for example: 'How did revenue change between "
                    "January and February?'"
                ),
                "requires_clarification": True,
            }

    # --------------------------------------------------
    # 3. Monthly revenue trend
    # --------------------------------------------------

    monthly_phrases = [
        "monthly",
        "month-wise",
        "month wise",
        "each month",
        "every month",
        "per month",
        "by month",
        "month by month",
        "trend",
    ]

    if any(phrase in question for phrase in monthly_phrases):
        return {
            "intent": "monthly_revenue",
        }

    # --------------------------------------------------
    # 4. Highest-revenue product
    # --------------------------------------------------

    if (
        "product" in question
        and any(
            word in question
            for word in [
                "highest",
                "top",
                "best",
                "most",
                "maximum",
            ]
        )
    ):
        return {
            "intent": "highest_revenue_product",
        }

    # --------------------------------------------------
    # 5. Highest-revenue region
    # --------------------------------------------------

    if (
        "region" in question
        and any(
            word in question
            for word in [
                "highest",
                "top",
                "best",
                "most",
                "maximum",
            ]
        )
    ):
        return {
            "intent": "highest_revenue_region",
        }

    # --------------------------------------------------
    # 6. Revenue by category
    # --------------------------------------------------

    if "category" in question:
        return {
            "intent": "revenue_by_category",
        }

    # --------------------------------------------------
    # 7. Revenue by sales channel
    # --------------------------------------------------

    if (
        "channel" in question
        or "online" in question
        or "retail" in question
    ):
        return {
            "intent": "revenue_by_sales_channel",
        }

    # --------------------------------------------------
    # 8. Units sold
    # --------------------------------------------------

    if (
        "units sold" in question
        or "quantity sold" in question
        or "how many" in question
    ):
        return {
            "intent": "total_units_sold",
        }

    # --------------------------------------------------
    # 9. Total revenue
    # --------------------------------------------------

    total_revenue_phrases = [
        "total revenue",
        "overall revenue",
        "total sales",
        "overall sales",
        "how much money",
        "how much did we make",
        "total earnings",
    ]

    if any(phrase in question for phrase in total_revenue_phrases):
        return {
            "intent": "total_revenue",
        }

    # Generic revenue/sales questions should not automatically
    # become total revenue. Let Gemini interpret them.
    return {
        "intent": "unknown",
        "message": (
            "I couldn't identify the requested analytics. "
            "Please ask about revenue, products, regions, "
            "monthly trends, categories, sales channels, "
            "or units sold."
        ),
    }

# --------------------------------------------------
# Gemini fallback
# --------------------------------------------------

def detect_intent(question):
    """
    Try rule-based detection first.
    Use Gemini only when rules cannot identify the intent.
    """

    rule_result = detect_intent_rules(question)
    if (
        rule_result["intent"] != "unknown"
        or rule_result.get("requires_clarification", False)
    ):
        logger.info(
            "Rule-based interpreter detected intent: %s",
            rule_result["intent"],
        )

        return rule_result

    try:
        gemini_result = interpret_with_gemini(question)

        logger.info(
            "Gemini detected intent: %s",
            gemini_result.get("intent"),
        )

        return gemini_result

    except Exception as error:
        print("\n===== GEMINI INTERPRETATION ERROR =====")
        print("Error type:", type(error).__name__)
        print("Error message:", repr(error))
        import traceback
        traceback.print_exc()
        print("=======================================\n")

        return rule_result

# --------------------------------------------------
# Execute the detected intent
# --------------------------------------------------

def answer_question(question):
    """Interpret a question and execute its analytics operation."""

    detected = detect_intent(question)

    intent = detected.get("intent", "unknown")

    # Unsupported questions.
    if intent == "unknown":
        return {
            "metric": "unknown",
            "message": detected.get(
                "message",
                "I couldn't understand that question. "
                "Please ask about sales revenue, products, "
                "regions, monthly trends, categories, "
                "sales channels, or units sold.",
            ),
        }

    # Total revenue.
    if intent == "total_revenue":
        return analytics.get_total_revenue()

    # Highest-revenue product.
    if intent == "highest_revenue_product":
        return analytics.get_highest_revenue_product()

    # Monthly revenue trend.
    if intent == "monthly_revenue":
        return analytics.get_monthly_revenue()

    # Highest-revenue region.
    if intent == "highest_revenue_region":
        return analytics.get_highest_revenue_region()

    # Monthly comparison.
    if intent == "monthly_comparison":

        months = detected.get("months", [])

        if len(months) != 2:
            return {
                "metric": "unknown",
                "message": (
                    "Please specify two months to compare, "
                    "for example: Compare January and February."
                ),
            }

        # Sort chronologically so the earlier month is the baseline.
        month_1, month_2 = sorted(months[:2])

        return analytics.compare_monthly_revenue(
            month_1,
            month_2,
        )

    # Total units sold.
    if intent == "total_units_sold":
        return analytics.get_total_units_sold()

    # Revenue by category.
    if intent == "revenue_by_category":
        return analytics.get_revenue_by_category()

    # Revenue by sales channel.
    if intent == "revenue_by_sales_channel":
        return analytics.get_revenue_by_sales_channel()
    
    if intent == "list_products":
        return analytics.get_products()

    return {
        "metric": "unknown",
        "message": (
            "This analytics operation is not supported yet."
        ),
    }
    
