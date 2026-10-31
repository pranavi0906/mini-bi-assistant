
"""Tests for the business analytics functions."""

from app import analytics


def test_total_revenue():
    result = analytics.get_total_revenue()

    assert result["metric"] == "total_revenue"
    assert result["total_revenue"] == 1445200.0
    assert result["transaction_count"] == 50


def test_highest_revenue_product():
    result = analytics.get_highest_revenue_product()

    assert result["metric"] == "highest_revenue_product"
    assert result["product"] == "Monitor"
    assert result["revenue"] == 473000.0
    assert result["units_sold"] == 50


def test_monthly_revenue():
    result = analytics.get_monthly_revenue()

    assert result["metric"] == "monthly_revenue"

    monthly_data = {
        row["month"]: row["revenue"]
        for row in result["data"]
    }

    assert monthly_data["2026-01"] == 210250.0
    assert monthly_data["2026-02"] == 234600.0
    assert monthly_data["2026-05"] == 318500.0


def test_highest_revenue_region():
    result = analytics.get_highest_revenue_region()

    assert result["metric"] == "highest_revenue_region"
    assert result["region"] == "South"
    assert result["revenue"] == 411200.0


def test_monthly_comparison():
    result = analytics.compare_monthly_revenue(
        "2026-01",
        "2026-02",
    )

    assert result["metric"] == "monthly_revenue_comparison"
    assert result["revenue_1"] == 210250.0
    assert result["revenue_2"] == 234600.0
    assert result["difference"] == 24350.0
    assert round(result["percentage_change"], 2) == 11.58


def test_total_units_sold():
    result = analytics.get_total_units_sold()

    assert result["metric"] == "total_units_sold"
    assert result["total_units_sold"] == 638


def test_revenue_by_category():
    result = analytics.get_revenue_by_category()

    assert result["metric"] == "revenue_by_category"

    category_revenue = {
        row["category"]: row["revenue"]
        for row in result["data"]
    }

    assert category_revenue["Accessories"] == 539100.0
    assert category_revenue["Electronics"] == 473000.0
    assert category_revenue["Furniture"] == 433100.0


def test_revenue_by_sales_channel():
    result = analytics.get_revenue_by_sales_channel()

    assert result["metric"] == "revenue_by_sales_channel"

    channel_revenue = {
        row["sales_channel"]: row["revenue"]
        for row in result["data"]
    }

    assert channel_revenue["Online"] == 752750.0
    assert channel_revenue["Retail"] == 692450.0
