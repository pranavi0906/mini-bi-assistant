
"""Database creation, CSV import, and data-quality handling."""

import sqlite3
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# File paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

CSV_PATH = BASE_DIR / "data" / "ai_bi_assistant_sales_data - GET.csv"
DB_PATH = BASE_DIR / "data" / "sales.db"


# --------------------------------------------------
# Database connection
# --------------------------------------------------

def get_connection():
    """Return a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)


# --------------------------------------------------
# Create database tables
# --------------------------------------------------

def create_tables():
    """Create the sales and data-quality tables."""

    with get_connection() as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                transaction_id TEXT PRIMARY KEY,
                order_date TEXT,
                product TEXT,
                category TEXT,
                region TEXT,
                sales_channel TEXT,
                quantity INTEGER,
                unit_price REAL,
                discount_amount REAL,
                status TEXT,
                price_was_imputed INTEGER DEFAULT 0,
                is_valid_for_revenue INTEGER DEFAULT 1
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS quality_issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id TEXT,
                issue_type TEXT NOT NULL,
                description TEXT NOT NULL
            )
        """)


# --------------------------------------------------
# Data cleaning and validation
# --------------------------------------------------

def clean_data(df):
    """
    Clean the input DataFrame.

    Returns:
        cleaned_df: DataFrame ready for database storage
        issues: List of data-quality issues
    """

    df = df.copy()
    issues = []

    # Normalize column names.
    df.columns = [
        column.strip().lower()
        for column in df.columns
    ]

    # Convert dates to datetime.
    df["order_date"] = pd.to_datetime(
        df["order_date"],
        format="%d-%m-%Y",
        errors="coerce"
    )

    # Convert numeric columns safely.
    numeric_columns = [
        "quantity",
        "unit_price",
        "discount_amount",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # --------------------------------------------------
    # Handle missing unit prices
    # --------------------------------------------------

    df["price_was_imputed"] = 0

    # Find products whose known prices are consistent.
    product_prices = (
        df.groupby("product")["unit_price"]
        .agg(["min", "max"])
    )

    consistent_prices = product_prices[
        product_prices["min"].notnull()
        & (product_prices["min"] == product_prices["max"])
    ]["min"]

    # Identify missing prices before filling them.
    missing_price_mask = df["unit_price"].isnull()

    # Fill only when the product has a consistent known price.
    inferred_prices = df.loc[
        missing_price_mask, "product"
    ].map(consistent_prices)

    can_impute = inferred_prices.notnull()

    rows_to_impute = inferred_prices[can_impute].index

    df.loc[rows_to_impute, "unit_price"] = inferred_prices[
        can_impute
    ]

    df.loc[rows_to_impute, "price_was_imputed"] = 1

    # Report unresolved missing prices.
    unresolved_prices = df["unit_price"].isnull()

    for _, row in df[unresolved_prices].iterrows():
        issues.append({
            "transaction_id": row["transaction_id"],
            "issue_type": "missing_unit_price",
            "description": (
                f"Could not infer unit price for product "
                f"'{row['product']}' because its known prices "
                f"were not consistent or unavailable."
            ),
        })

    # --------------------------------------------------
    # Validate records for revenue calculations
    # --------------------------------------------------

    df["is_valid_for_revenue"] = 1

    # Required fields for revenue analytics.
    required_fields = [
        "transaction_id",
        "order_date",
        "product",
        "category",
        "region",
        "sales_channel",
        "quantity",
        "unit_price",
        "discount_amount",
        "status",
    ]

    for column in required_fields:
        invalid_mask = df[column].isnull()

        df.loc[
            invalid_mask, "is_valid_for_revenue"
        ] = 0

        for _, row in df[invalid_mask].iterrows():
            issues.append({
                "transaction_id": row["transaction_id"],
                "issue_type": f"missing_{column}",
                "description": (
                    f"Missing required value in '{column}'."
                ),
            })

    # Negative quantity or price is invalid for this dataset.
    negative_quantity = df["quantity"] < 0
    negative_price = df["unit_price"] < 0
    negative_discount = df["discount_amount"] < 0

    invalid_numeric = (
        negative_quantity
        | negative_price
        | negative_discount
    ).fillna(False)

    df.loc[
        invalid_numeric, "is_valid_for_revenue"
    ] = 0

    for _, row in df[invalid_numeric].iterrows():
        issues.append({
            "transaction_id": row["transaction_id"],
            "issue_type": "invalid_numeric_value",
            "description": (
                "Negative quantity, unit price, or discount found."
            ),
        })

    # Check for duplicate transaction IDs.
    duplicate_ids = df["transaction_id"].duplicated(
        keep=False
    )

    for _, row in df[duplicate_ids].iterrows():
        issues.append({
            "transaction_id": row["transaction_id"],
            "issue_type": "duplicate_transaction_id",
            "description": "Duplicate transaction ID found.",
        })

    # Convert dates to ISO format for SQLite storage.
    df["order_date"] = df["order_date"].dt.strftime(
        "%Y-%m-%d"
    )

    # Convert missing values to None for SQLite.
    df = df.astype(object).where(
        pd.notnull(df),
        None
    )

    return df, issues


# --------------------------------------------------
# Load CSV into SQLite
# --------------------------------------------------

def load_csv():
    """Read, clean, validate, and import the sales CSV."""

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"CSV file not found: {CSV_PATH}"
        )

    df = pd.read_csv(CSV_PATH)

    cleaned_df, issues = clean_data(df)

    # Convert records into dictionaries.
    records = cleaned_df.to_dict(
        orient="records"
    )

    with get_connection() as connection:

        # Clear previous imported data so rerunning the
        # import does not leave stale records.
        connection.execute("DELETE FROM sales")
        connection.execute("DELETE FROM quality_issues")

        # Insert cleaned records.
        connection.executemany("""
            INSERT INTO sales (
                transaction_id,
                order_date,
                product,
                category,
                region,
                sales_channel,
                quantity,
                unit_price,
                discount_amount,
                status,
                price_was_imputed,
                is_valid_for_revenue
            )
            VALUES (
                :transaction_id,
                :order_date,
                :product,
                :category,
                :region,
                :sales_channel,
                :quantity,
                :unit_price,
                :discount_amount,
                :status,
                :price_was_imputed,
                :is_valid_for_revenue
            )
        """, records)

        # Store data-quality issues for later reporting.
        connection.executemany("""
            INSERT INTO quality_issues (
                transaction_id,
                issue_type,
                description
            )
            VALUES (
                :transaction_id,
                :issue_type,
                :description
            )
        """, issues)

    print("CSV import completed.")
    print(f"Total source rows: {len(df)}")
    print(f"Rows loaded: {len(records)}")
    print(f"Prices imputed: {cleaned_df['price_was_imputed'].sum()}")
    print(f"Data-quality issues recorded: {len(issues)}")


# --------------------------------------------------
# Initialize database
# --------------------------------------------------

def initialize_database():
    """Create database tables and import the CSV."""

    create_tables()
    load_csv()


if __name__ == "__main__":
    initialize_database()
