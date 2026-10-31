
"""SQL-based business analytics for the sales dataset."""

from app.database import get_connection


# --------------------------------------------------
# Common revenue conditions
# --------------------------------------------------

REVENUE_CONDITIONS = """
    status = 'Completed'
    AND is_valid_for_revenue = 1
    AND unit_price IS NOT NULL
"""


def execute_query(query, params=()):
    """Execute a SQL query and return all rows."""

    with get_connection() as connection:
        connection.row_factory = lambda cursor, row: {
            column[0]: value
            for column, value in zip(cursor.description, row)
        }

        cursor = connection.execute(query, params)

        return cursor.fetchall()


# --------------------------------------------------
# 1. Total revenue
# --------------------------------------------------

def get_total_revenue():
    """Calculate total revenue from completed transactions."""

    query = f"""
        SELECT
            SUM(
                (quantity * unit_price) - discount_amount
            ) AS total_revenue,
            COUNT(*) AS transaction_count
        FROM sales
        WHERE {REVENUE_CONDITIONS}
    """

    rows = execute_query(query)

    result = rows[0]

    return {
        "metric": "total_revenue",
        "total_revenue": result["total_revenue"] or 0,
        "transaction_count": result["transaction_count"],
    }


# --------------------------------------------------
# 2. Highest revenue product
# --------------------------------------------------

def get_highest_revenue_product():
    """Find the product generating the highest revenue."""

    query = f"""
        SELECT
            product,
            SUM(
                (quantity * unit_price) - discount_amount
            ) AS revenue,
            SUM(quantity) AS units_sold
        FROM sales
        WHERE {REVENUE_CONDITIONS}
        GROUP BY product
        ORDER BY revenue DESC
        LIMIT 1
    """

    rows = execute_query(query)

    if not rows:
        return {
            "metric": "highest_revenue_product",
            "message": "No valid completed sales found.",
        }

    return {
        "metric": "highest_revenue_product",
        **rows[0],
    }


# --------------------------------------------------
# 3. Monthly revenue trend
# --------------------------------------------------

def get_monthly_revenue():
    """Calculate revenue grouped by month."""

    query = f"""
        SELECT
            strftime('%Y-%m', order_date) AS month,
            SUM(
                (quantity * unit_price) - discount_amount
            ) AS revenue,
            COUNT(*) AS transaction_count
        FROM sales
        WHERE {REVENUE_CONDITIONS}
        GROUP BY month
        ORDER BY month
    """

    rows = execute_query(query)

    return {
        "metric": "monthly_revenue",
        "data": rows,
    }


# --------------------------------------------------
# 4. Highest revenue region
# --------------------------------------------------

def get_highest_revenue_region():
    """Find the region generating the highest revenue."""

    query = f"""
        SELECT
            region,
            SUM(
                (quantity * unit_price) - discount_amount
            ) AS revenue,
            COUNT(*) AS transaction_count
        FROM sales
        WHERE {REVENUE_CONDITIONS}
        GROUP BY region
        ORDER BY revenue DESC
        LIMIT 1
    """

    rows = execute_query(query)

    if not rows:
        return {
            "metric": "highest_revenue_region",
            "message": "No valid completed sales found.",
        }

    return {
        "metric": "highest_revenue_region",
        **rows[0],
    }


# --------------------------------------------------
# 5. Revenue comparison between two months
# --------------------------------------------------

def compare_monthly_revenue(month_1, month_2):
    """
    Compare revenue between two months.

    The difference and percentage change are calculated
    from month_1 to month_2.

    Expected format:
        YYYY-MM
    """

    query = f"""
        SELECT
            strftime('%Y-%m', order_date) AS month,
            SUM(
                (quantity * unit_price) - discount_amount
            ) AS revenue
        FROM sales
        WHERE {REVENUE_CONDITIONS}
          AND strftime('%Y-%m', order_date) IN (?, ?)
        GROUP BY month
    """

    rows = execute_query(
        query,
        (month_1, month_2)
    )

    revenue_by_month = {
        row["month"]: row["revenue"] or 0
        for row in rows
    }

    revenue_1 = revenue_by_month.get(month_1, 0)
    revenue_2 = revenue_by_month.get(month_2, 0)

    difference = revenue_2 - revenue_1

    if revenue_1 == 0:
        percentage_change = None
    else:
        percentage_change = (
            difference / revenue_1
        ) * 100

    return {
        "metric": "monthly_revenue_comparison",
        "month_1": month_1,
        "revenue_1": revenue_1,
        "month_2": month_2,
        "revenue_2": revenue_2,
        "difference": difference,
        "percentage_change": percentage_change,
    }

# --------------------------------------------------
# Additional analytics
# --------------------------------------------------

def get_total_units_sold():
    """Calculate total units sold in completed transactions."""

    query = f"""
        SELECT
            SUM(quantity) AS total_units_sold
        FROM sales
        WHERE {REVENUE_CONDITIONS}
    """

    rows = execute_query(query)

    return {
        "metric": "total_units_sold",
        "total_units_sold": rows[0]["total_units_sold"] or 0,
    }


def get_revenue_by_category():
    """Calculate revenue grouped by product category."""

    query = f"""
        SELECT
            category,
            SUM(
                (quantity * unit_price) - discount_amount
            ) AS revenue
        FROM sales
        WHERE {REVENUE_CONDITIONS}
        GROUP BY category
        ORDER BY revenue DESC
    """

    return {
        "metric": "revenue_by_category",
        "data": execute_query(query),
    }


def get_revenue_by_sales_channel():
    """Calculate revenue grouped by sales channel."""

    query = f"""
        SELECT
            sales_channel,
            SUM(
                (quantity * unit_price) - discount_amount
            ) AS revenue
        FROM sales
        WHERE {REVENUE_CONDITIONS}
        GROUP BY sales_channel
        ORDER BY revenue DESC
    """

    return {
        "metric": "revenue_by_sales_channel",
        "data": execute_query(query),
    }

def get_products():
    """Return the distinct products available in the sales dataset."""

    query = """
        SELECT DISTINCT Product
        FROM sales
        WHERE Product IS NOT NULL
        ORDER BY Product
    """

    rows = execute_query(query)
    products = [row["product"] for row in rows]

    return {
        "metric": "list_products",
        "products": products,
        "count": len(products),
    }