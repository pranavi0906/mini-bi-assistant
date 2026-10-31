
from app.analytics import (
    get_total_revenue,
    get_highest_revenue_product,
    get_monthly_revenue,
    get_highest_revenue_region,
    compare_monthly_revenue,
    get_total_units_sold,
    get_revenue_by_category,
    get_revenue_by_sales_channel,
)


def main():

    print("\n1. TOTAL REVENUE")
    print(get_total_revenue())

    print("\n2. HIGHEST REVENUE PRODUCT")
    print(get_highest_revenue_product())

    print("\n3. MONTHLY REVENUE")
    print(get_monthly_revenue())

    print("\n4. HIGHEST REVENUE REGION")
    print(get_highest_revenue_region())

    print("\n5. JANUARY VS FEBRUARY")
    print(
        compare_monthly_revenue(
            "2026-01",
            "2026-02"
        )
    )

    print("\n6. TOTAL UNITS SOLD")
    print(get_total_units_sold())

    print("\n7. REVENUE BY CATEGORY")
    print(get_revenue_by_category())

    print("\n8. REVENUE BY SALES CHANNEL")
    print(get_revenue_by_sales_channel())


if __name__ == "__main__":
    main()
