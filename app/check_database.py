from app.database import get_connection


def check_database():
    with get_connection() as connection:

        # Check total records.
        total = connection.execute(
            "SELECT COUNT(*) FROM sales"
        ).fetchone()[0]

        print("Total records:", total)

        # Check the Laptop Stand transaction.
        laptop_stand = connection.execute("""
            SELECT
                transaction_id,
                product,
                quantity,
                unit_price,
                discount_amount,
                price_was_imputed
            FROM sales
            WHERE transaction_id = 'TXN0051'
        """).fetchone()

        print("\nTXN0051:")
        print(laptop_stand)

        # Check all imputed prices.
        imputed = connection.execute("""
            SELECT
                transaction_id,
                product,
                unit_price
            FROM sales
            WHERE price_was_imputed = 1
        """).fetchall()

        print("\nImputed prices:")
        print(imputed)


if __name__ == "__main__":
    check_database()